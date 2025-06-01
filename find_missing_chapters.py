#!/usr/bin/env python3
"""
見つからない章を探す
"""

import re
from src.pdf_chapter_splitter.splitter import PDFChapterSplitter

def find_missing_chapters():
    pdf_path = "/home/junichiro/src/github.com/junichiro/pdf_chapter_splitter/pdfs/llm-prompt-engineering.pdf"
    splitter = PDFChapterSplitter(pdf_path)
    text = splitter.extract_text()
    lines = text.split('\n')
    
    # 見つからない章番号
    missing_chapters = [2, 3, 6, 7, 8, 9, 11]
    
    print("=== 見つからない章を検索 ===")
    
    for chapter_num in missing_chapters:
        print(f"\n--- 第{chapter_num}章を検索 ---")
        found_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 章番号を含む行を全て探す
            if re.search(rf'^第?\s*{chapter_num}\s*章', line):
                found_lines.append((i, line))
        
        print(f"第{chapter_num}章の候補: {len(found_lines)} 件")
        
        # 候補を表示（最初の10件）
        for j, (line_num, line_content) in enumerate(found_lines[:10]):
            is_header = splitter._is_obviously_header(line_content)
            header_status = "ヘッダー" if is_header else "本文"
            print(f"  {j+1:2d}. 行{line_num:4d} [{header_status}]: {line_content}")
        
        if len(found_lines) > 10:
            print(f"     ... 他 {len(found_lines) - 10} 件")

if __name__ == "__main__":
    find_missing_chapters()