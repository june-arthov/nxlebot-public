#!/usr/bin/env python3
"""
Caveman Compressor - Nxlebot + Julius Brussee
Compress text to caveman speak
"""

import re
from typing import List

class CavemanCompressor:
    """Compress text to ultra-efficient caveman speak"""
    
    # Filler words to remove
    FILLER_WORDS = [
        'i', "i'd", "i'm", 'me', 'my', 'myself',
        'the', 'a', 'an', 'this', 'that', 'these', 'those',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might',
        'please', 'kindly', 'just', 'simply', 'basically',
        'actually', 'really', 'very', 'quite', 'rather',
        'sure', 'certainly', 'definitely', 'absolutely',
        'probably', 'likely', 'maybe', 'perhaps',
        'so', 'then', 'thus', 'therefore', 'hence',
        'also', 'too', 'as well', 'additionally',
        'first', 'second', 'third', 'next', 'finally',
        'however', 'although', 'though', 'but', 'yet',
        'because', 'since', 'as', 'due to', 'owing to',
        'for example', 'for instance', 'such as', 'like',
        'in order to', 'so as to', 'with the aim of',
        'it is', 'there is', 'there are', 'this is',
        'i think', 'i believe', 'in my opinion',
        'you know', 'i mean', 'basically', 'literally',
    ]
    
    # Phrase replacements
    REPLACEMENTS = {
        'i would be happy to help': '',
        'i can help you with that': 'help:',
        'let me know if you need': 'need?',
        'please let me know': 'tell me',
        'i recommend': 'use',
        'you should': 'do',
        'you could': 'try',
        'it is recommended to': 'do',
        'it would be best to': 'do',
        'in order to': 'to',
        'so that you can': 'to',
        'with the purpose of': 'to',
        'for the purpose of': 'for',
        'due to the fact that': 'because',
        'in spite of the fact that': 'although',
        'regardless of the fact that': 'although',
        'at this point in time': 'now',
        'in the near future': 'soon',
        'in the event that': 'if',
        'under the circumstances': 'so',
        'in light of the fact that': 'because',
        'with regard to': 'about',
        'in relation to': 'about',
        'in connection with': 'about',
        'for the reason that': 'because',
        'on the grounds that': 'because',
        'owing to the fact that': 'because',
        'in view of the fact that': 'because',
        'i am writing to': '',
        'i am contacting you to': '',
        'i wanted to reach out': '',
        'i wanted to let you know': '',
        'i wanted to check in': '',
        'i hope this email finds you well': '',
        'i hope you are doing well': '',
        'thank you for your time': 'thanks',
        'thank you in advance': 'thanks',
        'i appreciate your help': 'thanks',
        'thanks so much': 'thanks',
        'thank you very much': 'thanks',
        'many thanks': 'thanks',
        'thanks a lot': 'thanks',
        'i look forward to': 'wait for',
        'looking forward to': 'wait for',
        'i am looking forward to': 'wait for',
        'please feel free to': '',
        'do not hesitate to': '',
        'if you have any questions': 'questions?',
        'if you need anything else': 'need more?',
        'let me know if you have any questions': 'questions?',
        'please do not hesitate to contact me': 'contact me',
        'i am happy to help': 'help:',
        'i would be glad to': '',
        'i am pleased to': '',
        'i am delighted to': '',
        'i am excited to': '',
        'i am thrilled to': '',
        'i am eager to': '',
        'i am ready to': 'ready:',
        'i am prepared to': 'ready:',
        'i am available to': 'can:',
        'i am able to': 'can:',
        'i can assist you with': 'help:',
        'i can help you with': 'help:',
        'i would like to': 'want:',
        'i want to': 'want:',
        'i need to': 'need:',
        'i have to': 'must:',
        'i must': 'must:',
        'i should': 'should:',
        'i will': 'will:',
        'i shall': 'will:',
        'i may': 'may:',
        'i might': 'might:',
        'i can': 'can:',
        'i could': 'could:',
        'i would': 'would:',
    }
    
    def __init__(self, level: str = "full"):
        self.level = level  # lite, full, ultra
    
    def remove_filler(self, text: str) -> str:
        """Remove filler words"""
        words = text.lower().split()
        filtered = [w for w in words if w.strip('.,!?;:"') not in self.FILLER_WORDS]
        return ' '.join(filtered)
    
    def replace_phrases(self, text: str) -> str:
        """Replace verbose phrases"""
        text_lower = text.lower()
        for phrase, replacement in self.REPLACEMENTS.items():
            text_lower = text_lower.replace(phrase, replacement)
        return text_lower
    
    def simplify_grammar(self, text: str) -> str:
        """Simplify to caveman grammar"""
        # Remove articles
        text = re.sub(r'\b(a|an|the)\b', '', text)
        
        # Simplify verbs
        text = re.sub(r'\b(is|are|was|were)\b', '=', text)
        text = re.sub(r'\b(has|have|had)\b', 'got', text)
        text = re.sub(r'\b(will|would)\b', 'will', text)
        
        # Remove helper verbs
        text = re.sub(r'\b(do|does|did)\b', '', text)
        
        # Simplify pronouns
        text = re.sub(r'\b(you are|youre)\b', 'you', text)
        text = re.sub(r'\b(it is|its)\b', 'it', text)
        text = re.sub(r'\b(they are|theyre)\b', 'they', text)
        
        return text
    
    def ultra_compress(self, text: str) -> str:
        """Ultra compression - symbols only"""
        # Replace common words with symbols
        replacements = {
            'and': '&',
            'or': '|',
            'not': '!',
            'equals': '=',
            'is': '=',
            'to': '→',
            'from': '←',
            'with': '+',
            'without': '-',
            'in': '∈',
            'out': '∉',
            'up': '↑',
            'down': '↓',
            'yes': '✓',
            'no': '✗',
            'good': '👍',
            'bad': '👎',
            'error': '⚠',
            'warning': '⚡',
            'success': '✅',
            'fail': '❌',
        }
        
        for word, symbol in replacements.items():
            text = re.sub(r'\b' + word + r'\b', symbol, text, flags=re.IGNORECASE)
        
        return text
    
    def compress(self, text: str) -> str:
        """Main compression method"""
        if self.level == "lite":
            text = self.replace_phrases(text)
            text = self.remove_filler(text)
            return text.strip()
        
        elif self.level == "full":
            text = self.replace_phrases(text)
            text = self.remove_filler(text)
            text = self.simplify_grammar(text)
            # Clean up extra spaces
            text = ' '.join(text.split())
            return text.strip()
        
        elif self.level == "ultra":
            text = self.replace_phrases(text)
            text = self.remove_filler(text)
            text = self.simplify_grammar(text)
            text = self.ultra_compress(text)
            text = ' '.join(text.split())
            return text.strip()
        
        return text


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Caveman Compressor')
    parser.add_argument('text', nargs='?', help='Text to compress')
    parser.add_argument('-l', '--level', choices=['lite', 'full', 'ultra'], 
                       default='full', help='Compression level')
    parser.add_argument('-f', '--file', help='File to compress')
    
    args = parser.parse_args()
    
    compressor = CavemanCompressor(args.level)
    
    if args.file:
        with open(args.file, 'r') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        # Demo
        text = "I would be happy to help you with that. The issue you're experiencing is most likely caused by your authentication middleware not properly validating the token expiry. Let me take a look and suggest a fix."
    
    original_tokens = len(text.split())
    compressed = compressor.compress(text)
    compressed_tokens = len(compressed.split())
    
    print(f"Original ({original_tokens} tokens):")
    print(f"  {text}")
    print()
    print(f"Caveman ({compressed_tokens} tokens, {100-(compressed_tokens/original_tokens*100):.0f}% saved):")
    print(f"  {compressed}")


if __name__ == '__main__':
    main()
