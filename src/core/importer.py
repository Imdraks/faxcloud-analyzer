"""
Importer module for FaxCloud analyzer.
Handles CSV and XLSX file import with automatic format detection.
"""

import os
import csv
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import chardet

from .config import Config

logger = logging.getLogger(__name__)


class FileImporter:
    """Handle import of CSV and XLSX files with automatic detection."""

    # Supported formats
    SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls']
    
    # Possible delimiters for CSV
    POSSIBLE_DELIMITERS = [';', ',', '\t', '|']
    
    # Expected columns
    EXPECTED_COLUMNS = {
        'fax_id': 0,           # A
        'user': 1,             # B
        'empty_c': 2,          # C
        'mode': 3,             # D
        'empty_e': 4,          # E
        'datetime': 5,         # F
        'empty_g': 6,          # G
        'number': 7,           # H
        'empty_i': 8,          # I
        'empty_j': 9,          # J
        'pages': 10            # K
    }

    def __init__(self, import_dir: str = None):
        """Initialize importer with optional custom import directory."""
        self.import_dir = import_dir or Config.IMPORT_DIR
        self.detected_encoding = None
        self.detected_delimiter = None
        self.file_format = None

    def import_file(self, file_path: str) -> dict:
        """
        Import a file and return structured data.
        
        Args:
            file_path: Path to the file to import
            
        Returns:
            dict with keys: success, data, errors, metadata
        """
        logger.info(f"Starting import of {file_path}")
        
        # Validate file exists
        if not os.path.exists(file_path):
            return self._error_response(f"File not found: {file_path}")
        
        # Detect file format
        self.file_format = self._detect_format(file_path)
        if not self.file_format:
            return self._error_response(f"Unsupported file format")
        
        logger.info(f"Detected format: {self.file_format}")
        
        try:
            # Import based on format
            if self.file_format == '.csv':
                return self._import_csv(file_path)
            else:
                return self._import_excel(file_path)
        except Exception as e:
            logger.error(f"Import error: {str(e)}")
            return self._error_response(f"Import failed: {str(e)}")

    def _detect_format(self, file_path: str) -> str:
        """Detect file format from extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in self.SUPPORTED_FORMATS:
            return ext
        return None

    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            logger.info(f"Detected encoding: {encoding}")
            return encoding or 'utf-8'
        except Exception as e:
            logger.warning(f"Could not detect encoding: {e}, using utf-8")
            return 'utf-8'

    def _detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Auto-detect CSV delimiter."""
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                sample = f.read(1024)
            
            # Try Sniffer
            try:
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample, delimiters=';,\t|').delimiter
                logger.info(f"Detected delimiter: '{delimiter}'")
                return delimiter
            except:
                pass
            
            # Count occurrences of each delimiter
            for delim in self.POSSIBLE_DELIMITERS:
                if delim in sample:
                    logger.info(f"Using delimiter: '{delim}'")
                    return delim
            
            # Default for FaxCloud files
            logger.info("Using default delimiter: ';'")
            return ';'
            
        except Exception as e:
            logger.warning(f"Could not detect delimiter: {e}, using ';'")
            return ';'

    def _import_csv(self, file_path: str) -> dict:
        """Import CSV file."""
        # Detect encoding and delimiter
        self.detected_encoding = self._detect_encoding(file_path)
        self.detected_delimiter = self._detect_delimiter(file_path, self.detected_encoding)
        
        try:
            # Read with pandas
            df = pd.read_csv(
                file_path,
                encoding=self.detected_encoding,
                sep=self.detected_delimiter,
                header=None
            )
            
            logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Extract fax entries
            entries = self._extract_entries(df)
            
            return {
                'success': True,
                'data': entries,
                'errors': [],
                'metadata': {
                    'file': os.path.basename(file_path),
                    'format': self.file_format,
                    'encoding': self.detected_encoding,
                    'delimiter': self.detected_delimiter,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'imported_entries': len(entries),
                    'import_date': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"CSV import error: {e}")
            return self._error_response(f"CSV import failed: {str(e)}")

    def _import_excel(self, file_path: str) -> dict:
        """Import Excel file (XLSX or XLS)."""
        try:
            # Read Excel file
            df = pd.read_excel(file_path, header=None)
            
            logger.info(f"Excel loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Extract fax entries
            entries = self._extract_entries(df)
            
            return {
                'success': True,
                'data': entries,
                'errors': [],
                'metadata': {
                    'file': os.path.basename(file_path),
                    'format': self.file_format,
                    'encoding': 'utf-8',
                    'delimiter': 'N/A',
                    'rows': len(df),
                    'columns': len(df.columns),
                    'imported_entries': len(entries),
                    'import_date': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Excel import error: {e}")
            return self._error_response(f"Excel import failed: {str(e)}")

    def _extract_entries(self, df: pd.DataFrame) -> list:
        """Extract FAX entries from dataframe."""
        entries = []
        
        for idx, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row.iloc[0]) and pd.isna(row.iloc[7]):
                    continue
                
                # Extract fields
                fax_id = str(row.iloc[0]).strip() if idx < len(self.EXPECTED_COLUMNS) else None
                user = str(row.iloc[1]).strip() if idx < len(self.EXPECTED_COLUMNS) else None
                mode = str(row.iloc[3]).strip() if idx < len(self.EXPECTED_COLUMNS) else None
                datetime_str = str(row.iloc[5]).strip() if idx < len(self.EXPECTED_COLUMNS) else None
                number = str(row.iloc[7]).strip() if idx < len(self.EXPECTED_COLUMNS) else None
                pages = row.iloc[10] if idx < len(self.EXPECTED_COLUMNS) else None
                
                # Skip if essential fields are missing
                if not number or number == 'nan':
                    continue
                
                # Create entry
                entry = {
                    'fax_id': fax_id if fax_id and fax_id != 'nan' else None,
                    'user': user if user and user != 'nan' else None,
                    'mode': mode if mode and mode != 'nan' else None,
                    'datetime': datetime_str if datetime_str and datetime_str != 'nan' else None,
                    'number': number,
                    'pages': int(pages) if pd.notna(pages) and str(pages) != 'nan' else None
                }
                
                entries.append(entry)
                
            except Exception as e:
                logger.warning(f"Error extracting row {idx}: {e}")
                continue
        
        logger.info(f"Extracted {len(entries)} FAX entries")
        return entries

    def save_imported_file(self, file_path: str, dest_dir: str = None) -> str:
        """Save imported file to import directory."""
        dest_dir = dest_dir or self.import_dir
        os.makedirs(dest_dir, exist_ok=True)
        
        filename = os.path.basename(file_path)
        dest_path = os.path.join(dest_dir, filename)
        
        try:
            with open(file_path, 'rb') as src:
                with open(dest_path, 'wb') as dst:
                    dst.write(src.read())
            logger.info(f"File saved to {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise

    def _error_response(self, message: str) -> dict:
        """Create error response."""
        return {
            'success': False,
            'data': [],
            'errors': [message],
            'metadata': {}
        }
