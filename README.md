# PDF Chapter Splitter

A Python tool that automatically splits PDF files by chapters.

## Features

- **Automatic Chapter Detection**: Analyzes PDF content to automatically detect chapter boundaries
- **Multiple Format Support**: Supports various chapter formats in Japanese and English
- **Simple Operation**: Split PDFs with a single command line
- **Organized Output**: Saves files in 3-digit format as 000.pdf, 001.pdf, 002.pdf...

## Installation

### Method 1: Using uv (Recommended)

```bash
git clone https://github.com/junichiro/pdf_chapter_splitter.git
cd pdf_chapter_splitter
uv sync
```

### Method 2: Using pip

```bash
git clone https://github.com/junichiro/pdf_chapter_splitter.git
cd pdf_chapter_splitter
pip install -e .
```

## Usage

### When installed with uv

```bash
# Basic usage
uv run pdf-chapter-splitter input.pdf

# Specify output directory
uv run pdf-chapter-splitter input.pdf --output-dir ./chapters

# Show detailed information
uv run pdf-chapter-splitter input.pdf --verbose

# Show help
uv run pdf-chapter-splitter --help
```

### When installed with pip

```bash
# Basic usage
pdf-chapter-splitter input.pdf

# Specify output directory
pdf-chapter-splitter input.pdf --output-dir ./chapters

# Show detailed information
pdf-chapter-splitter input.pdf --verbose

# Show help
pdf-chapter-splitter --help
```

### Usage Examples

```bash
# Run in project directory
cd pdf_chapter_splitter
uv run pdf-chapter-splitter sample.pdf

# Run from another directory
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