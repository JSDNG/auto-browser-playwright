"""
Formatters for output formatting and data cleaning.
"""

import re
import json
from typing import Any, Dict, List, Union, Optional
from datetime import datetime
from html import unescape


class OutputFormatter:
    """Formatter for output data."""
    
    @classmethod
    def format_json_output(cls, data: Dict[str, Any]) -> str:
        """Format data as compact JSON string."""
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    
    @classmethod
    def format_pretty_json(cls, data: Dict[str, Any]) -> str:
        """Format data as pretty JSON string."""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @classmethod
    def format_timestamp(cls, timestamp: datetime) -> str:
        """Format timestamp as ISO string."""
        return timestamp.isoformat() + "Z"
    
    @classmethod
    def format_execution_time(cls, seconds: float) -> str:
        """Format execution time as human-readable string."""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
    
    @classmethod
    def format_file_size(cls, size_bytes: int) -> str:
        """Format file size as human-readable string."""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f}KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / (1024**2):.1f}MB"
        else:
            return f"{size_bytes / (1024**3):.1f}GB"
    
    @classmethod
    def format_url(cls, url: str) -> str:
        """Format URL for display."""
        if not url:
            return ""
        
        # Remove trailing slash
        if url.endswith('/'):
            url = url[:-1]
        
        # Ensure protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @classmethod
    def format_error_message(cls, error: str, error_type: Optional[str] = None) -> str:
        """Format error message."""
        if not error:
            return ""
        
        # Clean error message
        error = cls._clean_error_message(error)
        
        # Add error type prefix if provided
        if error_type:
            error = f"[{error_type.upper()}] {error}"
        
        return error
    
    @classmethod
    def _clean_error_message(cls, error: str) -> str:
        """Clean error message from sensitive information."""
        # Remove file paths
        error = re.sub(r'[A-Za-z]:\\[^\\]*\\[^\\]*\\[^\\]*', '[PATH]', error)
        error = re.sub(r'/[^/]*/[^/]*/[^/]*', '[PATH]', error)
        
        # Remove URLs with credentials
        error = re.sub(r'https?://[^:]+:[^@]+@[^/]+', 'https://[CREDENTIALS]@[HOST]', error)
        
        # Remove stack traces
        error = re.sub(r'Traceback \(most recent call last\):.*$', '[STACK_TRACE]', error, flags=re.DOTALL)
        
        return error


class DataCleaner:
    """Data cleaner for extracted content."""
    
    @classmethod
    def clean_text(cls, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Decode HTML entities
        text = unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Remove zero-width characters
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\u200c', '')  # Zero-width non-joiner
        text = text.replace('\u200d', '')  # Zero-width joiner
        text = text.replace('\u2060', '')  # Word joiner
        text = text.replace('\ufeff', '')  # Byte order mark
        
        # Convert non-breaking spaces
        text = text.replace('\u00a0', ' ')
        
        return text.strip()
    
    @classmethod
    def clean_url(cls, url: str) -> str:
        """Clean and normalize URL."""
        if not url:
            return ""
        
        # Remove whitespace
        url = url.strip()
        
        # Remove fragment
        if '#' in url:
            url = url.split('#')[0]
        
        # Decode URL entities
        url = unescape(url)
        
        return url
    
    @classmethod
    def clean_attribute_value(cls, value: str) -> str:
        """Clean HTML attribute value."""
        if not value:
            return ""
        
        # Decode HTML entities
        value = unescape(value)
        
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        
        return value.strip()
    
    @classmethod
    def clean_list_data(cls, data: List[Any]) -> List[Any]:
        """Clean list data by removing empty/null values."""
        cleaned = []
        for item in data:
            if item is not None:
                if isinstance(item, str):
                    cleaned_item = cls.clean_text(item)
                    if cleaned_item:
                        cleaned.append(cleaned_item)
                elif isinstance(item, dict):
                    cleaned_item = cls.clean_dict_data(item)
                    if cleaned_item:
                        cleaned.append(cleaned_item)
                else:
                    cleaned.append(item)
        return cleaned
    
    @classmethod
    def clean_dict_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean dictionary data by removing empty/null values."""
        cleaned = {}
        for key, value in data.items():
            if value is not None:
                if isinstance(value, str):
                    cleaned_value = cls.clean_text(value)
                    if cleaned_value:
                        cleaned[key] = cleaned_value
                elif isinstance(value, list):
                    cleaned_value = cls.clean_list_data(value)
                    if cleaned_value:
                        cleaned[key] = cleaned_value
                elif isinstance(value, dict):
                    cleaned_value = cls.clean_dict_data(value)
                    if cleaned_value:
                        cleaned[key] = cleaned_value
                else:
                    cleaned[key] = value
        return cleaned
    
    @classmethod
    def normalize_data(cls, data: Any) -> Any:
        """Normalize data structure."""
        if isinstance(data, str):
            return cls.clean_text(data)
        elif isinstance(data, list):
            return cls.clean_list_data(data)
        elif isinstance(data, dict):
            return cls.clean_dict_data(data)
        else:
            return data
    
    @classmethod
    def extract_numbers(cls, text: str) -> List[float]:
        """Extract numbers from text."""
        if not text:
            return []
        
        # Find all number patterns
        number_pattern = r'-?\d+(?:\.\d+)?'
        matches = re.findall(number_pattern, text)
        
        numbers = []
        for match in matches:
            try:
                if '.' in match:
                    numbers.append(float(match))
                else:
                    numbers.append(int(match))
            except ValueError:
                continue
        
        return numbers
    
    @classmethod
    def extract_emails(cls, text: str) -> List[str]:
        """Extract email addresses from text."""
        if not text:
            return []
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        
        return list(set(matches))  # Remove duplicates
    
    @classmethod
    def extract_phone_numbers(cls, text: str) -> List[str]:
        """Extract phone numbers from text."""
        if not text:
            return []
        
        # Various phone number patterns
        phone_patterns = [
            r'\+\d{1,3}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{4}[-.\s]?\d{4}'
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        return list(set(phones))  # Remove duplicates
    
    @classmethod
    def extract_urls(cls, text: str) -> List[str]:
        """Extract URLs from text."""
        if not text:
            return []
        
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'
        matches = re.findall(url_pattern, text)
        
        return list(set(matches))  # Remove duplicates
    
    @classmethod
    def truncate_text(cls, text: str, max_length: int = 100) -> str:
        """Truncate text to specified length."""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + '...'
    
    @classmethod
    def format_table_data(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format table data for better display."""
        if not data:
            return []
        
        formatted = []
        for row in data:
            formatted_row = {}
            for key, value in row.items():
                if isinstance(value, str):
                    formatted_row[key] = cls.clean_text(value)
                else:
                    formatted_row[key] = value
            formatted.append(formatted_row)
        
        return formatted 