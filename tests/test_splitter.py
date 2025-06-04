import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from pdf_chapter_splitter.splitter import PDFChapterSplitter, split_pdf_chapters


class TestPDFChapterSplitter:
    def test_init(self, tmp_path):
        """Test initialization"""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()
        
        splitter = PDFChapterSplitter(str(pdf_path))
        
        assert splitter.pdf_path == pdf_path
        assert splitter.output_dir == pdf_path.parent / "output"
        assert splitter.output_dir.exists()
    
    def test_init_with_output_dir(self, tmp_path):
        """Test custom output directory"""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()
        output_dir = tmp_path / "custom_output"
        
        splitter = PDFChapterSplitter(str(pdf_path), str(output_dir))
        
        assert splitter.output_dir == output_dir
        assert splitter.output_dir.exists()
    
    def test_find_chapter_boundaries(self):
        """Test chapter boundary detection"""
        splitter = PDFChapterSplitter("dummy.pdf")
        
        test_text = """
Preface text

Chapter 1 Introduction
Content 1

Chapter 2 Methods
Content 2

Chapter 3 Results
Content 3

1. Introduction
Content 4
        """
        
        boundaries = splitter.find_chapter_boundaries(test_text)
        
        # Verify number of detected chapters
        assert len(boundaries) >= 3  # At least 3 chapters should be detected
        
        # Verify chapter titles are included
        titles = [title for _, title in boundaries]
        assert any("Chapter 1" in title for title in titles)
        assert any("Chapter 2" in title for title in titles)
    
    def test_find_chapter_boundaries_no_chapters(self):
        """Test when no chapters are found"""
        splitter = PDFChapterSplitter("dummy.pdf")
        
        test_text = """
This is normal text.
There are no chapter breaks.
        """
        
        boundaries = splitter.find_chapter_boundaries(test_text)
        
        assert len(boundaries) == 0
    
    @patch('pdf_chapter_splitter.splitter.open', new_callable=mock_open)
    @patch('pypdf.PdfReader')
    def test_extract_text(self, mock_pdf_reader, mock_file):
        """Test text extraction"""
        # Set up PDFReader mock
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 text"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader
        
        splitter = PDFChapterSplitter("dummy.pdf")
        text = splitter.extract_text()
        
        assert "Page 1 text" in text
        assert "Page 2 text" in text
    
    def test_split_pdf_chapters_function(self):
        """Test split_pdf_chapters function"""
        with patch.object(PDFChapterSplitter, 'split') as mock_split:
            mock_split.return_value = [Path("00.pdf"), Path("01.pdf")]
            
            result = split_pdf_chapters("test.pdf")
            
            assert len(result) == 2
            assert all(isinstance(path, Path) for path in result)
            mock_split.assert_called_once()


@pytest.fixture
def sample_pdf_text():
    """Sample PDF text for testing"""
    return """
Table of Contents

Chapter 1 Introduction
1.1 Background
1.2 Objectives

Chapter 2 Methodology
2.1 Data Collection
2.2 Analysis Methods

Chapter 3 Results
3.1 Basic Statistics
3.2 Detailed Analysis

Chapter 4 Discussion
4.1 Interpretation of Results
4.2 Limitations

Chapter 5 Conclusion
5.1 Summary
5.2 Future Work
    """


class TestChapterDetection:
    """Detailed chapter detection tests"""
    
    def test_japanese_chapters(self, sample_pdf_text):
        """Japanese chapter detection test"""
        splitter = PDFChapterSplitter("dummy.pdf")
        boundaries = splitter.find_chapter_boundaries(sample_pdf_text)
        
        # Verify that 5 chapters are detected
        assert len(boundaries) == 5
        
        # Verify each chapter title
        titles = [title for _, title in boundaries]
        assert "Chapter 1 Introduction" in titles
        assert "Chapter 2 Methodology" in titles
        assert "Chapter 3 Results" in titles
    
    def test_english_chapters(self):
        """English chapter detection test"""
        english_text = """
Table of Contents

Chapter 1 Introduction
1.1 Background
1.2 Objectives

Chapter 2 Methodology
2.1 Data Collection
2.2 Analysis

Chapter 3 Results
3.1 Findings
        """
        
        splitter = PDFChapterSplitter("dummy.pdf")
        boundaries = splitter.find_chapter_boundaries(english_text)
        
        assert len(boundaries) >= 3
        titles = [title for _, title in boundaries]
        assert any("Chapter 1" in title for title in titles)
        assert any("Chapter 2" in title for title in titles)