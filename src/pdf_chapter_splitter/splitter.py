import re
from pathlib import Path
from typing import List, Tuple, Optional
import PyPDF2


class PDFChapterSplitter:
    def __init__(self, pdf_path: str, output_dir: Optional[str] = None):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir) if output_dir else self.pdf_path.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_text(self) -> str:
        """PDFからテキストを抽出"""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def find_chapter_boundaries(self, text: str) -> List[Tuple[int, str]]:
        """章の境界を見つける"""
        lines = text.split('\n')
        chapter_boundaries = []
        
        # 章のパターンを定義（より柔軟に）
        chapter_patterns = [
            r'^第?\s*[0-9IVX一二三四五六七八九十百]+\s*[章部編篇]',  # 第1章、第一章、I章など
            r'^Chapter\s+[0-9IVX]+',  # Chapter 1, Chapter I など
            r'^[0-9]+\.\s*[A-Z]',  # 1. Introduction など
            r'^[0-9]+\s+[A-Z][A-Za-z\s]+$',  # 1 Introduction など
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 各パターンをチェック
            for pattern in chapter_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    chapter_boundaries.append((i, line))
                    break
        
        return chapter_boundaries
    
    def get_page_breaks(self) -> List[int]:
        """各ページの開始行を取得"""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            page_breaks = [0]  # 最初のページは0行目から
            current_line = 0
            
            for page in reader.pages:
                page_text = page.extract_text()
                page_lines = len(page_text.split('\n'))
                current_line += page_lines
                page_breaks.append(current_line)
                
        return page_breaks
    
    def find_chapter_pages(self, chapter_boundaries: List[Tuple[int, str]]) -> List[Tuple[int, int, str]]:
        """章ごとのページ範囲を計算"""
        page_breaks = self.get_page_breaks()
        chapter_pages = []
        
        for i, (line_num, title) in enumerate(chapter_boundaries):
            # 章の開始ページを見つける
            start_page = 0
            for j, page_break in enumerate(page_breaks):
                if line_num >= page_break:
                    start_page = j
                else:
                    break
            
            # 次の章の開始ページまたは最終ページを終了ページとする
            if i + 1 < len(chapter_boundaries):
                next_line_num = chapter_boundaries[i + 1][0]
                end_page = start_page
                for j, page_break in enumerate(page_breaks):
                    if next_line_num >= page_break:
                        end_page = j
                    else:
                        break
            else:
                # 最後の章の場合は最終ページまで
                with open(self.pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    end_page = len(reader.pages) - 1
            
            chapter_pages.append((start_page, end_page, title))
            
        return chapter_pages
    
    def split_pdf_by_pages(self, start_page: int, end_page: int, output_filename: str):
        """指定されたページ範囲でPDFを分割"""
        with open(self.pdf_path, 'rb') as input_file:
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()
            
            # 指定範囲のページを追加
            for page_num in range(start_page, min(end_page + 1, len(reader.pages))):
                writer.add_page(reader.pages[page_num])
            
            # 出力ファイルに書き込み
            output_path = self.output_dir / output_filename
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
        return output_path
    
    def split(self) -> List[Path]:
        """PDFを章ごとに分割"""
        print(f"PDFファイル '{self.pdf_path}' を分析中...")
        
        # テキストを抽出
        text = self.extract_text()
        
        # 章の境界を見つける
        chapter_boundaries = self.find_chapter_boundaries(text)
        
        if not chapter_boundaries:
            print("章の区切りが見つかりませんでした。全体を1つのファイルとして保存します。")
            output_path = self.split_pdf_by_pages(0, -1, "00.pdf")
            return [output_path]
        
        print(f"{len(chapter_boundaries)} 個の章が見つかりました:")
        for i, (_, title) in enumerate(chapter_boundaries):
            print(f"  {i:02d}: {title}")
        
        # 章ごとのページ範囲を計算
        chapter_pages = self.find_chapter_pages(chapter_boundaries)
        
        # 各章をPDFファイルに分割
        output_files = []
        for i, (start_page, end_page, title) in enumerate(chapter_pages):
            output_filename = f"{i:02d}.pdf"
            print(f"章 {i:02d} (ページ {start_page+1}-{end_page+1}) を '{output_filename}' に保存中...")
            
            output_path = self.split_pdf_by_pages(start_page, end_page, output_filename)
            output_files.append(output_path)
        
        print(f"\n分割完了! {len(output_files)} 個のファイルが '{self.output_dir}' に保存されました。")
        return output_files


def split_pdf_chapters(pdf_path: str, output_dir: Optional[str] = None) -> List[Path]:
    """PDFを章ごとに分割する関数"""
    splitter = PDFChapterSplitter(pdf_path, output_dir)
    return splitter.split()