#!/usr/bin/env python3
"""
章検出のデバッグ
"""

from src.pdf_chapter_splitter.splitter import PDFChapterSplitter

def debug_chapter_detection():
    pdf_path = "/home/junichiro/src/github.com/junichiro/pdf_chapter_splitter/pdfs/llm-prompt-engineering.pdf"
    splitter = PDFChapterSplitter(pdf_path)
    text = splitter.extract_text()
    lines = text.split('\n')
    
    # 目次の章を確認
    toc_chapters = splitter._find_toc_chapters(lines)
    print("=== 目次で見つかった章 ===")
    for chapter_num, title in toc_chapters:
        print(f"章{chapter_num}: {title}")
    
    # 目次の章情報をディクショナリに格納
    expected_chapters = {}
    for chapter_num, title in toc_chapters:
        expected_chapters[chapter_num] = title.strip()
    
    print(f"\n=== 期待される章: {expected_chapters.keys()} ===")
    
    # 本文で章らしき行を全て探す
    print("\n=== 本文で見つかった章らしき行 ===")
    chapter_candidates = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 15:
            continue
        
        # 章番号とタイトルを抽出
        import re
        chapter_match = re.match(r'^第?\s*([0-9一二三四五六七八九十]+)\s*章\s*(.*)', line)
        if chapter_match:
            chapter_num_str = chapter_match.group(1)
            chapter_title = chapter_match.group(2).strip()
            
            # 章番号を数字に変換
            chapter_num = splitter._convert_to_number(chapter_num_str)
            
            candidate_info = {
                'line_num': i,
                'line': line,
                'chapter_num': chapter_num,
                'in_expected': chapter_num in expected_chapters if chapter_num else False,
                'is_header': splitter._is_likely_page_header(lines, i, line)
            }
            chapter_candidates.append(candidate_info)
    
    print(f"章候補の総数: {len(chapter_candidates)}")
    
    # 期待される章に該当するもの
    print("\n=== 期待される章番号に該当する候補 ===")
    expected_candidates = [c for c in chapter_candidates if c['in_expected']]
    
    for i, candidate in enumerate(expected_candidates[:20]):  # 最初の20件
        header_status = "ヘッダー" if candidate['is_header'] else "本文"
        print(f"{i+1:2d}. 行{candidate['line_num']:4d} [章{candidate['chapter_num']}] [{header_status}]: {candidate['line']}")
    
    if len(expected_candidates) > 20:
        print(f"... 他 {len(expected_candidates) - 20} 件")

if __name__ == "__main__":
    debug_chapter_detection()