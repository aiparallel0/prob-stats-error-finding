"""
Text analyzer module for analyzing text files line by line.
Tracks line numbers for precise error reporting.
"""
import re
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from error_detector import ErrorDetector


class TextAnalyzer:
    """Analyze text files line by line for errors."""
    
    def __init__(self, enable_grammar: bool = True, enable_turkish: bool = True, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the text analyzer.
        
        Args:
            enable_grammar: Whether to enable grammar checking
            enable_turkish: Whether to enable Turkish-specific checks
            config: Optional configuration dictionary
        """
        self.detector = ErrorDetector(enable_grammar_check=enable_grammar, enable_turkish=enable_turkish, config=config)
        self.config = config or {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a text file line by line.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary containing analysis results with line numbers
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = {
            'file_path': file_path,
            'total_lines': len(lines),
            'lines_with_errors': [],
            'error_summary': {
                'grammar_punctuation': 0,
                'mathematical': 0,
                'turkish': 0,
                'spacing': 0
            },
            'total_errors': 0
        }
        
        # Analyze each line
        for line_num, line in enumerate(lines, start=1):
            line_text = line.rstrip('\n')
            
            if not line_text.strip():
                continue
            
            # Detect errors in this line
            errors = self.detector.check_all_errors(line_text)
            
            # Count errors
            line_error_count = sum(len(errs) for errs in errors.values())
            
            if line_error_count > 0:
                results['lines_with_errors'].append({
                    'line_number': line_num,
                    'text': line_text,
                    'errors': errors,
                    'error_count': line_error_count
                })
                
                # Update summary
                results['error_summary']['grammar_punctuation'] += len(errors.get('grammar_punctuation', []))
                results['error_summary']['mathematical'] += len(errors.get('mathematical', []))
                results['error_summary']['turkish'] += len(errors.get('turkish', []))
                results['error_summary']['spacing'] += len(errors.get('spacing', []))
                results['total_errors'] += line_error_count
        
        return results
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content directly.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        lines = text.split('\n')
        
        results = {
            'total_lines': len(lines),
            'lines_with_errors': [],
            'error_summary': {
                'grammar_punctuation': 0,
                'mathematical': 0,
                'turkish': 0,
                'spacing': 0
            },
            'total_errors': 0
        }
        
        # Analyze each line
        for line_num, line in enumerate(lines, start=1):
            line_text = line.rstrip('\n')
            
            if not line_text.strip():
                continue
            
            # Detect errors in this line
            errors = self.detector.check_all_errors(line_text)
            
            # Count errors
            line_error_count = sum(len(errs) for errs in errors.values())
            
            if line_error_count > 0:
                results['lines_with_errors'].append({
                    'line_number': line_num,
                    'text': line_text,
                    'errors': errors,
                    'error_count': line_error_count
                })
                
                # Update summary
                results['error_summary']['grammar_punctuation'] += len(errors.get('grammar_punctuation', []))
                results['error_summary']['mathematical'] += len(errors.get('mathematical', []))
                results['error_summary']['turkish'] += len(errors.get('turkish', []))
                results['error_summary']['spacing'] += len(errors.get('spacing', []))
                results['total_errors'] += line_error_count
        
        return results
    
    def get_line_context(self, lines: List[str], line_num: int, context_lines: int = 2) -> Tuple[int, int, List[str]]:
        """
        Get context lines around a specific line.
        
        Args:
            lines: List of all lines
            line_num: Target line number (1-indexed)
            context_lines: Number of lines to include before and after
            
        Returns:
            Tuple of (start_line, end_line, context_lines)
        """
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        
        return start + 1, end, lines[start:end]
    
    def close(self):
        """Clean up resources."""
        self.detector.close()
