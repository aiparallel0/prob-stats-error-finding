#!/usr/bin/env python3
"""
Main script for scanning PDF and text files and detecting errors.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from pdf_extractor import PDFExtractor
from error_detector import ErrorDetector

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Warning: tqdm not available. Install with 'pip install tqdm' for progress bars.")


def scan_text_file(file_path: str, output_dir: str = 'error_reports', enable_grammar: bool = True, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Scan a text file for errors line by line.
    
    Args:
        file_path: Path to the text file
        output_dir: Directory to save error reports
        enable_grammar: Whether to enable grammar checking
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing scan results
    """
    print(f"\n{'='*60}")
    print(f"Scanning Text File: {file_path}")
    print(f"{'='*60}\n")
    
    # Initialize detector
    detector = ErrorDetector(enable_grammar_check=enable_grammar, enable_turkish=True, config=config)
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    print(f"Total lines: {total_lines}\n")
    
    if total_lines == 0:
        print("Error: File is empty.")
        return None
    
    # Scan results
    results = {
        'file': file_path,
        'scan_date': datetime.now().isoformat(),
        'total_lines': total_lines,
        'lines_with_errors': []
    }
    
    total_errors = 0
    error_summary = {
        'grammar_punctuation': 0,
        'mathematical': 0,
        'turkish': 0,
        'spacing': 0
    }
    
    # Prepare iterator with optional progress bar
    if TQDM_AVAILABLE:
        line_iterator = tqdm(enumerate(lines, start=1), total=total_lines, desc="Scanning lines")
    else:
        line_iterator = enumerate(lines, start=1)
    
    # Scan each line
    for line_num, line_text in line_iterator:
        line_text = line_text.rstrip('\n')
        
        if not line_text.strip():
            continue
        
        # Detect errors
        errors = detector.check_all_errors(line_text)
        
        # Count total errors for this line
        line_error_count = sum(len(errs) for errs in errors.values())
        
        if line_error_count > 0:
            total_errors += line_error_count
            
            # Update summary
            error_summary['grammar_punctuation'] += len(errors.get('grammar_punctuation', []))
            error_summary['mathematical'] += len(errors.get('mathematical', []))
            error_summary['turkish'] += len(errors.get('turkish', []))
            error_summary['spacing'] += len(errors.get('spacing', []))
            
            # Store line results
            results['lines_with_errors'].append({
                'line_number': line_num,
                'text': line_text,
                'errors': errors,
                'error_count': line_error_count
            })
    
    results['total_errors'] = total_errors
    results['error_summary'] = error_summary
    
    # Clean up
    detector.close()
    
    print(f"\n{'='*60}")
    print(f"Scan Complete!")
    print(f"Total errors found: {total_errors}")
    print(f"  - Grammar/Punctuation: {error_summary['grammar_punctuation']}")
    print(f"  - Mathematical: {error_summary['mathematical']}")
    print(f"  - Turkish-specific: {error_summary['turkish']}")
    print(f"  - Spacing: {error_summary['spacing']}")
    print(f"{'='*60}\n")
    
    # Save report
    save_report(results, output_dir, is_text_file=True)
    
    return results


def scan_pdf(pdf_path: str, output_dir: str = 'error_reports', enable_grammar: bool = True, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Scan a PDF file for errors page by page.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save error reports
        enable_grammar: Whether to enable grammar checking
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing scan results
    """
    print(f"\n{'='*60}")
    print(f"Scanning PDF: {pdf_path}")
    print(f"{'='*60}\n")
    
    # Initialize extractor and detector
    extractor = PDFExtractor(pdf_path)
    detector = ErrorDetector(enable_grammar_check=enable_grammar, enable_turkish=True, config=config)
    
    # Get page count
    page_count = extractor.get_page_count()
    print(f"Total pages: {page_count}\n")
    
    if page_count == 0:
        print("Error: Could not read PDF or PDF is empty.")
        return None
    
    # Scan results
    results = {
        'pdf_file': pdf_path,
        'scan_date': datetime.now().isoformat(),
        'total_pages': page_count,
        'pages': []
    }
    
    total_errors = 0
    
    # Extract and check each page
    pages_data = extractor.extract_all_pages()
    
    # Prepare iterator with optional progress bar
    if TQDM_AVAILABLE:
        page_iterator = tqdm(pages_data, desc="Scanning pages")
    else:
        page_iterator = pages_data
    
    for page_data in page_iterator:
        page_num = page_data['page_number']
        text = page_data['text']
        
        if not TQDM_AVAILABLE:
            print(f"Scanning page {page_num}...")
        
        if not text or not text.strip():
            if not TQDM_AVAILABLE:
                print(f"  Warning: Page {page_num} is empty or could not be extracted.")
            results['pages'].append({
                'page_number': page_num,
                'text_length': 0,
                'errors': {},
                'total_errors': 0,
                'note': 'Empty or unreadable page'
            })
            continue
        
        # Detect errors
        errors = detector.check_all_errors(text)
        
        # Count total errors for this page
        page_error_count = (
            len(errors.get('grammar_punctuation', [])) + 
            len(errors.get('mathematical', [])) +
            len(errors.get('turkish', [])) +
            len(errors.get('spacing', []))
        )
        
        total_errors += page_error_count
        
        if not TQDM_AVAILABLE:
            print(f"  Found {page_error_count} error(s)")
            print(f"    - Grammar/Punctuation: {len(errors.get('grammar_punctuation', []))}")
            print(f"    - Mathematical: {len(errors.get('mathematical', []))}")
            print(f"    - Turkish-specific: {len(errors.get('turkish', []))}")
            print(f"    - Spacing: {len(errors.get('spacing', []))}")
        
        # Store page results
        results['pages'].append({
            'page_number': page_num,
            'text_length': len(text),
            'errors': errors,
            'total_errors': page_error_count
        })
    
    results['total_errors'] = total_errors
    
    # Clean up
    detector.close()
    
    print(f"\n{'='*60}")
    print(f"Scan Complete!")
    print(f"Total errors found: {total_errors}")
    print(f"{'='*60}\n")
    
    # Save report
    save_report(results, output_dir, is_text_file=False)
    
    return results


def save_report(results: Dict[str, Any], output_dir: str, is_text_file: bool = False):
    """
    Save error report to a JSON file.
    
    Args:
        results: Scan results dictionary
        output_dir: Directory to save the report
        is_text_file: Whether the scan was for a text file (vs PDF)
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    if is_text_file:
        file_name = Path(results['file']).stem
    else:
        file_name = Path(results['pdf_file']).stem
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"{file_name}_errors_{timestamp}.json"
    report_path = Path(output_dir) / report_filename
    
    # Save report
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Report saved to: {report_path}")
    
    # Also create a human-readable summary
    summary_filename = f"{file_name}_summary_{timestamp}.txt"
    summary_path = Path(output_dir) / summary_filename
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"Error Detection Report\n")
        f.write(f"{'='*60}\n\n")
        
        if is_text_file:
            f.write(f"File: {results['file']}\n")
            f.write(f"Scan Date: {results['scan_date']}\n")
            f.write(f"Total Lines: {results['total_lines']}\n")
            f.write(f"Total Errors: {results['total_errors']}\n\n")
            
            if 'error_summary' in results:
                f.write(f"Error Summary:\n")
                f.write(f"  - Grammar/Punctuation: {results['error_summary']['grammar_punctuation']}\n")
                f.write(f"  - Mathematical: {results['error_summary']['mathematical']}\n")
                f.write(f"  - Turkish-specific: {results['error_summary']['turkish']}\n")
                f.write(f"  - Spacing: {results['error_summary']['spacing']}\n\n")
            
            for line_data in results.get('lines_with_errors', []):
                if line_data['error_count'] > 0:
                    f.write(f"\nLine {line_data['line_number']} - {line_data['error_count']} error(s)\n")
                    f.write(f"{'-'*60}\n")
                    f.write(f"Text: {line_data['text']}\n\n")
                    
                    _write_errors_to_summary(f, line_data['errors'])
        else:
            f.write(f"PDF File: {results['pdf_file']}\n")
            f.write(f"Scan Date: {results['scan_date']}\n")
            f.write(f"Total Pages: {results['total_pages']}\n")
            f.write(f"Total Errors: {results['total_errors']}\n\n")
            
            for page in results['pages']:
                if page['total_errors'] > 0:
                    f.write(f"\nPage {page['page_number']} - {page['total_errors']} error(s)\n")
                    f.write(f"{'-'*60}\n")
                    
                    _write_errors_to_summary(f, page['errors'])
    
    print(f"Summary saved to: {summary_path}")


def _write_errors_to_summary(f, errors: Dict[str, Any]):
    """
    Write errors to summary file.
    
    Args:
        f: File handle
        errors: Dictionary of errors by type
    """
    # Grammar/Punctuation errors
    if errors.get('grammar_punctuation'):
        f.write(f"\nGrammar/Punctuation Errors:\n")
        for i, error in enumerate(errors['grammar_punctuation'], 1):
            f.write(f"  {i}. {error['message']}\n")
            f.write(f"     Context: {error['context']}\n")
            if error.get('suggestions'):
                f.write(f"     Suggestions: {', '.join(error['suggestions'])}\n")
            f.write(f"\n")
    
    # Mathematical errors
    if errors.get('mathematical'):
        f.write(f"\nMathematical Errors:\n")
        for i, error in enumerate(errors['mathematical'], 1):
            f.write(f"  {i}. {error['message']}\n")
            f.write(f"     Context: {error['context']}\n")
            f.write(f"     Severity: {error.get('severity', 'N/A')}\n")
            if error.get('suggestions'):
                f.write(f"     Suggestions: {', '.join(error['suggestions'])}\n")
            f.write(f"\n")
    
    # Turkish-specific errors
    if errors.get('turkish'):
        f.write(f"\nTurkish-specific Errors:\n")
        for i, error in enumerate(errors['turkish'], 1):
            f.write(f"  {i}. {error['message']}\n")
            f.write(f"     Context: {error['context']}\n")
            f.write(f"     Severity: {error.get('severity', 'N/A')}\n")
            if error.get('suggestions'):
                f.write(f"     Suggestions: {', '.join(error['suggestions'])}\n")
            f.write(f"\n")
    
    # Spacing errors
    if errors.get('spacing'):
        f.write(f"\nSpacing Errors:\n")
        for i, error in enumerate(errors['spacing'], 1):
            f.write(f"  {i}. {error['message']}\n")
            f.write(f"     Context: {error['context']}\n")
            f.write(f"     Severity: {error.get('severity', 'N/A')}\n")
            f.write(f"\n")


def scan_directory(directory: str, output_dir: str = 'error_reports', enable_grammar: bool = True, scan_text: bool = False, config: Optional[Dict[str, Any]] = None):
    """
    Scan all PDF or text files in a directory.
    
    Args:
        directory: Directory containing files
        output_dir: Directory to save error reports
        enable_grammar: Whether to enable grammar checking
        scan_text: Whether to scan text files instead of PDFs
        config: Optional configuration dictionary
    """
    if scan_text:
        files = list(Path(directory).glob('*.txt'))
        file_type = "text"
    else:
        files = list(Path(directory).glob('*.pdf'))
        file_type = "PDF"
    
    if not files:
        print(f"No {file_type} files found in {directory}")
        return
    
    print(f"Found {len(files)} {file_type} file(s) to scan\n")
    
    for file_path in files:
        if scan_text:
            scan_text_file(str(file_path), output_dir, enable_grammar, config)
        else:
            scan_pdf(str(file_path), output_dir, enable_grammar, config)
        print()


def main():
    """Main entry point for the PDF and text error scanner."""
    parser = argparse.ArgumentParser(
        description='Scan PDF or text files for grammar, punctuation, mathematical, and Turkish-specific errors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single PDF file
  python scanner.py book.pdf
  
  # Scan a text file
  python scanner.py text.txt --text
  
  # Scan all PDFs in a directory
  python scanner.py --directory ./books
  
  # Scan all text files in a directory
  python scanner.py --directory ./texts --text
  
  # Scan with custom output directory
  python scanner.py book.pdf --output ./my_reports
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Path to file to scan (PDF or text)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='Directory containing files to scan'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='error_reports',
        help='Output directory for error reports (default: error_reports)'
    )
    
    parser.add_argument(
        '--no-grammar',
        action='store_true',
        help='Disable grammar checking (useful for offline mode or faster scanning)'
    )
    
    parser.add_argument(
        '--text',
        action='store_true',
        help='Scan text files instead of PDFs'
    )
    
    args = parser.parse_args()
    
    # Check if we have either a file or directory
    if not args.file and not args.directory:
        parser.print_help()
        sys.exit(1)
    
    try:
        enable_grammar = not args.no_grammar
        config = None  # Could load from config.yaml if needed
        
        if args.directory:
            scan_directory(args.directory, args.output, enable_grammar, args.text, config)
        else:
            if not os.path.exists(args.file):
                print(f"Error: File '{args.file}' not found")
                sys.exit(1)
            
            # Determine file type
            if args.text or args.file.endswith('.txt'):
                scan_text_file(args.file, args.output, enable_grammar, config)
            else:
                scan_pdf(args.file, args.output, enable_grammar, config)
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during scan: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
