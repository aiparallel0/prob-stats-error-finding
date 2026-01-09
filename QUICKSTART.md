# Quick Start Guide

This guide will help you get started with the PDF error detection system.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aiparallel0/prob-stats-error-finding.git
   cd prob-stats-error-finding
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Place your PDF files:**
   ```bash
   # Copy your probability and statistics books to the books/ directory
   cp /path/to/your/book.pdf books/
   ```

## Usage Examples

### Scan a single PDF file

```bash
python scanner.py books/your_book.pdf
```

### Scan all PDFs in the books directory

```bash
python scanner.py --directory books
```

### Scan without grammar checking (faster, works offline)

```bash
python scanner.py books/your_book.pdf --no-grammar
```

### Specify custom output directory

```bash
python scanner.py books/your_book.pdf --output my_custom_reports
```

## Understanding the Output

After scanning, you'll find two types of reports in the `error_reports/` directory:

1. **JSON Report** (`*_errors_*.json`):
   - Complete machine-readable data
   - Contains all error details
   - Can be processed programmatically

2. **Text Summary** (`*_summary_*.txt`):
   - Human-readable format
   - Shows errors organized by page
   - Includes error messages, context, and suggestions

### Example Output Structure

```
error_reports/
├── probability_theory_errors_20260109_120000.json
└── probability_theory_summary_20260109_120000.txt
```

## Types of Errors Detected

### 1. Grammar and Punctuation Errors
- Article usage (a vs an)
- Spacing issues
- Common spelling mistakes
- Punctuation placement

### 2. Mathematical Errors
- Unmatched parentheses `()`
- Unmatched brackets `[]`
- Unmatched braces `{}`
- Mathematical error keywords (undefined, NaN, division by zero, etc.)
- Double operators (`++`, `--`, etc.)

## Tips

- For large PDFs, use `--no-grammar` flag for faster scanning
- Check the text summary first for a quick overview
- Use the JSON report for automated processing or further analysis
- The scanner processes each page independently, so you can identify exactly where errors occur

## Troubleshooting

### "No PDF files found"
- Make sure your PDF files are in the specified directory
- Check that files have the `.pdf` extension

### Grammar checking not working
- The system will automatically fall back to pattern-based checking if LanguageTool is unavailable
- Use `--no-grammar` flag to skip grammar checking entirely

### PDF text extraction issues
- Some PDFs with complex formatting or scanned images may not extract text properly
- Consider converting scanned PDFs to text-searchable PDFs first

## Next Steps

1. Place your probability and statistics textbooks in the `books/` directory
2. Run the scanner on your PDFs
3. Review the generated reports
4. Fix the identified errors in your source documents

For more information, see the main [README.md](README.md) file.
