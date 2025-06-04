import re
from pathlib import Path
from typing import List, Tuple, Optional
from pypdf import PdfReader, PdfWriter


class PDFChapterSplitter:
    def __init__(self, pdf_path: str, output_dir: Optional[str] = None):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir) if output_dir else self.pdf_path.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_text(self) -> str:
        """Extract text from PDF"""
        print("Loading PDF with pypdf...")
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file, strict=False)
                print(f"PDF page count: {len(reader.pages)}")
                text = ""
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        text += page_text + "\n"
                        if i == 0:  # Display part of the first page
                            print(f"First page sample: {page_text[:200]}...")
                    except Exception as e:
                        print(f"Warning: Error loading page {i+1}: {e}")
                        continue
            return text
        except Exception as e:
            print(f"Error with pypdf: {e}")
            raise
    
    def find_chapter_boundaries(self, text: str) -> List[Tuple[int, str]]:
        """Find chapter boundaries (simple approach: only adopt first occurrence of each chapter)"""
        lines = text.split('\n')
        chapter_boundaries = []
        
        print("Detecting chapters...")
        
        # Record only the first occurrence of each chapter number
        seen_chapters = set()
        
        # Chapter pattern (specialized for Japanese chapter numbers only)
        # Chapter pattern
        
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
            
            # Convert chapter number to digit
            chapter_num = self._convert_to_number(chapter_num_str)
            if chapter_num is None:
                continue
            
            # Only chapters within range 1-15
            if chapter_num < 1 or chapter_num > 15:
                continue
            
            # Skip already found chapters (adopt only first occurrence)
            if chapter_num in seen_chapters:
                continue
            
            # Exclude obvious page headers
            if self._is_obviously_header(line):
                continue
            
            # Determine as true chapter start
            chapter_boundaries.append((i, line))
            seen_chapters.add(chapter_num)
            print(f"Detected chapter {chapter_num}: line {i} - {line}")
        
        # Return in order of appearance
        return chapter_boundaries
    
    def _find_toc_chapters(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Extract chapter list from table of contents"""
        toc_chapters = []
        
        # Search for table of contents-like sections (first ~300 lines)
        for i, line in enumerate(lines[:300]):
            line = line.strip()
            # Look for "Chapter X  Title  ...  Page Number" format
            match = re.match(r'^([0-9]+)章\s*(.+?)\s*[ʜ…\.]*\s*([0-9]+)\s*$', line)
            if match:
                chapter_num = int(match.group(1))
                title = match.group(2).strip()
                if len(title) > 5:  # Title is sufficiently long
                    toc_chapters.append((chapter_num, title))
        
        return sorted(toc_chapters, key=lambda x: x[0])
    
    def _convert_to_number(self, num_str: str) -> Optional[int]:
        """Convert chapter number to digit"""
        # For numeric case
        if num_str.isdigit():
            return int(num_str)
        
        # For Chinese numeral case
        kanji_nums = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12
        }
        return kanji_nums.get(num_str)
    
    def _extract_chapter_number(self, line: str) -> int:
        """Extract chapter number from line"""
        match = re.match(r'^第?\s*([0-9一二三四五六七八九十]+)\s*章', line)
        if match:
            return self._convert_to_number(match.group(1)) or 0
        return 0
    
    def _is_obviously_header(self, line: str) -> bool:
        """Determine if obviously a page header (simple version)"""
        
        # 1. Contains line characters (table of contents or decoration)
        if 'ʜ' in line or '…' in line or re.search(r'[\.]{3,}', line):
            return True
        
        # 2. Has page number-like digits at the end
        if re.search(r'\s+[0-9]+\s*$', line):
            return True
        
        # 3. Exclude lines with only chapter numbers
        if re.match(r'^\s*[0-9]+章\s*$', line):
            return True
        
        return False
    
    def _estimate_pages_from_line(self, line_number: int) -> int:
        """Estimate page count from line number"""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file, strict=False)
                
                # Calculate average lines per page from first few pages
                total_lines = 0
                pages_to_sample = min(5, len(reader.pages))
                
                for i in range(pages_to_sample):
                    try:
                        page_text = reader.pages[i].extract_text()
                        page_lines = len(page_text.split('\n'))
                        total_lines += page_lines
                    except Exception:
                        continue
                
                if total_lines > 0:
                    avg_lines_per_page = total_lines / pages_to_sample
                    estimated_page = int(line_number / avg_lines_per_page)
                    return max(1, estimated_page)  # Minimum 1 page
                else:
                    return 1
                    
        except Exception as e:
            print(f"Page estimation error: {e}")
            return 1
    
    def get_page_breaks(self) -> List[int]:
        """Get starting line for each page"""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file, strict=False)
                page_breaks = [0]  # First page starts from line 0
                current_line = 0
                
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        page_lines = len(page_text.split('\n'))
                        current_line += page_lines
                        page_breaks.append(current_line)
                    except Exception as e:
                        print(f"Warning: Error processing page {i+1}: {e}")
                        page_breaks.append(current_line)
                        
            return page_breaks
        except Exception as e:
            print(f"Page splitting process error: {e}")
            raise
    
    def find_chapter_pages(self, chapter_boundaries: List[Tuple[int, str]]) -> List[Tuple[int, int, str]]:
        """Calculate page range for each chapter"""
        page_breaks = self.get_page_breaks()
        chapter_pages = []
        
        for i, (line_num, title) in enumerate(chapter_boundaries):
            # Find chapter start page (shift 1 page earlier)
            start_page = 0
            for j, page_break in enumerate(page_breaks):
                if line_num >= page_break:
                    start_page = j
                else:
                    break
            # Shift 1 page earlier except for first chapter
            if start_page > 0:
                start_page -= 1
            
            # Set next chapter start page or final page as end page
            if i + 1 < len(chapter_boundaries):
                next_line_num = chapter_boundaries[i + 1][0]
                next_start_page = 0
                for j, page_break in enumerate(page_breaks):
                    if next_line_num >= page_break:
                        next_start_page = j
                    else:
                        break
                # Set page before next chapter start as current chapter end (shift 1 page earlier)
                end_page = max(start_page, next_start_page - 2)
            else:
                # For last chapter, go to final page
                with open(self.pdf_path, 'rb') as file:
                    reader = PdfReader(file, strict=False)
                    end_page = len(reader.pages) - 1
            
            chapter_pages.append((start_page, end_page, title))
            
        return chapter_pages
    
    def split_pdf_by_pages(self, start_page: int, end_page: int, output_filename: str):
        """Split PDF by specified page range"""
        try:
            with open(self.pdf_path, 'rb') as input_file:
                reader = PdfReader(input_file, strict=False)
                writer = PdfWriter()
                
                # Add pages in specified range
                for page_num in range(start_page, min(end_page + 1, len(reader.pages))):
                    try:
                        writer.add_page(reader.pages[page_num])
                    except Exception as e:
                        print(f"Warning: Error adding page {page_num+1}: {e}")
                        continue
                
                # Write to output file
                output_path = self.output_dir / output_filename
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
        except Exception as e:
            print(f"PDF splitting error: {e}")
            raise
                
        return output_path
    
    def split(self) -> List[Path]:
        """Split PDF by chapters"""
        print(f"Analyzing PDF file '{self.pdf_path}'...")
        
        # Extract text
        text = self.extract_text()
        
        # Find chapter boundaries
        chapter_boundaries = self.find_chapter_boundaries(text)
        
        if not chapter_boundaries:
            print("No chapter breaks found. Saving entire document as one file.")
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file, strict=False)
                last_page = len(reader.pages) - 1
            output_path = self.split_pdf_by_pages(0, last_page, "000.pdf")
            return [output_path]
        
        print(f"Found {len(chapter_boundaries)} chapters:")
        for i, (_, title) in enumerate(chapter_boundaries):
            print(f"  {i:02d}: {title}")
        
        # Calculate page range for each chapter
        chapter_pages = self.find_chapter_pages(chapter_boundaries)
        
        # Add content before first chapter as 000.pdf
        if chapter_pages:
            first_chapter_start_page = chapter_pages[0][0]
            if first_chapter_start_page > 0:
                # If first chapter starts after page 0, make previous pages 000.pdf
                front_matter_end = first_chapter_start_page - 1
                chapter_pages.insert(0, (0, front_matter_end, "Preface・Table of Contents"))
                print(f"Saving preface・table of contents as 000.pdf (pages 1-{front_matter_end + 1})")
            else:
                # If first chapter starts from page 0, check actual chapter start position
                first_chapter_line = chapter_boundaries[0][0] if chapter_boundaries else 0
                
                # If first chapter is at a much later line (possibility of table of contents or preface)
                if first_chapter_line > 50:  # If first chapter is after line 50
                    # Estimate pages from line numbers for more accurate page splitting
                    estimated_front_matter_pages = self._estimate_pages_from_line(first_chapter_line)
                    if estimated_front_matter_pages > 0:
                        # Update first chapter start page
                        chapter_pages[0] = (estimated_front_matter_pages, chapter_pages[0][1], chapter_pages[0][2])
                        # Add preface
                        chapter_pages.insert(0, (0, estimated_front_matter_pages - 1, "Preface・Table of Contents"))
                        print(f"Estimated: Saving preface・table of contents as 000.pdf (pages 1-{estimated_front_matter_pages})")
        # If no chapters found, entire document is already processed as 000.pdf

        # Split each chapter into PDF files
        output_files = []
        for i, (start_page, end_page, title) in enumerate(chapter_pages):
            output_filename = f"{i:03d}.pdf"
            page_count = end_page - start_page + 1
            print(f"Saving chapter {i:02d} (pages {start_page+1}-{end_page+1}, {page_count} pages) to '{output_filename}'...")
            print(f"  Title: {title[:60]}{'...' if len(title) > 60 else ''}")
            
            output_path = self.split_pdf_by_pages(start_page, end_page, output_filename)
            output_files.append(output_path)
        
        print(f"\nSplitting complete! {len(output_files)} files saved to '{self.output_dir}'.")
        return output_files


def split_pdf_chapters(pdf_path: str, output_dir: Optional[str] = None) -> List[Path]:
    """Function to split PDF by chapters"""
    splitter = PDFChapterSplitter(pdf_path, output_dir)
    return splitter.split()
