"""
Error detection module for finding grammar, punctuation, and mathematical errors in text.
"""
import re
from typing import List, Dict, Set


class ErrorDetector:
    """Detect various types of errors in text."""
    
    def __init__(self, enable_grammar_check: bool = True):
        """
        Initialize the error detector with language tools.
        
        Args:
            enable_grammar_check: Whether to enable grammar checking (requires internet on first run)
        """
        self.grammar_enabled = False
        self.language_tool = None
        self.simple_grammar = None
        
        if enable_grammar_check:
            try:
                import language_tool_python
                self.language_tool = language_tool_python.LanguageTool('en-US')
                self.grammar_enabled = True
                print("Using LanguageTool for grammar checking")
            except Exception as e:
                # Fall back to simple grammar checker
                try:
                    from simple_grammar import SimpleGrammarChecker
                    self.simple_grammar = SimpleGrammarChecker()
                    self.grammar_enabled = True
                    print("Using simple pattern-based grammar checker (LanguageTool unavailable)")
                except Exception as e2:
                    print(f"Warning: Grammar checking disabled. Error: {e}")
                    print("The scanner will continue with mathematical error detection only.")
                    self.grammar_enabled = False
        
        # Common mathematical symbols and patterns
        self.math_patterns = {
            'unmatched_parentheses': r'\([^()]*(?:\([^()]*\)[^()]*)*[^)]*$|^[^(]*\)',
            'double_operators': r'[\+\-\*/]{2,}',
            'malformed_fraction': r'\\frac(?!\{)',
            'unmatched_brackets': r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*[^\]]*$|^[^\[]*\]',
            'unmatched_braces': r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*[^}]*$|^[^{]*\}',
        }
        
        # Common mathematical error indicators
        self.math_error_keywords = [
            'undefined',
            'infinity',
            'division by zero',
            'NaN',
            'error',
        ]
    
    def check_grammar_punctuation(self, text: str) -> List[Dict[str, any]]:
        """
        Check for grammar and punctuation errors.
        
        Args:
            text: Text to check
            
        Returns:
            List of detected errors with details
        """
        errors = []
        
        if not self.grammar_enabled:
            return errors
        
        if not text or not text.strip():
            return errors
        
        try:
            if self.language_tool:
                # Use LanguageTool
                matches = self.language_tool.check(text)
                
                for match in matches:
                    errors.append({
                        'type': 'grammar/punctuation',
                        'message': match.message,
                        'context': match.context,
                        'offset': match.offset,
                        'length': match.errorLength,
                        'suggestions': match.replacements[:3],  # Top 3 suggestions
                        'rule': match.ruleId
                    })
            elif self.simple_grammar:
                # Use simple grammar checker
                errors = self.simple_grammar.check(text)
        except Exception as e:
            print(f"Error during grammar check: {e}")
        
        return errors
    
    def check_mathematical_errors(self, text: str) -> List[Dict[str, any]]:
        """
        Check for mathematical notation errors and inconsistencies.
        
        Args:
            text: Text to check
            
        Returns:
            List of detected mathematical errors
        """
        errors = []
        
        if not text:
            return errors
        
        # Check for unmatched parentheses
        paren_count = text.count('(') - text.count(')')
        if paren_count != 0:
            errors.append({
                'type': 'mathematical',
                'message': f'Unmatched parentheses: {abs(paren_count)} {"opening" if paren_count > 0 else "closing"} parenthesis/es',
                'context': 'Full text',
                'severity': 'high'
            })
        
        # Check for unmatched brackets
        bracket_count = text.count('[') - text.count(']')
        if bracket_count != 0:
            errors.append({
                'type': 'mathematical',
                'message': f'Unmatched brackets: {abs(bracket_count)} {"opening" if bracket_count > 0 else "closing"} bracket(s)',
                'context': 'Full text',
                'severity': 'high'
            })
        
        # Check for unmatched braces
        brace_count = text.count('{') - text.count('}')
        if brace_count != 0:
            errors.append({
                'type': 'mathematical',
                'message': f'Unmatched braces: {abs(brace_count)} {"opening" if brace_count > 0 else "closing"} brace(s)',
                'context': 'Full text',
                'severity': 'high'
            })
        
        # Check for common mathematical error keywords
        text_lower = text.lower()
        for keyword in self.math_error_keywords:
            if keyword in text_lower:
                # Find the context around the keyword
                idx = text_lower.index(keyword)
                start = max(0, idx - 30)
                end = min(len(text), idx + len(keyword) + 30)
                context = text[start:end]
                
                errors.append({
                    'type': 'mathematical',
                    'message': f'Potential mathematical error: "{keyword}" found',
                    'context': f'...{context}...',
                    'severity': 'medium'
                })
        
        # Check for double operators (e.g., ++, --, etc.)
        double_ops = re.finditer(r'[\+\-\*/]{2,}', text)
        for match in double_ops:
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end]
            
            errors.append({
                'type': 'mathematical',
                'message': f'Double operator detected: "{match.group()}"',
                'context': f'...{context}...',
                'severity': 'medium'
            })
        
        return errors
    
    def check_all_errors(self, text: str) -> Dict[str, List[Dict[str, any]]]:
        """
        Check for all types of errors.
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary containing all detected errors by type
        """
        return {
            'grammar_punctuation': self.check_grammar_punctuation(text),
            'mathematical': self.check_mathematical_errors(text)
        }
    
    def close(self):
        """Clean up resources."""
        try:
            if self.language_tool:
                self.language_tool.close()
        except:
            pass
