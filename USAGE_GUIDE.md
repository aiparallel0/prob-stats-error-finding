# Usage Guide - Enhanced Error Detection Tools

This comprehensive guide explains how to use the enhanced error detection tools with Turkish language support and advanced mathematical error detection.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Analyzing Text Files](#analyzing-text-files)
- [Analyzing PDF Files](#analyzing-pdf-files)
- [Understanding Error Reports](#understanding-error-reports)
- [Error Types Detected](#error-types-detected)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/aiparallel0/prob-stats-error-finding.git
cd prob-stats-error-finding

# Install required packages
pip install -r requirements.txt
```

### Dependencies Installed
- `PyPDF2` - PDF processing
- `pdfplumber` - PDF text extraction
- `language-tool-python` - Grammar checking (downloads LanguageTool on first run)
- `pyyaml` - Configuration file support
- `tqdm` - Progress bars

## Quick Start

### Analyze a Text File
```bash
python analyze_text_file.py "Olasılık Çözümlü Sorular.txt"
```

### Analyze a PDF File
```bash
python scanner.py "document.pdf"
```

### Use Enhanced Scanner with Text Files
```bash
python scanner.py "document.txt" --text
```

## Configuration

The tool uses `config.yaml` for customizable error detection. You can modify this file to enable/disable specific error types and customize detection rules.

### Configuration Options

```yaml
# Enable/disable error types
error_types:
  enable_grammar: true              # General grammar checking
  enable_punctuation: true          # Punctuation errors
  enable_mathematical: true         # Mathematical notation errors
  enable_turkish_specific: true    # Turkish language-specific errors

# Turkish-specific rules
turkish_rules:
  check_comma_spacing: true         # Check for missing spaces after commas
  check_spelling: true              # Check Turkish spelling
  check_word_errors: true           # Check common Turkish word errors
  
  # Add custom error patterns
  common_errors:
    - pattern: "adalandırılan"
      correction: "adlandırılan"
      description: "Missing 'd' in Turkish word"

# Mathematical error detection
mathematical_rules:
  check_unmatched_brackets: true    # Check for unmatched brackets/parentheses
  check_notation_errors: true       # Check mathematical notation
  check_split_equations: true       # Check for split equation numbers

# Report generation
reporting:
  include_line_numbers: true        # Include line numbers in reports
  include_context_lines: 2          # Number of context lines
  export_formats:                   # Export formats
    - json
    - markdown
    - html
```

## Analyzing Text Files

### Using analyze_text_file.py (Recommended for Text Files)

This script is specifically designed for analyzing text files line by line.

#### Basic Usage
```bash
python analyze_text_file.py "your_file.txt"
```

#### With Custom Output Directory
```bash
python analyze_text_file.py "your_file.txt" --output ./my_reports
```

#### Without Grammar Checking (Faster, Offline Mode)
```bash
python analyze_text_file.py "your_file.txt" --no-grammar
```

#### With Custom Configuration
```bash
python analyze_text_file.py "your_file.txt" --config custom_config.yaml
```

### Using scanner.py for Text Files

```bash
# Scan a single text file
python scanner.py "document.txt" --text

# Scan all text files in a directory
python scanner.py --directory ./texts --text

# With custom output
python scanner.py "document.txt" --text --output ./reports
```

## Analyzing PDF Files

### Scan a Single PDF
```bash
python scanner.py "document.pdf"
```

### Scan Multiple PDFs
```bash
# Scan all PDFs in the books directory
python scanner.py --directory ./books

# With custom output directory
python scanner.py --directory ./books --output ./pdf_reports
```

### Disable Grammar Checking (Faster)
```bash
python scanner.py "document.pdf" --no-grammar
```

## Understanding Error Reports

The tools generate reports in multiple formats:

### 1. JSON Report (`*_errors_*.json`)
- Machine-readable format
- Complete error data
- Suitable for programmatic processing
- Includes all error details, contexts, and suggestions

### 2. Markdown Report (`*_errors_*.md`)
- Human-readable format
- Well-formatted with headers and tables
- Easy to view in GitHub or text editors
- Includes error summary and detailed breakdown

### 3. HTML Report (`*_errors_*.html`)
- Visual, web-based format
- Color-coded severity levels
- Styled for easy reading
- Can be opened in any web browser

### 4. Text Summary (`*_summary_*.txt`)
- Simple text format
- Quick overview of errors
- Easy to read in any text editor

## Error Types Detected

### 1. Grammar and Punctuation Errors
- Article usage (a vs an)
- Spacing issues
- Common spelling mistakes
- Punctuation placement

### 2. Mathematical Errors
- **Unmatched Brackets**: Detects unmatched `()`, `[]`, `{}`
- **Wrong Symbols**: Identifies incorrect use of union (∪) vs intersection (∩)
  - Example: `A∪B = ∅` should be `A∩B = ∅`
- **Split Equations**: Finds equation numbers split across lines
- **Double Operators**: Detects `++`, `--`, etc.
- **Error Keywords**: Finds terms like "undefined", "NaN", "division by zero"

### 3. Turkish-Specific Errors
- **Spelling Errors**:
  - `adalandırılan` → `adlandırılan` (missing 'd')
- **Comma Spacing**: Missing space after comma in Turkish
  - Example: `deneyler,toplam` → `deneyler, toplam`
- **Terminology Consistency**:
  - `olabilir farklı` → `olası farklı`
- **Mixed Language**:
  - `N is` → `N ise` (English vs Turkish)
- **Broken References**:
  - `Örnek ??` (broken example reference)
  - `Şekil ??` (broken figure reference)
  - `Tablo ??` (broken table reference)

### 4. Spacing Errors
- Multiple consecutive spaces
- Extra numbers between words
- Inconsistent spacing patterns

## Examples

### Example 1: Quick Text File Analysis
```bash
python analyze_text_file.py "Olasılık Çözümlü Sorular.txt"
```

Output:
```
============================================================
Analyzing Text File: Olasılık Çözümlü Sorular.txt
============================================================

Analyzing file...

============================================================
Analysis Complete!
============================================================
Total lines: 29557
Lines with errors: 523
Total errors: 892

Error Summary:
  - Grammar/Punctuation: 234
  - Mathematical: 145
  - Turkish-specific: 389
  - Spacing: 124
============================================================

JSON report saved to: error_reports/Olasılık_Çözümlü_Sorular_errors_20260109_120000.json
Markdown report saved to: error_reports/Olasılık_Çözümlü_Sorular_errors_20260109_120000.md
HTML report saved to: error_reports/Olasılık_Çözümlü_Sorular_errors_20260109_120000.html
```

### Example 2: PDF Analysis with Progress Bar
```bash
python scanner.py "textbook.pdf"
```

Output with tqdm installed:
```
============================================================
Scanning PDF: textbook.pdf
============================================================

Total pages: 150

Scanning pages: 100%|████████████████| 150/150 [02:34<00:00,  1.03s/it]

============================================================
Scan Complete!
Total errors found: 245
============================================================

Report saved to: error_reports/textbook_errors_20260109_120000.json
Summary saved to: error_reports/textbook_summary_20260109_120000.txt
```

### Example 3: Batch Processing
```bash
# Process all text files in a directory
python scanner.py --directory ./documents --text --output ./results
```

### Example 4: Offline Mode (No Grammar Checking)
```bash
# Faster analysis without internet-dependent grammar checking
python analyze_text_file.py "document.txt" --no-grammar
```

## Specific Errors Addressed

Based on the Turkish text analysis, the tool detects:

| Line | Error Type | Description |
|------|------------|-------------|
| 148 | Spacing | Extra space/number "2" between words: "Problemler 2 252" |
| 220 | Turkish Punctuation | Missing space after comma: "deneyler,toplam" |
| 264 | Turkish Spelling | "adalandırılan" → "adlandırılan" |
| 370 | Turkish Terminology | "olabilir farklı" → "olası farklı" |
| 531 | Mixed Language | "N is" → "N ise" |
| 579 | Broken Reference | "Örnek ??" |
| 662 | Mathematical | Wrong symbol: "A∪B = ∅" → "A∩B = ∅" |
| 799 | Mathematical | Split equation number: "B = (1.8" |

## Troubleshooting

### Issue: "LanguageTool unavailable"
**Solution**: This is not critical. The tool automatically falls back to pattern-based checking. To fix:
```bash
pip install --upgrade language-tool-python
```

### Issue: "tqdm not available"
**Solution**: Install tqdm for progress bars:
```bash
pip install tqdm
```

### Issue: "Config file not found"
**Solution**: The tool works without a config file using defaults. To use custom config:
1. Ensure `config.yaml` is in the same directory
2. Or specify config path: `--config /path/to/config.yaml`

### Issue: "Empty or unreadable file"
**Solution**: 
- Check file encoding (should be UTF-8)
- Verify file is not corrupted
- For PDFs, ensure text is not in image format

### Issue: Large files take too long
**Solution**: Use `--no-grammar` flag to disable grammar checking:
```bash
python analyze_text_file.py large_file.txt --no-grammar
```

### Issue: Too many false positives
**Solution**: Customize detection rules in `config.yaml`:
- Disable specific error types
- Adjust severity thresholds
- Add exceptions for domain-specific terms

## Advanced Usage

### Custom Error Patterns

Edit `config.yaml` to add custom patterns:

```yaml
turkish_rules:
  common_errors:
    - pattern: "your_pattern"
      correction: "correct_form"
      description: "Description of the error"
```

### Programmatic Usage

```python
from text_analyzer import TextAnalyzer

# Initialize analyzer
analyzer = TextAnalyzer(enable_grammar=True, enable_turkish=True)

# Analyze file
results = analyzer.analyze_file("document.txt")

# Access results
print(f"Total errors: {results['total_errors']}")
for line_data in results['lines_with_errors']:
    print(f"Line {line_data['line_number']}: {line_data['error_count']} errors")

# Clean up
analyzer.close()
```

### Custom Reporting

```python
from analyze_text_file import load_config, generate_markdown_report
import json

# Load results
with open('error_reports/document_errors_*.json', 'r') as f:
    results = json.load(f)

# Generate custom report
generate_markdown_report(results, 'custom_report.md')
```

## Best Practices

1. **Start with a sample**: Test on a small file first to understand the output
2. **Review config.yaml**: Customize detection rules for your use case
3. **Use appropriate format**: 
   - JSON for programmatic processing
   - Markdown for GitHub/documentation
   - HTML for visual review
4. **Offline mode**: Use `--no-grammar` for faster processing when internet is unavailable
5. **Batch processing**: Process multiple files at once using directory scanning
6. **Regular updates**: Keep dependencies updated for best results

## Support and Contribution

- Report issues: [GitHub Issues](https://github.com/aiparallel0/prob-stats-error-finding/issues)
- Contribute: Fork the repository and submit pull requests
- Documentation: Check README.md and QUICKSTART.md

## License

This project is for educational purposes.
