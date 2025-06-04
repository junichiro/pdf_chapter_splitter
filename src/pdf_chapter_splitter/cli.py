import click
from pathlib import Path
from .splitter import split_pdf_chapters


@click.command()
@click.argument('pdf_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='Output directory (if not specified, output folder in same directory as input file)')
@click.option('--verbose', '-v', is_flag=True, help='Display detailed information')
def main(pdf_file: Path, output_dir: Path, verbose: bool):
    """Split PDF file by chapters.
    
    PDF_FILE: Path to the PDF file to split
    """
    try:
        if verbose:
            click.echo(f"Input file: {pdf_file}")
            if output_dir:
                click.echo(f"Output directory: {output_dir}")
        
        # Split PDF
        output_files = split_pdf_chapters(str(pdf_file), str(output_dir) if output_dir else None)
        
        click.echo(f"\n✓ Splitting complete! {len(output_files)} files generated:")
        for output_file in output_files:
            click.echo(f"  - {output_file}")
            
    except FileNotFoundError:
        click.echo(f"Error: File '{pdf_file}' not found.", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


if __name__ == '__main__':
    main()