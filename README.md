# PDF Chapter Splitter

PDFファイルを章ごとに自動分割するPythonツールです。

## 特徴

- **自動章検出**: PDFの内容を解析して章の境界を自動的に検出
- **複数形式対応**: 日本語・英語の様々な章形式に対応
- **簡単操作**: コマンドライン一つで分割実行
- **整理された出力**: 000.pdf、001.pdf、002.pdf...の3桁形式で順序付けて保存

## インストール

```bash
git clone https://github.com/junichiro/pdf_chapter_splitter.git
cd pdf_chapter_splitter
uv sync
```

## 使用方法

```bash
# 基本的な使用方法
pdf-chapter-splitter input.pdf

# 出力ディレクトリを指定
pdf-chapter-splitter input.pdf --output-dir ./chapters

# 詳細情報を表示
pdf-chapter-splitter input.pdf --verbose
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

### テスト実行

```bash
uv run pytest
```

### 開発環境セットアップ

```bash
# 開発用依存関係を含めてインストール
uv sync --dev

# パッケージを開発モードでインストール
uv pip install -e .
```

## 依存関係

- Python >= 3.12
- click >= 8.2.1 (CLI)
- pypdf >= 4.0.0 (PDF操作)
- pikepdf >= 8.0.0 (PDF最適化)