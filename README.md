# prob-stats-error-finding

A repository to find errors in a uni project in probability and statistics books. Any error is counted, whether grammar punctuation or mathematical.

## Features

- 📄 **PDF Text Extraction**: Extracts text from PDF files page by page
- ✍️ **Grammar & Punctuation Checking**: Detects grammar and punctuation errors using LanguageTool
- 🔢 **Mathematical Error Detection**: Identifies mathematical notation errors, unmatched parentheses/brackets/braces, and potential calculation errors
- 📊 **Detailed Reports**: Generates comprehensive JSON and human-readable text reports
- 🔍 **Page-by-Page Analysis**: Scans each page individually for precise error location

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aiparallel0/prob-stats-error-finding.git
cd prob-stats-error-finding
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Download the LanguageTool model (required for grammar checking):
```bash
# This happens automatically on first run
# Or you can pre-download it manually
python -c "import language_tool_python; language_tool_python.LanguageTool('en-US')"
```

## Usage

### Scan a single PDF file

```bash
python scanner.py book.pdf
```

### Scan all PDF files in a directory

```bash
python scanner.py --directory ./books
```

### Specify custom output directory for reports

```bash
python scanner.py book.pdf --output ./my_reports
```

### Get help

```bash
python scanner.py --help
```

## Directory Structure

```
prob-stats-error-finding/
├── books/              # Place your PDF files here
├── error_reports/      # Generated error reports (created automatically)
├── scanner.py          # Main scanning script
├── pdf_extractor.py    # PDF text extraction module
├── error_detector.py   # Error detection module
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Error Types Detected

### Grammar & Punctuation Errors
- Spelling mistakes
- Grammar errors
- Punctuation issues
- Style suggestions
- And more via LanguageTool

### Mathematical Errors
- Unmatched parentheses `()`
- Unmatched brackets `[]`
- Unmatched braces `{}`
- Double operators (`++`, `--`, etc.)
- Error keywords (undefined, NaN, division by zero, etc.)

## Output Reports

The scanner generates two types of reports in the `error_reports/` directory:

1. **JSON Report** (`*_errors_*.json`): Complete machine-readable error data
2. **Text Summary** (`*_summary_*.txt`): Human-readable summary with error details

### Example Output

```
============================================================
Scanning PDF: books/probability_theory.pdf
============================================================

Total pages: 150

Scanning page 1...
  Found 3 error(s)
    - Grammar/Punctuation: 2
    - Mathematical: 1

Scanning page 2...
  Found 0 error(s)
    - Grammar/Punctuation: 0
    - Mathematical: 0

...

============================================================
Scan Complete!
Total errors found: 42
============================================================

Report saved to: error_reports/probability_theory_errors_20260109_120000.json
Summary saved to: error_reports/probability_theory_summary_20260109_120000.txt
```

## Adding PDF Files

Place your probability and statistics PDF books in the `books/` directory:

```bash
cp your_book.pdf books/
```

Then scan them:

```bash
python scanner.py --directory books
```

## Requirements

- Python 3.7+
- pdfplumber
- PyPDF2
- language-tool-python
- LanguageTool Java backend (downloaded automatically)

## Contributing

Feel free to contribute by:
- Adding more error detection rules
- Improving mathematical error detection
- Adding support for more file formats
- Enhancing the reporting system

## License

This project is for educational purposes.
