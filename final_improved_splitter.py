#!/usr/bin/env python3
"""
最終版の改良された章検出パターン
真の章開始のみを検出する
"""

import re
from pathlib import Path
from src.pdf_chapter_splitter.splitter import PDFChapterSplitter

class FinalImprovedPDFChapterSplitter(PDFChapterSplitter):
    
    def find_chapter_boundaries(self, text: str) -> list:
        """最終改良版の章の境界検出"""
        lines = text.split('\n')
        chapter_boundaries = []
        
        print("\n=== 最終改良版章検出を実行中 ===")
        
        # まず目次部分の章を探す（これが真の章リスト）
        toc_chapters = self._find_toc_chapters(lines)
        print(f"目次で見つかった章: {len(toc_chapters)} 個")
        
        # 目次で見つかった章番号とタイトルをもとに、本文の章開始位置を探す
        chapter_info = {}
        for chapter_num, title in toc_chapters:
            chapter_info[chapter_num] = title.strip()
        
        # 本文で真の章開始を探す
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 15:
                continue
            
            # 章番号を抽出
            chapter_match = re.match(r'^第?\s*([0-9一二三四五六七八九十]+)\s*章\s*(.*)', line)
            if not chapter_match:
                continue
            
            chapter_num_str = chapter_match.group(1)
            chapter_title = chapter_match.group(2).strip()
            
            # 数字に変換
            chapter_num = self._convert_to_number(chapter_num_str)
            if chapter_num is None:
                continue
            
            # 目次にある章番号かチェック
            if chapter_num not in chapter_info:
                continue
            
            # ページヘッダーかどうかを判定
            if self._is_page_header(lines, i, line):
                continue
            
            # タイトルが目次のものと類似しているかチェック
            expected_title = chapter_info[chapter_num]
            if self._titles_match(chapter_title, expected_title):
                chapter_boundaries.append((i, line))
                print(f"真の章検出: 行{i} - {line}")
        
        return chapter_boundaries
    
    def _find_toc_chapters(self, lines: list) -> list:
        """目次から章リストを抽出"""
        toc_chapters = []
        
        # 目次らしい部分を探す（最初の300行程度）
        for i, line in enumerate(lines[:300]):
            line = line.strip()
            # 「X章　タイトル」形式を探す
            match = re.match(r'^([0-9]+)章\s*(.+?)\s*[ʜ…\.]*\s*([0-9]+)\s*$', line)
            if match:
                chapter_num = int(match.group(1))
                title = match.group(2).strip()
                if len(title) > 5:  # タイトルが十分長い
                    toc_chapters.append((chapter_num, title))
        
        return sorted(toc_chapters, key=lambda x: x[0])
    
    def _convert_to_number(self, num_str: str) -> int:
        """章番号を数字に変換"""
        # 数字の場合
        if num_str.isdigit():
            return int(num_str)
        
        # 漢数字の場合
        kanji_nums = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12
        }
        return kanji_nums.get(num_str)
    
    def _is_page_header(self, lines: list, line_index: int, line: str) -> bool:
        """ページヘッダーかどうかを判定"""
        
        # 行の位置をチェック（ページの最初や最後近くはヘッダー/フッターの可能性）
        # 前後に多くの空行がある場合はページ区切りの可能性
        empty_before = 0
        empty_after = 0
        
        # 前の空行をカウント
        for i in range(max(0, line_index - 10), line_index):
            if not lines[i].strip():
                empty_before += 1
        
        # 後の空行をカウント  
        for i in range(line_index + 1, min(len(lines), line_index + 11)):
            if not lines[i].strip():
                empty_after += 1
        
        # ページ番号のような数字が末尾にある
        if re.search(r'\s+[0-9]+\s*$', line):
            return True
        
        # 罫線文字が含まれている（目次や装飾）
        if 'ʜ' in line or '…' in line:
            return True
        
        # 本文っぽい文章が続いていない（次の行がまた章番号など）
        if line_index + 1 < len(lines):
            next_line = lines[line_index + 1].strip()
            if next_line and re.match(r'^[0-9]+\s*章', next_line):
                return True
        
        return False
    
    def _titles_match(self, title1: str, title2: str) -> bool:
        """2つのタイトルが同じ章を指しているかチェック"""
        if not title1 or not title2:
            return True  # 空の場合は一致とみなす
        
        # 特殊文字やスペースを除去して比較
        clean_title1 = re.sub(r'[ʜ…\s\u3000]+', '', title1)
        clean_title2 = re.sub(r'[ʜ…\s\u3000]+', '', title2)
        
        # 部分一致でチェック（最初の5文字程度）
        if len(clean_title1) >= 5 and len(clean_title2) >= 5:
            return clean_title1[:5] in clean_title2 or clean_title2[:5] in clean_title1
        
        return True

def test_final_improved_detection():
    """最終改良版の検出の試行"""
    pdf_path = "/home/junichiro/src/github.com/junichiro/pdf_chapter_splitter/pdfs/llm-prompt-engineering.pdf"
    
    print("=== 現在の検出方法 ===")
    original_splitter = PDFChapterSplitter(pdf_path)
    text = original_splitter.extract_text()
    original_boundaries = original_splitter.find_chapter_boundaries(text)
    print(f"検出された章数: {len(original_boundaries)}")
    
    print("\n=== 最終改良版検出方法 ===")
    improved_splitter = FinalImprovedPDFChapterSplitter(pdf_path)
    improved_boundaries = improved_splitter.find_chapter_boundaries(text)
    print(f"検出された章数: {len(improved_boundaries)}")
    
    print("\n=== 最終改良版検出結果 ===")
    for i, (line_num, title) in enumerate(improved_boundaries):
        print(f"{i+1:2d}. 行{line_num:4d}: {title}")

if __name__ == "__main__":
    test_final_improved_detection()