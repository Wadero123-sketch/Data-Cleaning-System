"""
File Upload and Format Handling
"""
import pandas as pd
import os
import logging
from typing import Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UploadHandler:
    """Handle various file formats"""
    
    SUPPORTED_FORMATS = {
        'csv': 'read_csv',
        'xlsx': 'read_excel',
        'xls': 'read_excel',
        'json': 'read_json',
        'xml': 'read_xml',
        'parquet': 'read_parquet',
        'tsv': 'read_csv'
    }
    
    def read_file(self, filepath: str) -> pd.DataFrame:
        """
        Read file and return pandas DataFrame
        
        Args:
            filepath: Path to the file
        
        Returns:
            DataFrame
        """
        file_ext = os.path.splitext(filepath)[1].lstrip('.').lower()
        
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        try:
            if file_ext == 'csv':
                df = pd.read_csv(filepath)
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(filepath)
            elif file_ext == 'json':
                df = pd.read_json(filepath)
            elif file_ext == 'xml':
                df = pd.read_xml(filepath)
            elif file_ext == 'parquet':
                df = pd.read_parquet(filepath)
            elif file_ext == 'tsv':
                df = pd.read_csv(filepath, sep='\t')
            
            logger.info(f"Successfully read {file_ext} file: {filepath}")
            return df
        
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            raise
    
    def write_file(self, df: pd.DataFrame, filepath: str) -> None:
        """
        Write DataFrame to file
        
        Args:
            df: DataFrame to write
            filepath: Output file path
        """
        file_ext = os.path.splitext(filepath)[1].lstrip('.').lower()
        
        try:
            if file_ext == 'csv':
                df.to_csv(filepath, index=False)
            elif file_ext in ['xlsx', 'xls']:
                df.to_excel(filepath, index=False)
            elif file_ext == 'json':
                df.to_json(filepath, orient='records')
            elif file_ext == 'xml':
                df.to_xml(filepath, index=False)
            elif file_ext == 'parquet':
                df.to_parquet(filepath, index=False)
            elif file_ext == 'tsv':
                df.to_csv(filepath, sep='\t', index=False)
            
            logger.info(f"Successfully wrote {file_ext} file: {filepath}")
        
        except Exception as e:
            logger.error(f"Error writing file {filepath}: {str(e)}")
            raise
