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

## 対応する章形式

- **日本語**: 第1章、第一章、第2章、第二章...
- **英語**: Chapter 1, Chapter 2, Chapter I, Chapter II...  
- **番号付き**: 1. Introduction, 2. Methods, 3. Results...
- **数字のみ**: 1 Introduction, 2 Methods...

## プロジェクト構成

```
pdf_chapter_splitter/
├── src/
│   └── pdf_chapter_splitter/
│       ├── __init__.py
│       ├── cli.py          # コマンドラインインターフェース
│       └── splitter.py     # 章分割のメインロジック
├── tests/
│   ├── __init__.py
│   └── test_splitter.py    # ユニットテスト
├── pdfs/                   # テスト用PDFファイル
├── pyproject.toml          # プロジェクト設定
└── README.md
```

## 開発

### 開発環境セットアップ

```bash
# プロジェクトをクローン
git clone https://github.com/junichiro/pdf_chapter_splitter.git
cd pdf_chapter_splitter

# 開発用依存関係を含めてインストール
uv sync --dev
```

### テスト実行

```bash
# ユニットテスト実行
uv run pytest

# テスト用PDFで動作確認
uv run pdf-chapter-splitter pdfs/sample.pdf
```

### 新しいターミナルでの実行方法

別のターミナルから実行する場合は以下の方法があります：

#### 方法1: uvでプロジェクトディレクトリを指定

```bash
# 任意のディレクトリから実行
uv run --directory /path/to/pdf_chapter_splitter pdf-chapter-splitter input.pdf
```

#### 方法2: システム全体にインストール

```bash
# プロジェクトディレクトリで実行
cd /path/to/pdf_chapter_splitter
pip install -e .

# その後、任意のディレクトリから実行可能
pdf-chapter-splitter input.pdf
```

#### 方法3: パスを通す

```bash
# ~/.bashrc や ~/.zshrc に追加
export PATH="/path/to/pdf_chapter_splitter/.venv/bin:$PATH"

# その後、任意のディレクトリから実行可能
pdf-chapter-splitter input.pdf
```

## 依存関係

- Python >= 3.12
- click >= 8.2.1 (CLI)
- pypdf >= 4.0.0 (PDF操作)
- pikepdf >= 8.0.0 (PDF最適化)