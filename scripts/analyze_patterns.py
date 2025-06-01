#!/usr/bin/env python3
"""
章検出パターンの分析スクリプト
142個のファイルが生成される原因を特定する
"""

import re
from pathlib import Path
from src.pdf_chapter_splitter.splitter import PDFChapterSplitter

def analyze_chapter_patterns(pdf_path: str):
    """各章検出パターンがどの程度マッチしているかを分析"""
    
    # PDFからテキストを抽出
    splitter = PDFChapterSplitter(pdf_path)
    text = splitter.extract_text()
    lines = text.split('\n')
    
    # 現在のパターン
    chapter_patterns = [
        (r'^第?\s*[0-9IVX一二三四五六七八九十百]+\s*[章部編篇]', "日本語章番号"),
        (r'^Chapter\s+[0-9IVX]+', "英語Chapter"),
        (r'^[0-9]+\.\s*[A-Z]', "番号付きセクション"),
        (r'^[0-9]+\s+[A-Z][A-Za-z\s]+$', "番号+タイトル"),
    ]
    
    # 各パターンのマッチ結果を記録
    pattern_matches = {name: [] for _, name in chapter_patterns}
    all_matches = []
    
    print("=== 章検出パターン分析 ===\n")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 各パターンをチェック
        for pattern, name in chapter_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                match_info = {
                    'line_num': i,
                    'line': line,
                    'pattern': name
                }
                pattern_matches[name].append(match_info)
                all_matches.append(match_info)
                break
    
    # 結果を表示
    print(f"総マッチ数: {len(all_matches)}")
    print("\n各パターンのマッチ数:")
    for name, matches in pattern_matches.items():
        print(f"  {name}: {len(matches)} 件")
    
    print("\n=== 最初の50件のマッチ ===")
    for i, match in enumerate(all_matches[:50]):
        print(f"{i+1:3d}. 行{match['line_num']:4d} [{match['pattern']}]: {match['line']}")
    
    if len(all_matches) > 50:
        print(f"\n... 他 {len(all_matches) - 50} 件")
    
    # 真の章らしきものを識別
    print("\n=== 真の章候補 (より厳格なパターン) ===")
    strict_patterns = [
        (r'^第\s*[0-9一二三四五六七八九十]+\s*章', "第X章"),
        (r'^Chapter\s+[0-9]+', "Chapter X"),
        (r'^[0-9]+\.\s*[A-Z][a-z]+', "1. Introduction形式"),
    ]
    
    strict_matches = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        for pattern, name in strict_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                strict_matches.append({
                    'line_num': i,
                    'line': line,
                    'pattern': name
                })
                break
    
    print(f"厳格パターンでのマッチ数: {len(strict_matches)}")
    for i, match in enumerate(strict_matches):
        print(f"{i+1:2d}. 行{match['line_num']:4d} [{match['pattern']}]: {match['line']}")
    
    # 問題のある行の特徴を分析
    print("\n=== 問題のある可能性が高いマッチ ===")
    problematic = []
    for match in all_matches:
        line = match['line']
        # 短すぎる行、数字だけ、ページ番号らしきもの
        if (len(line) < 10 or 
            re.match(r'^\s*[0-9]+\s*$', line) or 
            'page' in line.lower() or
            len(line.split()) < 3):
            problematic.append(match)
    
    print(f"問題のある可能性が高いマッチ: {len(problematic)} 件")
    for i, match in enumerate(problematic[:20]):
        print(f"{i+1:2d}. 行{match['line_num']:4d} [{match['pattern']}]: '{match['line']}'")
    
    if len(problematic) > 20:
        print(f"... 他 {len(problematic) - 20} 件")

if __name__ == "__main__":
    pdf_path = "/home/junichiro/src/github.com/junichiro/pdf_chapter_splitter/pdfs/llm-prompt-engineering.pdf"
    analyze_chapter_patterns(pdf_path)