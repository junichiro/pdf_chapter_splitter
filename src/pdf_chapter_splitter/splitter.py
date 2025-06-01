import re
from pathlib import Path
from typing import List, Tuple, Optional
from pypdf import PdfReader, PdfWriter
import pikepdf


class PDFChapterSplitter:
    def __init__(self, pdf_path: str, output_dir: Optional[str] = None):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir) if output_dir else self.pdf_path.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_text(self) -> str:
        """PDFからテキストを抽出"""
        # まずpikepdfで試行（より堅牢）
        try:
            print("pikepdf でPDFを読み込み中...")
            with pikepdf.Pdf.open(self.pdf_path) as pdf:
                print(f"PDFページ数: {len(pdf.pages)}")
                
                # pikepdf用のテキスト抽出は限定的なのでpypdfにフォールバック
                raise Exception("pikepdfからpypdfにフォールバック")
                
        except Exception as pike_error:
            print(f"pikepdf での読み込み失敗: {pike_error}")
            print("pypdf での読み込みを試行中...")
            
            # pypdfで試行
            try:
                with open(self.pdf_path, 'rb') as file:
                    reader = PdfReader(file, strict=False)
                    print(f"pypdf でPDFページ数: {len(reader.pages)}")
                    text = ""
                    for i, page in enumerate(reader.pages):
                        try:
                            page_text = page.extract_text()
                            text += page_text + "\n"
                            if i == 0:  # 最初のページの一部を表示
                                print(f"最初のページのサンプル: {page_text[:200]}...")
                        except Exception as e:
                            print(f"警告: ページ {i+1} の読み込みでエラー: {e}")
                            continue
                return text
                
            except Exception as e:
                print(f"pypdf でもエラー: {e}")
                raise
    
    def find_chapter_boundaries(self, text: str) -> List[Tuple[int, str]]:
        """章の境界を見つける（シンプルアプローチ：各章の最初の出現のみ採用）"""
        lines = text.split('\n')
        chapter_boundaries = []
        
        print("章検出を実行中...")
        
        # 各章番号の最初の出現のみを記録
        seen_chapters = set()
        
        # 章のパターン（日本語の章番号のみに特化）
        chapter_pattern = r'^第?\s*([0-9一二三四五六七八九十]+)\s*章\s*(.*)'
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # 章番号とタイトルを抽出
            chapter_match = re.match(chapter_pattern, line)
            if not chapter_match:
                continue
            
            chapter_num_str = chapter_match.group(1)
            chapter_title = chapter_match.group(2).strip()
            
            # 章番号を数字に変換
            chapter_num = self._convert_to_number(chapter_num_str)
            if chapter_num is None:
                continue
            
            # 1〜15章の範囲内の章のみ
            if chapter_num < 1 or chapter_num > 15:
                continue
            
            # 既に見つかった章はスキップ（最初の出現のみを採用）
            if chapter_num in seen_chapters:
                continue
            
            # 明らかにページヘッダーのものを除外
            if self._is_obviously_header(line):
                continue
            
            # 真の章開始と判定
            chapter_boundaries.append((i, line))
            seen_chapters.add(chapter_num)
            print(f"章 {chapter_num} を検出: 行{i} - {line}")
        
        # 出現順に並んだまま返す
        return chapter_boundaries
    
    def _find_toc_chapters(self, lines: List[str]) -> List[Tuple[int, str]]:
        """目次から章リストを抽出"""
        toc_chapters = []
        
        # 目次らしい部分を探す（最初の300行程度）
        for i, line in enumerate(lines[:300]):
            line = line.strip()
            # 「X章　タイトル　...　ページ番号」形式を探す
            match = re.match(r'^([0-9]+)章\s*(.+?)\s*[ʜ…\.]*\s*([0-9]+)\s*$', line)
            if match:
                chapter_num = int(match.group(1))
                title = match.group(2).strip()
                if len(title) > 5:  # タイトルが十分長い
                    toc_chapters.append((chapter_num, title))
        
        return sorted(toc_chapters, key=lambda x: x[0])
    
    def _convert_to_number(self, num_str: str) -> Optional[int]:
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
    
    def _extract_chapter_number(self, line: str) -> int:
        """行から章番号を抽出"""
        match = re.match(r'^第?\s*([0-9一二三四五六七八九十]+)\s*章', line)
        if match:
            return self._convert_to_number(match.group(1)) or 0
        return 0
    
    def _is_obviously_header(self, line: str) -> bool:
        """明らかにページヘッダーかどうかを判定（シンプル版）"""
        
        # 1. 罫線文字が含まれている（目次や装飾）
        if 'ʜ' in line or '…' in line or re.search(r'[\.]{3,}', line):
            return True
        
        # 2. ページ番号のような数字が末尾にある
        if re.search(r'\s+[0-9]+\s*$', line):
            return True
        
        # 3. 章番号のみの行は除外
        if re.match(r'^\s*[0-9]+章\s*$', line):
            return True
        
        return False
    
    def get_page_breaks(self) -> List[int]:
        """各ページの開始行を取得"""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file, strict=False)
                page_breaks = [0]  # 最初のページは0行目から
                current_line = 0
                
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        page_lines = len(page_text.split('\n'))
                        current_line += page_lines
                        page_breaks.append(current_line)
                    except Exception as e:
                        print(f"警告: ページ {i+1} の処理でエラー: {e}")
                        page_breaks.append(current_line)
                        
            return page_breaks
        except Exception as e:
            print(f"ページ分割処理エラー: {e}")
            raise
    
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
                    reader = PdfReader(file, strict=False)
                    end_page = len(reader.pages) - 1
            
            chapter_pages.append((start_page, end_page, title))
            
        return chapter_pages
    
    def split_pdf_by_pages(self, start_page: int, end_page: int, output_filename: str):
        """指定されたページ範囲でPDFを分割"""
        try:
            with open(self.pdf_path, 'rb') as input_file:
                reader = PdfReader(input_file, strict=False)
                writer = PdfWriter()
                
                # 指定範囲のページを追加
                for page_num in range(start_page, min(end_page + 1, len(reader.pages))):
                    try:
                        writer.add_page(reader.pages[page_num])
                    except Exception as e:
                        print(f"警告: ページ {page_num+1} の追加でエラー: {e}")
                        continue
                
                # 出力ファイルに書き込み
                output_path = self.output_dir / output_filename
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
        except Exception as e:
            print(f"PDF分割エラー: {e}")
            raise
                
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
            output_path = self.split_pdf_by_pages(0, -1, "000.pdf")
            return [output_path]
        
        print(f"{len(chapter_boundaries)} 個の章が見つかりました:")
        for i, (_, title) in enumerate(chapter_boundaries):
            print(f"  {i:02d}: {title}")
        
        # 章ごとのページ範囲を計算
        chapter_pages = self.find_chapter_pages(chapter_boundaries)
        
        # 各章をPDFファイルに分割
        output_files = []
        for i, (start_page, end_page, title) in enumerate(chapter_pages):
            output_filename = f"{i:03d}.pdf"
            print(f"章 {i:02d} (ページ {start_page+1}-{end_page+1}) を '{output_filename}' に保存中...")
            
            output_path = self.split_pdf_by_pages(start_page, end_page, output_filename)
            output_files.append(output_path)
        
        print(f"\n分割完了! {len(output_files)} 個のファイルが '{self.output_dir}' に保存されました。")
        return output_files


def split_pdf_chapters(pdf_path: str, output_dir: Optional[str] = None) -> List[Path]:
    """PDFを章ごとに分割する関数"""
    splitter = PDFChapterSplitter(pdf_path, output_dir)
    return splitter.split()
