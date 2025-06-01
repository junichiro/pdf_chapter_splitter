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

    def find_chapter_boundaries(self, text: str) -> list:
        """
        最終改良版の章の境界検出ロジック
        （final_improved_splitter.py の内容を統合）
        """
        lines = text.split('\n')
        chapter_boundaries = []
        
        print("\n=== 最終改良版章検出を実行中 ===")
        
        # まず目次部分の章を探す（これが真の章リスト）
        toc_chapters = self._find_toc_chapters(lines)
        print(f"目次で見つかった章: {len(toc_chapters)} 個")
        
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
        """目次から章リストを抽出（final_improved_splitter風に改良）"""
        toc_chapters = []
        
        # 目次らしい部分を探す（最初の300行程度）
        for i, line in enumerate(lines[:300]):
            line = line.strip()
            # 「X章 タイトル ... ページ番号」形式を探す
            match = re.match(r'^([0-9]+)章\s*(.+?)\s*[ʜ…\.]*\s*([0-9]+)\s*$', line)
            if match:
                chapter_num = int(match.group(1))
                title = match.group(2).strip()
                if len(title) > 5:  # タイトルが十分長い
                    toc_chapters.append((chapter_num, title))
        
        return sorted(toc_chapters, key=lambda x: x[0])

    def _convert_to_number(self, num_str: str) -> Optional[int]:
        """章番号を数字に変換（final_improved_splitter風に改良）"""
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
        """ページヘッダーかどうかを判定（final_improved_splitter風に改良）"""
        
        # 行の位置をチェック（ページの最初や最後近くはヘッダー/フッターの可能性）
        empty_before = 0
        empty_after = 0
        
        # 前の空行をカウント
        for idx in range(max(0, line_index - 10), line_index):
            if not lines[idx].strip():
                empty_before += 1
        
        # 後の空行をカウント
        for idx in range(line_index + 1, min(len(lines), line_index + 11)):
            if not lines[idx].strip():
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
        """2つのタイトルが同じ章を指しているかどうかを比較"""
        if not title1 or not title2:
            return True  # どちらかが空なら、一致とみなす
        
        # 特殊文字やスペースを除去して比較
        clean_title1 = re.sub(r'[ʜ…\s\u3000]+', '', title1)
        clean_title2 = re.sub(r'[ʜ…\s\u3000]+', '', title2)
        
        # 部分一致でチェック（最初の5文字程度）
        if len(clean_title1) >= 5 and len(clean_title2) >= 5:
            return (clean_title1[:5] in clean_title2) or (clean_title2[:5] in clean_title1)
        
        return True
        
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
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file, strict=False)
                last_page = len(reader.pages) - 1
            output_path = self.split_pdf_by_pages(0, last_page, "000.pdf")
            return [output_path]
        
        print(f"{len(chapter_boundaries)} 個の章が見つかりました:")
        for i, (_, title) in enumerate(chapter_boundaries):
            print(f"  {i:02d}: {title}")
        
        # 章ごとのページ範囲を計算
        chapter_pages = self.find_chapter_pages(chapter_boundaries)
        
        # もし最初の章が0ページ目以降から始まるならば前文として分割対象に追加
        if chapter_pages and chapter_pages[0][0] > 0:
            front_matter_end = chapter_pages[0][0] - 1
            if front_matter_end >= 0:
                chapter_pages.insert(0, (0, front_matter_end, "前文"))

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
