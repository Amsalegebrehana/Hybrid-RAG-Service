# .md, .txt files read raw content
# type: FileLoader
import re
from abc import abstractmethod
from dataclasses import dataclass

from markdown_it import MarkdownIt

@dataclass  
class File:
    source: str
    content: bytes

class FileLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self) -> File:
        with open(self.file_path, 'rb') as f:
            print(f"Loading file: {self.file_path}")
            return File(
                source=self.file_path,
                content=f.read()
            )
    
    
class Cleaner:
    def __init__(self, content: bytes):
        self.content = content
    @abstractmethod
    def clean(self) -> str:
        pass 

class MDFileCleaner(Cleaner):

    def clean(self) -> str:
        text = self._normalize(self.content)
        text = self._strip_front_matter(text)
        blocks = self._extract_blocks(text)
        return self._join_blocks(blocks)

    def _normalize(self, content: bytes) -> str:
        text = content.decode('utf-8').lstrip('﻿')
        return text.replace('\r\n', '\n').replace('\r', '\n')

    def _strip_front_matter(self, text: str) -> str:
        return re.sub(r'\A---\n.*?\n---[ \t]*(?:\n|\Z)', '', text, count=1, flags=re.DOTALL)

    def _extract_blocks(self, text: str) -> list[str]:
        blocks = []
        for token in MarkdownIt().enable('table').parse(text):
            if token.type == 'inline':
                blocks.append(self._inline_to_text(token))
            elif token.type in ('fence', 'code_block'):
                blocks.append(token.content.rstrip('\n'))
        return blocks

    def _inline_to_text(self, token) -> str:
        parts = []
        for child in token.children or []:
            if child.type in ('text', 'code_inline'):
                parts.append(child.content)
            elif child.type == 'softbreak':
                parts.append(' ')
            elif child.type == 'hardbreak':
                parts.append('\n')
        return ''.join(parts)

    def _join_blocks(self, blocks: list[str]) -> str:
        return '\n\n'.join(b.strip() for b in blocks if b.strip())


class TXTFileCleaner(Cleaner):

    def clean(self) -> str:
        # Implement text-specific cleaning logic here
        cleaned_content = self.content.decode('utf-8').strip()  #  strip whitespace
        return cleaned_content
        
            