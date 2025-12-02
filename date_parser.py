"""
Date Parser - Extracts and normalizes dates from text
"""
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
import dateparser


class DateParser:
    """Extract and normalize dates from text"""
    
    # Date patterns
    DATE_PATTERNS = [
        # DD/MM/YYYY, DD-MM-YYYY
        r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',
        
        # DD Month YYYY
        r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
        
        # Month DD, YYYY
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b',
        
        # DD/MM/YY, DD-MM-YY (two-digit year)
        r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2})\b',
    ]
    
    # Context patterns for specific date types
    CONTEXT_PATTERNS = {
        'incorporation': [
            r'date of incorporation[:\s]+([^\n]{5,30})',
            r'incorporated on[:\s]+([^\n]{5,30})',
            r'incorporation date[:\s]+([^\n]{5,30})',
        ],
        'name_change': [
            r'date of change[:\s]+([^\n]{5,30})',
            r'changed (?:its name )?on[:\s]+([^\n]{5,30})',
            r'effective (?:date|from)[:\s]+([^\n]{5,30})',
        ],
        'registration': [
            r'date of registration[:\s]+([^\n]{5,30})',
            r'registered on[:\s]+([^\n]{5,30})',
        ],
        'filing': [
            r'filed on[:\s]+([^\n]{5,30})',
            r'filing date[:\s]+([^\n]{5,30})',
        ]
    }
    
    def extract_dates(self, text: str, context: Optional[str] = None) -> List[datetime]:
        """
        Extract dates from text
        
        Args:
            text: Text to search
            context: Document context (incorporation, name_change, etc.)
            
        Returns:
            List of datetime objects
        """
        dates = []
        
        # Try context-specific patterns first
        if context and context in self.CONTEXT_PATTERNS:
            context_dates = self._extract_with_context(text, context)
            dates.extend(context_dates)
        
        # Extract all dates using patterns
        all_dates = self._extract_all_dates(text)
        dates.extend(all_dates)
        
        # Remove duplicates and sort
        unique_dates = list(set(dates))
        unique_dates.sort()
        
        return unique_dates
    
    def _extract_with_context(self, text: str, context: str) -> List[datetime]:
        """
        Extract dates using context-specific patterns
        
        Args:
            text: Text to search
            context: Document context
            
        Returns:
            List of datetime objects
        """
        dates = []
        
        patterns = self.CONTEXT_PATTERNS.get(context, [])
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(1).strip()
                parsed_date = self.parse_date(date_str)
                if parsed_date:
                    dates.append(parsed_date)
        
        return dates
    
    def _extract_all_dates(self, text: str) -> List[datetime]:
        """
        Extract all dates from text using regex patterns
        
        Args:
            text: Text to search
            
        Returns:
            List of datetime objects
        """
        dates = []
        
        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0)
                parsed_date = self.parse_date(date_str)
                if parsed_date:
                    dates.append(parsed_date)
        
        return dates
    
    def parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse a date string into datetime object
        
        Args:
            date_string: Date string to parse
            
        Returns:
            datetime object or None if parsing fails
        """
        try:
            # Try dateparser (handles many formats)
            parsed = dateparser.parse(
                date_string,
                settings={
                    'STRICT_PARSING': False,
                    'PREFER_DAY_OF_MONTH': 'first',
                    'DATE_ORDER': 'DMY'  # UK format
                }
            )
            
            if parsed:
                # Validate reasonable date range (1800-2100)
                if 1800 <= parsed.year <= 2100:
                    return parsed
            
        except Exception as e:
            pass
        
        return None
    
    def extract_date_ranges(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract date ranges (e.g., "from 01/01/2020 to 31/12/2020")
        
        Args:
            text: Text to search
            
        Returns:
            List of dictionaries with start_date and end_date
        """
        ranges = []
        
        # Pattern: "from DATE to DATE"
        pattern = r'from\s+([^\s]+(?:\s+\w+\s+\d{4})?)\s+to\s+([^\s]+(?:\s+\w+\s+\d{4})?)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            start_str = match.group(1).strip()
            end_str = match.group(2).strip()
            
            start_date = self.parse_date(start_str)
            end_date = self.parse_date(end_str)
            
            if start_date and end_date:
                ranges.append({
                    'start_date': start_date,
                    'end_date': end_date,
                    'text': match.group(0)
                })
        
        return ranges
    
    def compare_dates(self, date1: datetime, date2: datetime, 
                     tolerance_days: int = 0) -> bool:
        """
        Compare two dates with optional tolerance
        
        Args:
            date1: First date
            date2: Second date
            tolerance_days: Allowed difference in days
            
        Returns:
            True if dates match within tolerance
        """
        if tolerance_days == 0:
            return date1.date() == date2.date()
        
        diff = abs((date1 - date2).days)
        return diff <= tolerance_days
    
    def format_date(self, date: datetime, format_type: str = 'uk') -> str:
        """
        Format date according to specified format
        
        Args:
            date: datetime object
            format_type: 'uk', 'us', 'iso', or custom format string
            
        Returns:
            Formatted date string
        """
        formats = {
            'uk': '%d/%m/%Y',
            'us': '%m/%d/%Y',
            'iso': '%Y-%m-%d',
            'long': '%d %B %Y',
        }
        
        format_str = formats.get(format_type, format_type)
        return date.strftime(format_str)
    
    def extract_incorporation_date(self, text: str) -> Optional[datetime]:
        """
        Specifically extract incorporation date from document
        
        Args:
            text: Document text
            
        Returns:
            Incorporation date or None
        """
        dates = self._extract_with_context(text, 'incorporation')
        return dates[0] if dates else None
    
    def extract_name_change_date(self, text: str) -> Optional[datetime]:
        """
        Specifically extract name change date from document
        
        Args:
            text: Document text
            
        Returns:
            Name change date or None
        """
        dates = self._extract_with_context(text, 'name_change')
        return dates[0] if dates else None
    
    def validate_date_sequence(self, dates: List[datetime]) -> bool:
        """
        Check if dates are in chronological order
        
        Args:
            dates: List of dates
            
        Returns:
            True if dates are sequential
        """
        if len(dates) <= 1:
            return True
        
        sorted_dates = sorted(dates)
        return dates == sorted_dates
    
    def find_date_mismatches(self, expected_date: datetime, 
                           found_dates: List[datetime],
                           tolerance_days: int = 0) -> List[Dict[str, Any]]:
        """
        Find dates that don't match the expected date
        
        Args:
            expected_date: Expected date
            found_dates: List of dates found in document
            tolerance_days: Allowed difference in days
            
        Returns:
            List of mismatch details
        """
        mismatches = []
        
        for found_date in found_dates:
            if not self.compare_dates(expected_date, found_date, tolerance_days):
                diff_days = (found_date - expected_date).days
                mismatches.append({
                    'expected': expected_date,
                    'found': found_date,
                    'difference_days': diff_days,
                    'expected_str': self.format_date(expected_date),
                    'found_str': self.format_date(found_date)
                })
        
        return mismatches
