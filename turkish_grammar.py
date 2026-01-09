"""
Turkish grammar and spelling checker for detecting Turkish-specific errors.
"""
import re
from typing import List, Dict, Any, Optional


class TurkishGrammarChecker:
    """Check for Turkish-specific grammar, spelling, and punctuation errors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Turkish grammar checker.
        
        Args:
            config: Optional configuration dictionary with Turkish rules
        """
        self.config = config or {}
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default Turkish grammar rules."""
        # Common Turkish spelling errors
        self.spelling_errors = {
            'adalandırılan': 'adlandırılan',
            'gosterilmiştir': 'gösterilmiştir',
            'gostermektedir': 'göstermektedir',
            'olsuturur': 'oluşturur',
        }
        
        # Turkish-specific patterns
        self.turkish_patterns = [
            {
                'pattern': r'adalandırılan',
                'correction': 'adlandırılan',
                'message': 'Turkish spelling error: missing "d" in "adlandırılan"',
                'severity': 'high'
            },
            {
                'pattern': r'\bolabilir\s+farklı',
                'correction': 'olası farklı',
                'message': 'Inconsistent terminology: use "olası" instead of "olabilir" for consistency',
                'severity': 'medium'
            },
            {
                'pattern': r'\bN\s+is\b',
                'correction': 'N ise',
                'message': 'Mixed language: "is" should be Turkish "ise"',
                'severity': 'high'
            },
            {
                'pattern': r',([A-Za-zÇĞİÖŞÜçğıöşü])',
                'correction': lambda m: ', ' + m.group(1),
                'message': 'Missing space after comma (Turkish punctuation rule)',
                'severity': 'medium'
            },
            {
                'pattern': r';([A-Za-zÇĞİÖŞÜçğıöşü])',
                'correction': lambda m: '; ' + m.group(1),
                'message': 'Missing space after semicolon (Turkish punctuation rule)',
                'severity': 'medium'
            },
            {
                'pattern': r':([A-Za-zÇĞİÖŞÜçğıöşü])',
                'correction': lambda m: ': ' + m.group(1),
                'message': 'Missing space after colon (Turkish punctuation rule)',
                'severity': 'medium'
            },
        ]
        
        # Broken reference patterns
        self.reference_patterns = [
            {
                'pattern': r'Örnek\s+\?\?',
                'message': 'Broken example reference',
                'severity': 'high'
            },
            {
                'pattern': r'Şekil\s+\?\?',
                'message': 'Broken figure reference',
                'severity': 'high'
            },
            {
                'pattern': r'Tablo\s+\?\?',
                'message': 'Broken table reference',
                'severity': 'high'
            },
            {
                'pattern': r'Bölüm\s+\?\?',
                'message': 'Broken section reference',
                'severity': 'high'
            },
        ]
    
    def check_spelling(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for Turkish spelling errors.
        
        Args:
            text: Text to check
            
        Returns:
            List of spelling errors found
        """
        errors = []
        
        for misspelling, correction in self.spelling_errors.items():
            pattern = re.compile(r'\b' + misspelling + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = text[start:end]
                
                errors.append({
                    'type': 'turkish_spelling',
                    'message': f'Turkish spelling error: "{match.group()}" should be "{correction}"',
                    'context': f'...{context}...',
                    'offset': match.start(),
                    'length': match.end() - match.start(),
                    'suggestions': [correction],
                    'severity': 'high'
                })
        
        return errors
    
    def check_comma_spacing(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for missing spaces after commas in Turkish text.
        
        Args:
            text: Text to check
            
        Returns:
            List of comma spacing errors found
        """
        errors = []
        
        # Pattern for comma followed by letter without space
        pattern = re.compile(r',([A-Za-zÇĞİÖŞÜçğıöşü])')
        
        for match in pattern.finditer(text):
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            errors.append({
                'type': 'turkish_punctuation',
                'message': 'Missing space after comma (Turkish punctuation rule)',
                'context': f'...{context}...',
                'offset': match.start(),
                'length': match.end() - match.start(),
                'suggestions': [', ' + match.group(1)],
                'severity': 'medium'
            })
        
        return errors
    
    def check_turkish_patterns(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for Turkish-specific grammar patterns.
        
        Args:
            text: Text to check
            
        Returns:
            List of pattern-based errors found
        """
        errors = []
        
        for rule in self.turkish_patterns:
            pattern = re.compile(rule['pattern'])
            
            for match in pattern.finditer(text):
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = text[start:end]
                
                # Get correction
                if callable(rule.get('correction')):
                    correction = rule['correction'](match)
                else:
                    correction = rule.get('correction', '')
                
                errors.append({
                    'type': 'turkish_grammar',
                    'message': rule['message'],
                    'context': f'...{context}...',
                    'offset': match.start(),
                    'length': match.end() - match.start(),
                    'suggestions': [correction] if correction else [],
                    'severity': rule.get('severity', 'medium')
                })
        
        return errors
    
    def check_broken_references(self, text: str) -> List[Dict[str, Any]]:
        """
        Check for broken references (e.g., "Örnek ??").
        
        Args:
            text: Text to check
            
        Returns:
            List of broken references found
        """
        errors = []
        
        for rule in self.reference_patterns:
            pattern = re.compile(rule['pattern'])
            
            for match in pattern.finditer(text):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                
                errors.append({
                    'type': 'broken_reference',
                    'message': rule['message'],
                    'context': f'...{context}...',
                    'offset': match.start(),
                    'length': match.end() - match.start(),
                    'suggestions': [],
                    'severity': rule.get('severity', 'high')
                })
        
        return errors
    
    def check_all(self, text: str) -> List[Dict[str, Any]]:
        """
        Run all Turkish grammar checks.
        
        Args:
            text: Text to check
            
        Returns:
            List of all Turkish-specific errors found
        """
        errors = []
        
        errors.extend(self.check_spelling(text))
        errors.extend(self.check_comma_spacing(text))
        errors.extend(self.check_turkish_patterns(text))
        errors.extend(self.check_broken_references(text))
        
        return errors
