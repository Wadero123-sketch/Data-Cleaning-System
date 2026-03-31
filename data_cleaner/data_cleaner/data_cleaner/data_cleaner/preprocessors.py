"""
Data Preprocessing Module
"""
import pandas as pd
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Preprocess data before cleaning"""
    
    @staticmethod
    def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names (lowercase, remove spaces, special chars)"""
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)
        logger.info("Standardized column names")
        return df
    
    @staticmethod
    def remove_whitespace(df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """Remove leading/trailing whitespace from string columns"""
        target_cols = columns if columns else df.select_dtypes(include=['object']).columns
        
        for col in target_cols:
            if col in df.columns and df[col].dtype == 'object':
                df[col] = df[col].str.strip()
        
        logger.info("Removed whitespace from columns")
        return df
    
    @staticmethod
    def convert_to_numeric(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Convert columns to numeric type"""
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        logger.info(f"Converted {len(columns)} columns to numeric")
        return df
