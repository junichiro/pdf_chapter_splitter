import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from pdf_chapter_splitter.splitter import PDFChapterSplitter, split_pdf_chapters


class TestPDFChapterSplitter:
    def test_init(self, tmp_path):
        """初期化のテスト"""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()
        
        splitter = PDFChapterSplitter(str(pdf_path))
        
        assert splitter.pdf_path == pdf_path
        assert splitter.output_dir == pdf_path.parent / "output"
        assert splitter.output_dir.exists()
    
    def test_init_with_output_dir(self, tmp_path):
        """カスタム出力ディレクトリのテスト"""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()
        output_dir = tmp_path / "custom_output"
        
        splitter = PDFChapterSplitter(str(pdf_path), str(output_dir))
        
        assert splitter.output_dir == output_dir
        assert splitter.output_dir.exists()
    
    def test_find_chapter_boundaries(self):
        """章の境界検出のテスト"""
        splitter = PDFChapterSplitter("dummy.pdf")
        
        test_text = """
前文テキスト

第1章 はじめに
内容1

第2章 方法
内容2

Chapter 3 Results
内容3

1. Introduction
内容4
        """
        
        boundaries = splitter.find_chapter_boundaries(test_text)
        
        # 検出された章の数を確認
        assert len(boundaries) >= 3  # 最低でも3つの章が検出されるはず
        
        # 章のタイトルが含まれているか確認
        titles = [title for _, title in boundaries]
        assert any("第1章" in title for title in titles)
        assert any("第2章" in title for title in titles)
    
    def test_find_chapter_boundaries_no_chapters(self):
        """章が見つからない場合のテスト"""
        splitter = PDFChapterSplitter("dummy.pdf")
        
        test_text = """
これは普通のテキストです。
章の区切りはありません。
        """
        
        boundaries = splitter.find_chapter_boundaries(test_text)
        
        assert len(boundaries) == 0
    
    @patch('pdf_chapter_splitter.splitter.open', new_callable=mock_open)
    @patch('pypdf.PdfReader')
    def test_extract_text(self, mock_pdf_reader, mock_file):
        """テキスト抽出のテスト"""
        # PDFReaderのモックを設定
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
        """split_pdf_chapters関数のテスト"""
        with patch.object(PDFChapterSplitter, 'split') as mock_split:
            mock_split.return_value = [Path("00.pdf"), Path("01.pdf")]
            
            result = split_pdf_chapters("test.pdf")
            
            assert len(result) == 2
            assert all(isinstance(path, Path) for path in result)
            mock_split.assert_called_once()


@pytest.fixture
def sample_pdf_text():
    """テスト用のサンプルPDFテキスト"""
    return """
目次

第1章 序論
1.1 背景
1.2 目的

第2章 方法論  
2.1 データ収集
2.2 分析手法

第3章 結果
3.1 基本統計
3.2 詳細分析

第4章 考察
4.1 結果の解釈
4.2 限界

第5章 結論
5.1 まとめ
5.2 今後の課題
    """


class TestChapterDetection:
    """章検出の詳細テスト"""
    
    def test_japanese_chapters(self, sample_pdf_text):
        """日本語の章検出テスト"""
        splitter = PDFChapterSplitter("dummy.pdf")
        boundaries = splitter.find_chapter_boundaries(sample_pdf_text)
        
        # 5つの章が検出されることを確認
        assert len(boundaries) == 5
        
        # 各章のタイトルを確認
        titles = [title for _, title in boundaries]
        assert "第1章 序論" in titles
        assert "第2章 方法論" in titles
        assert "第3章 結果" in titles
    
    def test_english_chapters(self):
        """英語の章検出テスト"""
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