# PDF Chapter Splitter

PDFファイルを章ごとに自動分割するPythonツールです。

## 特徴

- **自動章検出**: PDFの内容を解析して章の境界を自動的に検出
- **複数形式対応**: 日本語・英語の様々な章形式に対応
- **簡単操作**: コマンドライン一つで分割実行
- **整理された出力**: 000.pdf、001.pdf、002.pdf...の3桁形式で順序付けて保存

## インストール

### 方法1: uvを使用（推奨）

```bash
git clone https://github.com/junichiro/pdf_chapter_splitter.git
cd pdf_chapter_splitter
uv sync
```

### 方法2: pipを使用

```bash
git clone https://github.com/junichiro/pdf_chapter_splitter.git
cd pdf_chapter_splitter
pip install -e .
```

## 使用方法

### uvでインストールした場合

```bash
# 基本的な使用方法
uv run pdf-chapter-splitter input.pdf

# 出力ディレクトリを指定
uv run pdf-chapter-splitter input.pdf --output-dir ./chapters

# 詳細情報を表示
uv run pdf-chapter-splitter input.pdf --verbose

# ヘルプを表示
uv run pdf-chapter-splitter --help
```

### pipでインストールした場合

```bash
# 基本的な使用方法
pdf-chapter-splitter input.pdf

# 出力ディレクトリを指定
pdf-chapter-splitter input.pdf --output-dir ./chapters

# 詳細情報を表示
pdf-chapter-splitter input.pdf --verbose

# ヘルプを表示
pdf-chapter-splitter --help
```

### 実行例

```bash
# プロジェクトディレクトリで実行
cd pdf_chapter_splitter
uv run pdf-chapter-splitter sample.pdf

# 別のディレクトリから実行
uv run --directory /path/to/pdf_chapter_splitter pdf-chapter-splitter ~/Documents/book.pdf --output-dir ~/Desktop/chapters
```

## Supported Chapter Formats

- **Japanese**: 第1章、第一章、第2章、第二章...
- **English**: Chapter 1, Chapter 2, Chapter I, Chapter II...  
- **Numbered**: 1. Introduction, 2. Methods, 3. Results...
- **Numbers Only**: 1 Introduction, 2 Methods...

## Project Structure

```
pdf_chapter_splitter/
├── src/
│   └── pdf_chapter_splitter/
│       ├── __init__.py
│       ├── cli.py          # Command line interface
│       └── splitter.py     # Main logic for chapter splitting
├── tests/
│   ├── __init__.py
│   └── test_splitter.py    # Unit tests
├── pdfs/                   # Test PDF files
├── pyproject.toml          # Project configuration
└── README.md
```

## Development

### Development Environment Setup

```bash
# Clone the project
git clone https://github.com/junichiro/pdf_chapter_splitter.git
cd pdf_chapter_splitter

# Install including development dependencies
uv sync --dev
```

### Running Tests

```bash
# Run unit tests
uv run pytest

# Verify operation with test PDF
uv run pdf-chapter-splitter pdfs/sample.pdf
```

### How to Run from New Terminal

When running from a different terminal, you have the following options:

#### Method 1: Specify project directory with uv

```bash
# Execute from any directory
uv run --directory /path/to/pdf_chapter_splitter pdf-chapter-splitter input.pdf
```

#### Method 2: Install system-wide

```bash
# Execute in project directory
cd /path/to/pdf_chapter_splitter
pip install -e .

# Then executable from any directory
pdf-chapter-splitter input.pdf
```

#### Method 3: Add to PATH

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/path/to/pdf_chapter_splitter/.venv/bin:$PATH"

# Then executable from any directory
pdf-chapter-splitter input.pdf
```

## Dependencies

- Python >= 3.12
- click >= 8.2.1 (CLI)
- pypdf >= 4.0.0 (PDF operations)