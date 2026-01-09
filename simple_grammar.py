"""
Simple offline grammar and spelling checker using pattern matching.
"""
import re
from typing import List, Dict


class SimpleGrammarChecker:
    """Simple grammar checker using pattern matching rules."""
    
    def __init__(self):
        """Initialize the grammar checker with rules."""
        # Common grammar patterns
        self.grammar_rules = [
            {
                'pattern': r'\ba\s+[aeiou]',  # "a" before vowel
                'message': 'Use "an" before words starting with a vowel sound',
                'suggestion': lambda m: m.group().replace('a ', 'an ')
            },
            {
                'pattern': r'\ban\s+[^aeiou]',  # "an" before consonant
                'message': 'Use "a" before words starting with a consonant sound',
                'suggestion': lambda m: m.group().replace('an ', 'a ')
            },
            {
                'pattern': r'\s{2,}',  # Multiple spaces
                'message': 'Multiple consecutive spaces found',
                'suggestion': lambda m: ' '
            },
            {
                'pattern': r'[,;:]\S',  # Missing space after punctuation
                'message': 'Missing space after punctuation',
                'suggestion': lambda m: m.group()[0] + ' ' + m.group()[1]
            },
            {
                'pattern': r'\s[,;:.]',  # Space before punctuation
                'message': 'Unexpected space before punctuation',
                'suggestion': lambda m: m.group().strip()
            },
        ]
        
        # Common spelling mistakes (small list)
        self.common_misspellings = {
            'recieve': 'receive',
            'occured': 'occurred',
            'seperate': 'separate',
            'untill': 'until',
            'occurance': 'occurrence',
            'acheive': 'achieve',
            'beleive': 'believe',
            'begining': 'beginning',
            'occuring': 'occurring',
            'teh': 'the',
            'adn': 'and',
            'taht': 'that',
        }
    
    def check(self, text: str) -> List[Dict[str, any]]:
        """
        Check text for grammar and spelling errors.
        
        Args:
            text: Text to check
            
        Returns:
            List of detected errors with details
        """
        errors = []
        
        if not text:
            return errors
        
        # Check grammar rules
        for rule in self.grammar_rules:
            pattern = re.compile(rule['pattern'], re.IGNORECASE)
            for match in pattern.finditer(text):
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end]
                
                try:
                    suggestion = rule['suggestion'](match)
                except:
                    suggestion = ''
                
                errors.append({
                    'type': 'grammar/punctuation',
                    'message': rule['message'],
                    'context': f'...{context}...',
                    'offset': match.start(),
                    'length': match.end() - match.start(),
                    'suggestions': [suggestion] if suggestion else [],
                    'rule': 'simple_grammar'
                })
        
        # Check spelling
        words = re.findall(r'\b\w+\b', text.lower())
        for misspelling, correction in self.common_misspellings.items():
            if misspelling in words:
                # Find position in text
                pattern = re.compile(r'\b' + misspelling + r'\b', re.IGNORECASE)
                for match in pattern.finditer(text):
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    context = text[start:end]
                    
                    errors.append({
                        'type': 'grammar/punctuation',
                        'message': f'Possible spelling mistake: "{match.group()}"',
                        'context': f'...{context}...',
                        'offset': match.start(),
                        'length': match.end() - match.start(),
                        'suggestions': [correction],
                        'rule': 'spelling'
                    })
        
        return errors
