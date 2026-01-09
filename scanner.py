#!/usr/bin/env python3
"""
Main script for scanning PDF files and detecting errors.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict
from pdf_extractor import PDFExtractor
from error_detector import ErrorDetector


def scan_pdf(pdf_path: str, output_dir: str = 'error_reports', enable_grammar: bool = True) -> Dict[str, any]:
    """
    Scan a PDF file for errors page by page.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save error reports
        enable_grammar: Whether to enable grammar checking
        
    Returns:
        Dictionary containing scan results
    """
    print(f"\n{'='*60}")
    print(f"Scanning PDF: {pdf_path}")
    print(f"{'='*60}\n")
    
    # Initialize extractor and detector
    extractor = PDFExtractor(pdf_path)
    detector = ErrorDetector(enable_grammar_check=enable_grammar)
    
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
    
    for page_data in pages_data:
        page_num = page_data['page_number']
        text = page_data['text']
        
        print(f"Scanning page {page_num}...")
        
        if not text or not text.strip():
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
            len(errors['grammar_punctuation']) + 
            len(errors['mathematical'])
        )
        
        total_errors += page_error_count
        
        print(f"  Found {page_error_count} error(s)")
        print(f"    - Grammar/Punctuation: {len(errors['grammar_punctuation'])}")
        print(f"    - Mathematical: {len(errors['mathematical'])}")
        
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
    save_report(results, output_dir)
    
    return results


def save_report(results: Dict[str, any], output_dir: str):
    """
    Save error report to a JSON file.
    
    Args:
        results: Scan results dictionary
        output_dir: Directory to save the report
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    pdf_name = Path(results['pdf_file']).stem
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"{pdf_name}_errors_{timestamp}.json"
    report_path = Path(output_dir) / report_filename
    
    # Save report
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Report saved to: {report_path}")
    
    # Also create a human-readable summary
    summary_filename = f"{pdf_name}_summary_{timestamp}.txt"
    summary_path = Path(output_dir) / summary_filename
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"Error Detection Report\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"PDF File: {results['pdf_file']}\n")
        f.write(f"Scan Date: {results['scan_date']}\n")
        f.write(f"Total Pages: {results['total_pages']}\n")
        f.write(f"Total Errors: {results['total_errors']}\n\n")
        
        for page in results['pages']:
            if page['total_errors'] > 0:
                f.write(f"\nPage {page['page_number']} - {page['total_errors']} error(s)\n")
                f.write(f"{'-'*60}\n")
                
                # Grammar/Punctuation errors
                if page['errors']['grammar_punctuation']:
                    f.write(f"\nGrammar/Punctuation Errors:\n")
                    for i, error in enumerate(page['errors']['grammar_punctuation'], 1):
                        f.write(f"  {i}. {error['message']}\n")
                        f.write(f"     Context: {error['context']}\n")
                        if error['suggestions']:
                            f.write(f"     Suggestions: {', '.join(error['suggestions'])}\n")
                        f.write(f"\n")
                
                # Mathematical errors
                if page['errors']['mathematical']:
                    f.write(f"\nMathematical Errors:\n")
                    for i, error in enumerate(page['errors']['mathematical'], 1):
                        f.write(f"  {i}. {error['message']}\n")
                        f.write(f"     Context: {error['context']}\n")
                        f.write(f"     Severity: {error['severity']}\n")
                        f.write(f"\n")
    
    print(f"Summary saved to: {summary_path}")


def scan_directory(directory: str, output_dir: str = 'error_reports', enable_grammar: bool = True):
    """
    Scan all PDF files in a directory.
    
    Args:
        directory: Directory containing PDF files
        output_dir: Directory to save error reports
        enable_grammar: Whether to enable grammar checking
    """
    pdf_files = list(Path(directory).glob('*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to scan\n")
    
    for pdf_file in pdf_files:
        scan_pdf(str(pdf_file), output_dir, enable_grammar)
        print()


def main():
    """Main entry point for the PDF error scanner."""
    parser = argparse.ArgumentParser(
        description='Scan PDF files for grammar, punctuation, and mathematical errors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single PDF file
  python scanner.py book.pdf
  
  # Scan all PDFs in a directory
  python scanner.py --directory ./books
  
  # Scan with custom output directory
  python scanner.py book.pdf --output ./my_reports
        """
    )
    
    parser.add_argument(
        'pdf',
        nargs='?',
        help='Path to PDF file to scan'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='Directory containing PDF files to scan'
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
    
    args = parser.parse_args()
    
    # Check if we have either a file or directory
    if not args.pdf and not args.directory:
        parser.print_help()
        sys.exit(1)
    
    try:
        enable_grammar = not args.no_grammar
        
        if args.directory:
            scan_directory(args.directory, args.output, enable_grammar)
        else:
            if not os.path.exists(args.pdf):
                print(f"Error: File '{args.pdf}' not found")
                sys.exit(1)
            scan_pdf(args.pdf, args.output, enable_grammar)
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
