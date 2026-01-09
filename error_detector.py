"""
Error detection module for finding grammar, punctuation, and mathematical errors in text.
"""
import re
from typing import List, Dict, Any, Optional


class ErrorDetector:
    """Detect various types of errors in text."""
    
    def __init__(self, enable_grammar_check: bool = True, enable_turkish: bool = True, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the error detector with language tools.
        
        Args:
            enable_grammar_check: Whether to enable grammar checking (requires internet on first run)
            enable_turkish: Whether to enable Turkish-specific checks
            config: Optional configuration dictionary
        """
        self.grammar_enabled = False
        self.language_tool = None
        self.simple_grammar = None
        self.turkish_checker = None
        self.config = config or {}
        
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
        
        # Initialize Turkish grammar checker
        if enable_turkish:
            try:
                from turkish_grammar import TurkishGrammarChecker
                self.turkish_checker = TurkishGrammarChecker(config.get('turkish_rules', {}))
                print("Turkish grammar checker enabled")
            except Exception as e:
                print(f"Warning: Turkish grammar checking disabled. Error: {e}")
        
        # Common mathematical error indicators
        self.math_error_keywords = [
            'undefined',
            'infinity',
            'division by zero',
            'NaN',
            'error',
        ]
    
    def check_grammar_punctuation(self, text: str) -> List[Dict[str, Any]]:
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
    
    def check_mathematical_errors(self, text: str) -> List[Dict[str, Any]]:
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
        
        # Check for wrong union/intersection symbols (A∪B = ∅ should be A∩B = ∅)
        wrong_union = re.finditer(r'([A-Z])∪([A-Z])\s*=\s*[∅{}]', text)
        for match in wrong_union:
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end]
            
            errors.append({
                'type': 'mathematical',
                'message': f'Wrong symbol: "{match.group()}" - Union (∪) with empty set suggests intersection (∩) should be used',
                'context': f'...{context}...',
                'severity': 'high',
                'suggestions': [match.group().replace('∪', '∩')]
            })
        
        # Check for split equation numbers (equation number split across lines)
        split_equation = re.finditer(r'=\s*\(\d+\.?\d*$', text, re.MULTILINE)
        for match in split_equation:
            start = max(0, match.start() - 30)
            end = min(len(text), match.end())
            context = text[start:end]
            
            errors.append({
                'type': 'mathematical',
                'message': 'Equation number appears to be split across lines',
                'context': f'...{context}',
                'severity': 'medium'
            })
        
        # Check for inconsistent equation numbering format
        # Look for patterns like "B = (1.8" where equation number is incomplete
        incomplete_eq = re.finditer(r'[A-Z]\s*=\s*\(\d+\.\d*$', text, re.MULTILINE)
        for match in incomplete_eq:
            start = max(0, match.start() - 20)
            end = min(len(text), match.end())
            context = text[start:end]
            
            errors.append({
                'type': 'mathematical',
                'message': 'Incomplete equation or split equation number',
                'context': f'...{context}',
                'severity': 'high'
            })
        
        return errors
    
    def check_turkish_errors(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for Turkish-specific errors.
        
        Args:
            text: Text to check
            
        Returns:
            List of Turkish-specific errors
        """
        errors = []
        
        if self.turkish_checker:
            try:
                errors = self.turkish_checker.check_all(text)
            except Exception as e:
                print(f"Error during Turkish grammar check: {e}")
        
        return errors
    
    def check_spacing_errors(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for inconsistent spacing and extra content.
        
        Args:
            text: Text to check
            
        Returns:
            List of spacing errors
        """
        errors = []
        
        if not text:
            return errors
        
        # Check for extra space and number between words (e.g., "Problemler 2 252")
        extra_content = re.finditer(r'([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d+)\s+(\d+)', text)
        for match in extra_content:
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end]
            
            errors.append({
                'type': 'spacing',
                'message': f'Extra space and number detected: "{match.group()}"',
                'context': f'...{context}...',
                'offset': match.start(),
                'severity': 'medium'
            })
        
        return errors
    
    def check_all_errors(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check for all types of errors.
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary containing all detected errors by type
        """
        return {
            'grammar_punctuation': self.check_grammar_punctuation(text),
            'mathematical': self.check_mathematical_errors(text),
            'turkish': self.check_turkish_errors(text),
            'spacing': self.check_spacing_errors(text)
        }
    
    def close(self):
        """Clean up resources."""
        try:
            if self.language_tool:
                self.language_tool.close()
        except (AttributeError, Exception):
            pass
