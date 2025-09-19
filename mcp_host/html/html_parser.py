#!/usr/bin/env python3

"""
HTML Code Extraction Module

Provides functionality to extract code blocks from HTML files, particularly
from notebook exports that contain code in <pre class="language"><code> format.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup


class HTMLCodeExtractor:
    """Extract code blocks from HTML files."""
    
    def __init__(self):
        """Initialize the HTML code extractor."""
        pass
    
    def extract_code_blocks(self, html_content: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract code blocks from HTML content.
        
        Args:
            html_content: The HTML content as a string
            language: Optional language filter (e.g., 'r', 'python', 'sql')
        
        Returns:
            List of dictionaries containing code blocks with metadata
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        code_blocks = []
        
        # Find all <pre> tags that contain <code> tags
        pre_tags = soup.find_all('pre')
        
        for i, pre_tag in enumerate(pre_tags):
            # Check if this pre tag has a class attribute that indicates language
            pre_classes = pre_tag.get('class', [])
            detected_language = None
            
            # Look for language indicators in class names
            for cls in pre_classes:
                if cls in ['r', 'python', 'sql', 'bash', 'javascript', 'css', 'html']:
                    detected_language = cls
                    break
            
            # Find code tag within pre tag
            code_tag = pre_tag.find('code')
            if code_tag:
                code_content = code_tag.get_text()
                
                # If no language detected from pre tag, check code tag classes
                if not detected_language:
                    code_classes = code_tag.get('class', [])
                    for cls in code_classes:
                        if cls in ['r', 'python', 'sql', 'bash', 'javascript', 'css', 'html']:
                            detected_language = cls
                            break
                        # Handle class patterns like 'language-r', 'lang-python', etc.
                        if cls.startswith('language-'):
                            detected_language = cls.replace('language-', '')
                            break
                        if cls.startswith('lang-'):
                            detected_language = cls.replace('lang-', '')
                            break
                
                # If still no language detected, try to infer from content
                if not detected_language:
                    detected_language = self._infer_language_from_content(code_content)
                
                # Filter by language if specified
                if language is None or (detected_language and detected_language.lower() == language.lower()):
                    code_blocks.append({
                        'index': i,
                        'language': detected_language or 'unknown',
                        'code': code_content.strip(),
                        'raw_html': str(pre_tag)
                    })
        
        return code_blocks
    
    def _infer_language_from_content(self, code_content: str) -> Optional[str]:
        """
        Try to infer the programming language from code content.
        
        Args:
            code_content: The code content as string
            
        Returns:
            Inferred language or None
        """
        code_lower = code_content.lower().strip()
        
        # SQL patterns (check first as they're more specific)
        if any(pattern in code_lower for pattern in [
            'select ', 'from ', 'where ', 'insert ', 'update ', 'delete ', 'create table', 'alter table'
        ]):
            return 'sql'
        
        # R language patterns
        if any(pattern in code_lower for pattern in [
            'library(', 'require(', '<-', 'data.frame', 'read.csv', 'ggplot'
        ]):
            return 'r'
        
        # Python patterns
        if any(pattern in code_lower for pattern in [
            'import ', 'from ', 'def ', 'print(', 'pandas', 'numpy'
        ]):
            return 'python'
        
        # Bash patterns
        if any(pattern in code_lower for pattern in [
            '#!/bin/bash', 'echo ', 'cd ', 'ls ', 'grep '
        ]):
            return 'bash'
        
        return None
    
    def extract_from_file(self, file_path: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract code blocks from an HTML file.
        
        Args:
            file_path: Path to the HTML file
            language: Optional language filter
            
        Returns:
            List of code blocks with metadata
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"HTML file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(path, 'r', encoding='latin-1') as f:
                html_content = f.read()
        
        return self.extract_code_blocks(html_content, language)
    
    def combine_code_blocks(self, code_blocks: List[Dict[str, Any]], separator: str = "\n\n") -> str:
        """
        Combine multiple code blocks into a single string.
        
        Args:
            code_blocks: List of code block dictionaries
            separator: String to use between code blocks
            
        Returns:
            Combined code as a single string
        """
        if not code_blocks:
            return ""
        
        combined_code = separator.join([block['code'] for block in code_blocks])
        return combined_code
    
    def get_code_summary(self, code_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get a summary of extracted code blocks.
        
        Args:
            code_blocks: List of code block dictionaries
            
        Returns:
            Summary dictionary with statistics
        """
        if not code_blocks:
            return {
                'total_blocks': 0,
                'languages': {},
                'total_lines': 0,
                'total_characters': 0
            }
        
        languages = {}
        total_lines = 0
        total_characters = 0
        
        for block in code_blocks:
            lang = block['language']
            if lang not in languages:
                languages[lang] = 0
            languages[lang] += 1
            
            lines = len(block['code'].split('\n'))
            total_lines += lines
            total_characters += len(block['code'])
        
        return {
            'total_blocks': len(code_blocks),
            'languages': languages,
            'total_lines': total_lines,
            'total_characters': total_characters
        }
