#!/usr/bin/env python3
"""
Analyze text files directly without PDF processing.
Generates comprehensive reports in multiple formats.
"""
import os
import sys
import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from text_analyzer import TextAnalyzer


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    try:
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            print(f"Warning: Config file '{config_path}' not found. Using defaults.")
            return {}
    except Exception as e:
        print(f"Warning: Could not load config: {e}. Using defaults.")
        return {}


def analyze_text_file(file_path: str, output_dir: str = 'error_reports', 
                      enable_grammar: bool = True, config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Analyze a text file for errors.
    
    Args:
        file_path: Path to the text file
        output_dir: Directory to save error reports
        enable_grammar: Whether to enable grammar checking
        config_path: Path to configuration file
        
    Returns:
        Dictionary containing analysis results
    """
    print(f"\n{'='*60}")
    print(f"Analyzing Text File: {file_path}")
    print(f"{'='*60}\n")
    
    # Load configuration
    config = load_config(config_path)
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"Error: File '{file_path}' not found")
        return None
    
    # Initialize analyzer
    analyzer = TextAnalyzer(
        enable_grammar=enable_grammar,
        enable_turkish=config.get('error_types', {}).get('enable_turkish_specific', True),
        config=config
    )
    
    try:
        # Analyze file
        print("Analyzing file...")
        results = analyzer.analyze_file(file_path)
        
        # Add metadata
        results['analysis_date'] = datetime.now().isoformat()
        results['config_used'] = config_path
        
        print(f"\n{'='*60}")
        print(f"Analysis Complete!")
        print(f"{'='*60}")
        print(f"Total lines: {results['total_lines']}")
        print(f"Lines with errors: {len(results['lines_with_errors'])}")
        print(f"Total errors: {results['total_errors']}")
        print(f"\nError Summary:")
        print(f"  - Grammar/Punctuation: {results['error_summary']['grammar_punctuation']}")
        print(f"  - Mathematical: {results['error_summary']['mathematical']}")
        print(f"  - Turkish-specific: {results['error_summary']['turkish']}")
        print(f"  - Spacing: {results['error_summary']['spacing']}")
        print(f"{'='*60}\n")
        
        # Save reports
        save_reports(results, output_dir, config)
        
        return results
        
    finally:
        analyzer.close()


def save_reports(results: Dict[str, Any], output_dir: str, config: Dict[str, Any]):
    """
    Save error reports in multiple formats.
    
    Args:
        results: Analysis results dictionary
        output_dir: Directory to save the reports
        config: Configuration dictionary
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename base
    file_name = Path(results['file_path']).stem
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Get export formats from config
    export_formats = config.get('reporting', {}).get('export_formats', ['json', 'markdown'])
    
    # Save JSON report
    if 'json' in export_formats:
        json_filename = f"{file_name}_errors_{timestamp}.json"
        json_path = Path(output_dir) / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"JSON report saved to: {json_path}")
    
    # Save Markdown report
    if 'markdown' in export_formats:
        md_filename = f"{file_name}_errors_{timestamp}.md"
        md_path = Path(output_dir) / md_filename
        
        generate_markdown_report(results, md_path)
        print(f"Markdown report saved to: {md_path}")
    
    # Save HTML report
    if 'html' in export_formats:
        html_filename = f"{file_name}_errors_{timestamp}.html"
        html_path = Path(output_dir) / html_filename
        
        generate_html_report(results, html_path)
        print(f"HTML report saved to: {html_path}")


def generate_markdown_report(results: Dict[str, Any], output_path: Path):
    """
    Generate a Markdown format error report.
    
    Args:
        results: Analysis results dictionary
        output_path: Path to save the Markdown report
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Error Detection Report\n\n")
        f.write(f"**File:** {results.get('file_path', 'N/A')}\n\n")
        f.write(f"**Analysis Date:** {results.get('analysis_date', 'N/A')}\n\n")
        f.write(f"**Total Lines:** {results['total_lines']}\n\n")
        f.write(f"**Lines with Errors:** {len(results['lines_with_errors'])}\n\n")
        f.write(f"**Total Errors:** {results['total_errors']}\n\n")
        
        f.write(f"## Error Summary\n\n")
        f.write(f"| Error Type | Count |\n")
        f.write(f"|------------|-------|\n")
        f.write(f"| Grammar/Punctuation | {results['error_summary']['grammar_punctuation']} |\n")
        f.write(f"| Mathematical | {results['error_summary']['mathematical']} |\n")
        f.write(f"| Turkish-specific | {results['error_summary']['turkish']} |\n")
        f.write(f"| Spacing | {results['error_summary']['spacing']} |\n\n")
        
        f.write(f"## Detailed Errors\n\n")
        
        for line_data in results['lines_with_errors']:
            line_num = line_data['line_number']
            line_text = line_data['text']
            
            f.write(f"### Line {line_num}\n\n")
            f.write(f"```\n{line_text}\n```\n\n")
            
            # Grammar/Punctuation errors
            if line_data['errors'].get('grammar_punctuation'):
                f.write(f"#### Grammar/Punctuation Errors\n\n")
                for i, error in enumerate(line_data['errors']['grammar_punctuation'], 1):
                    f.write(f"{i}. **{error['message']}**\n")
                    f.write(f"   - Context: `{error['context']}`\n")
                    if error.get('suggestions'):
                        f.write(f"   - Suggestions: {', '.join(error['suggestions'])}\n")
                    f.write(f"\n")
            
            # Mathematical errors
            if line_data['errors'].get('mathematical'):
                f.write(f"#### Mathematical Errors\n\n")
                for i, error in enumerate(line_data['errors']['mathematical'], 1):
                    f.write(f"{i}. **{error['message']}**\n")
                    f.write(f"   - Context: `{error['context']}`\n")
                    f.write(f"   - Severity: {error.get('severity', 'N/A')}\n")
                    if error.get('suggestions'):
                        f.write(f"   - Suggestions: {', '.join(error['suggestions'])}\n")
                    f.write(f"\n")
            
            # Turkish-specific errors
            if line_data['errors'].get('turkish'):
                f.write(f"#### Turkish-specific Errors\n\n")
                for i, error in enumerate(line_data['errors']['turkish'], 1):
                    f.write(f"{i}. **{error['message']}**\n")
                    f.write(f"   - Context: `{error['context']}`\n")
                    f.write(f"   - Severity: {error.get('severity', 'N/A')}\n")
                    if error.get('suggestions'):
                        f.write(f"   - Suggestions: {', '.join(error['suggestions'])}\n")
                    f.write(f"\n")
            
            # Spacing errors
            if line_data['errors'].get('spacing'):
                f.write(f"#### Spacing Errors\n\n")
                for i, error in enumerate(line_data['errors']['spacing'], 1):
                    f.write(f"{i}. **{error['message']}**\n")
                    f.write(f"   - Context: `{error['context']}`\n")
                    f.write(f"   - Severity: {error.get('severity', 'N/A')}\n")
                    f.write(f"\n")


def generate_html_report(results: Dict[str, Any], output_path: Path):
    """
    Generate an HTML format error report.
    
    Args:
        results: Analysis results dictionary
        output_path: Path to save the HTML report
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error Detection Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .metadata {{
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary {{
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .summary th, .summary td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .summary th {{
            background-color: #4CAF50;
            color: white;
        }}
        .error-line {{
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .line-number {{
            font-weight: bold;
            color: #4CAF50;
            font-size: 1.2em;
        }}
        .line-text {{
            background-color: #f9f9f9;
            padding: 10px;
            border-left: 3px solid #4CAF50;
            margin: 10px 0;
            font-family: monospace;
            white-space: pre-wrap;
        }}
        .error-item {{
            margin: 10px 0;
            padding: 10px;
            border-left: 3px solid #ff9800;
            background-color: #fff8f0;
        }}
        .error-type {{
            font-weight: bold;
            color: #d84315;
            margin-bottom: 10px;
        }}
        .error-message {{
            font-weight: bold;
            color: #555;
        }}
        .context {{
            color: #666;
            font-family: monospace;
            font-size: 0.9em;
        }}
        .severity-high {{
            border-left-color: #d32f2f;
        }}
        .severity-medium {{
            border-left-color: #ff9800;
        }}
        .severity-low {{
            border-left-color: #ffc107;
        }}
    </style>
</head>
<body>
    <h1>Error Detection Report</h1>
    
    <div class="metadata">
        <p><strong>File:</strong> {results.get('file_path', 'N/A')}</p>
        <p><strong>Analysis Date:</strong> {results.get('analysis_date', 'N/A')}</p>
        <p><strong>Total Lines:</strong> {results['total_lines']}</p>
        <p><strong>Lines with Errors:</strong> {len(results['lines_with_errors'])}</p>
        <p><strong>Total Errors:</strong> {results['total_errors']}</p>
    </div>
    
    <div class="summary">
        <h2>Error Summary</h2>
        <table>
            <tr>
                <th>Error Type</th>
                <th>Count</th>
            </tr>
            <tr>
                <td>Grammar/Punctuation</td>
                <td>{results['error_summary']['grammar_punctuation']}</td>
            </tr>
            <tr>
                <td>Mathematical</td>
                <td>{results['error_summary']['mathematical']}</td>
            </tr>
            <tr>
                <td>Turkish-specific</td>
                <td>{results['error_summary']['turkish']}</td>
            </tr>
            <tr>
                <td>Spacing</td>
                <td>{results['error_summary']['spacing']}</td>
            </tr>
        </table>
    </div>
    
    <h2>Detailed Errors</h2>
""")
        
        for line_data in results['lines_with_errors']:
            line_num = line_data['line_number']
            line_text = line_data['text']
            
            f.write(f"""
    <div class="error-line">
        <div class="line-number">Line {line_num}</div>
        <div class="line-text">{line_text}</div>
""")
            
            # All error types
            for error_type, errors in line_data['errors'].items():
                if errors:
                    type_name = error_type.replace('_', ' ').title()
                    f.write(f'        <div class="error-type">{type_name} Errors</div>\n')
                    
                    for error in errors:
                        severity = error.get('severity', 'medium')
                        f.write(f'        <div class="error-item severity-{severity}">\n')
                        f.write(f'            <div class="error-message">{error["message"]}</div>\n')
                        f.write(f'            <div class="context">Context: {error.get("context", "N/A")}</div>\n')
                        
                        if error.get('suggestions'):
                            f.write(f'            <div>Suggestions: {", ".join(error["suggestions"])}</div>\n')
                        
                        f.write(f'        </div>\n')
            
            f.write(f'    </div>\n')
        
        f.write("""
</body>
</html>
""")


def main():
    """Main entry point for the text file analyzer."""
    parser = argparse.ArgumentParser(
        description='Analyze text files for grammar, punctuation, mathematical, and Turkish-specific errors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a text file
  python analyze_text_file.py "Olasılık Çözümlü Sorular.txt"
  
  # Analyze with custom output directory
  python analyze_text_file.py text.txt --output ./my_reports
  
  # Analyze without grammar checking (faster)
  python analyze_text_file.py text.txt --no-grammar
  
  # Use custom config file
  python analyze_text_file.py text.txt --config custom_config.yaml
        """
    )
    
    parser.add_argument(
        'file',
        help='Path to text file to analyze'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='error_reports',
        help='Output directory for error reports (default: error_reports)'
    )
    
    parser.add_argument(
        '--no-grammar',
        action='store_true',
        help='Disable grammar checking (useful for offline mode or faster analysis)'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        enable_grammar = not args.no_grammar
        analyze_text_file(args.file, args.output, enable_grammar, args.config)
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
