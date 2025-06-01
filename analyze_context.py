#!/usr/bin/env python3
"""
特定の行の前後文脈を分析
"""

from src.pdf_chapter_splitter.splitter import PDFChapterSplitter

def analyze_line_context(line_index: int, lines: list, context_size: int = 10):
    """指定した行の前後文脈を表示"""
    print(f"\n=== 行{line_index}の前後{context_size}行 ===")
    start = max(0, line_index - context_size)
    end = min(len(lines), line_index + context_size + 1)
    
    for i in range(start, end):
        marker = ">>> " if i == line_index else "    "
        line_content = lines[i].strip()[:100]  # 最初の100文字
        print(f"{marker}行{i:4d}: {line_content}")

def main():
    pdf_path = "/home/junichiro/src/github.com/junichiro/pdf_chapter_splitter/pdfs/llm-prompt-engineering.pdf"
    splitter = PDFChapterSplitter(pdf_path)
    text = splitter.extract_text()
    lines = text.split('\n')
    
    # 興味深い行を分析
    interesting_lines = [320, 392, 434, 480, 529, 609]  # 1章の候補
    
    for line_index in interesting_lines:
        analyze_line_context(line_index, lines)
        
        # ページヘッダー判定の詳細
        line = lines[line_index].strip()
        is_header = splitter._is_likely_page_header(lines, line_index, line)
        print(f"ページヘッダー判定: {is_header}")
        
        # 前後の空行数を詳しく調べる
        empty_before = 0
        for i in range(max(0, line_index - 10), line_index):
            if not lines[i].strip():
                empty_before += 1
        
        has_meaningful_content_after = False
        for i in range(line_index + 1, min(len(lines), line_index + 15)):
            next_line = lines[i].strip()
            if next_line and len(next_line) > 30:
                import re
                if not re.match(r'^[0-9]+\s*章', next_line):
                    has_meaningful_content_after = True
                    print(f"本文らしい行{i}: {next_line[:50]}...")
                    break
        
        print(f"前の空行数: {empty_before}, 後に本文: {has_meaningful_content_after}")
        print("-" * 80)

if __name__ == "__main__":
    main()