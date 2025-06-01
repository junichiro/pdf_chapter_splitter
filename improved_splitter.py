#!/usr/bin/env python3
"""
改良された章検出パターンの提案
ページヘッダーと真の章の開始を区別する
"""

import re
from pathlib import Path
from src.pdf_chapter_splitter.splitter import PDFChapterSplitter

class ImprovedPDFChapterSplitter(PDFChapterSplitter):
    
    def find_chapter_boundaries(self, text: str) -> list:
        """改良された章の境界検出"""
        lines = text.split('\n')
        chapter_boundaries = []
        
        # より厳格な章検出パターン
        # 1. 章番号 + タイトルが含まれるもののみ（最低10文字以上）
        # 2. ページ番号や短い文字列を除外
        strict_patterns = [
            # 第X章　タイトル形式（フルタイトル必須）
            r'^第?\s*([0-9一二三四五六七八九十]+)\s*章\s*[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\w\s]{8,}',
            # Chapter X: Title形式
            r'^Chapter\s+([0-9IVX]+)[\s:]\s*[A-Z][A-Za-z\s]{8,}',
            # X. Title形式（タイトルが8文字以上）
            r'^([0-9]+)\.\s*[A-Z][A-Za-z\s]{8,}$',
        ]
        
        # 除外パターン（ページヘッダー、目次、フッターなど）
        exclusion_patterns = [
            r'^\s*[0-9]+\s*$',  # 数字のみ
            r'page\s*[0-9]+',   # ページ番号
            r'^\s*第?\s*[0-9一二三四五六七八九十]+\s*章\s*$',  # 章番号のみ
            r'^\s*[0-9]+\s*章\s*$',  # 「1章」のような短い形式
            r'ʜʜʜʜ',  # 罫線文字
            r'^\s*[0-9]+\s*[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]{1,10}\s*[0-9]+\s*$',  # 目次形式
        ]
        
        print("\n=== 改良された章検出を実行中 ===")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 10:  # 短すぎる行はスキップ
                continue
            
            # 除外パターンのチェック
            should_exclude = False
            for exclusion_pattern in exclusion_patterns:
                if re.search(exclusion_pattern, line, re.IGNORECASE):
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
            
            # 章パターンのチェック
            for pattern in strict_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # 前後の文脈をチェック（追加の検証）
                    if self._is_likely_chapter_start(lines, i, line):
                        chapter_boundaries.append((i, line))
                        print(f"章検出: 行{i} - {line}")
                        break
        
        return chapter_boundaries
    
    def _is_likely_chapter_start(self, lines: list, line_index: int, line: str) -> bool:
        """章の開始らしいかどうかの追加検証"""
        
        # 1. ページの上部にある（前の行が空行やページ区切りらしい）
        preceding_empty_lines = 0
        for i in range(max(0, line_index - 5), line_index):
            if not lines[i].strip():
                preceding_empty_lines += 1
        
        # 2. 次の行が空行または本文らしい（章タイトルの後は通常空行）
        has_following_content = False
        if line_index + 1 < len(lines):
            next_line = lines[line_index + 1].strip()
            # 次の行が空行、または本文の開始らしい
            if not next_line or (len(next_line) > 20 and not re.match(r'^[0-9]+', next_line)):
                has_following_content = True
        
        # 3. 短すぎる行（ページヘッダーの可能性）を除外
        if len(line) < 15:
            return False
        
        # 4. ページ番号らしきものが含まれている場合は除外
        if re.search(r'\s+[0-9]+\s*$', line):
            return False
        
        # 判定：前に空行があり、適切な長さがあるものを真の章とする
        return preceding_empty_lines >= 1 and has_following_content

def test_improved_detection():
    """改良された検出の試行"""
    pdf_path = "/home/junichiro/src/github.com/junichiro/pdf_chapter_splitter/pdfs/llm-prompt-engineering.pdf"
    
    print("=== 現在の検出方法 ===")
    original_splitter = PDFChapterSplitter(pdf_path)
    text = original_splitter.extract_text()
    original_boundaries = original_splitter.find_chapter_boundaries(text)
    print(f"検出された章数: {len(original_boundaries)}")
    
    print("\n=== 改良された検出方法 ===")
    improved_splitter = ImprovedPDFChapterSplitter(pdf_path)
    improved_boundaries = improved_splitter.find_chapter_boundaries(text)
    print(f"検出された章数: {len(improved_boundaries)}")
    
    print("\n=== 改良された検出結果 ===")
    for i, (line_num, title) in enumerate(improved_boundaries):
        print(f"{i+1:2d}. 行{line_num:4d}: {title}")

if __name__ == "__main__":
    test_improved_detection()
