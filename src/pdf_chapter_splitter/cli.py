import click
from pathlib import Path
from .splitter import split_pdf_chapters


@click.command()
@click.argument('pdf_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='出力ディレクトリ（指定しない場合は入力ファイルと同じディレクトリのoutputフォルダ）')
@click.option('--verbose', '-v', is_flag=True, help='詳細な情報を表示')
def main(pdf_file: Path, output_dir: Path, verbose: bool):
    """PDFファイルを章ごとに分割します。
    
    PDF_FILE: 分割したいPDFファイルのパス
    """
    try:
        if verbose:
            click.echo(f"入力ファイル: {pdf_file}")
            if output_dir:
                click.echo(f"出力ディレクトリ: {output_dir}")
        
        # PDFを分割
        output_files = split_pdf_chapters(str(pdf_file), str(output_dir) if output_dir else None)
        
        click.echo(f"\n✓ 分割完了! {len(output_files)} 個のファイルが生成されました:")
        for output_file in output_files:
            click.echo(f"  - {output_file}")
            
    except FileNotFoundError:
        click.echo(f"エラー: ファイル '{pdf_file}' が見つかりません。", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"エラー: {str(e)}", err=True)
        exit(1)


if __name__ == '__main__':
    main()