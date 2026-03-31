"""
Core Data Cleaning Logic
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCleaner:
    """Main data cleaning class"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize cleaner with dataframe"""
        self.df = df.copy()
        self.original_df = df.copy()
        self.cleaning_log = []
    
    def remove_duplicates(self, subset: List[str] = None, keep: str = 'first') -> pd.DataFrame:
        """
        Remove duplicate rows
        
        Args:
            subset: Column names to consider for duplicates
            keep: 'first', 'last', or False
        """
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed = initial_rows - len(self.df)
        
        log_msg = f"Removed {removed} duplicate rows"
        self.cleaning_log.append(log_msg)
        logger.info(log_msg)
        
        return self.df
    
    def handle_missing_values(self, strategy: str = 'mean', columns: List[str] = None) -> pd.DataFrame:
        """
        Handle missing values in the dataset
        
        Args:
            strategy: 'mean', 'median', 'mode', 'drop', 'forward_fill', 'backward_fill'
            columns: Specific columns to handle (None = all)
        """
        target_cols = columns if columns else self.df.columns
        
        for col in target_cols:
            if col not in self.df.columns:
                continue
                
            missing_count = self.df[col].isna().sum()
            if missing_count == 0:
                continue
            
            if strategy == 'drop':
                self.df = self.df.dropna(subset=[col])
            elif strategy == 'mean' and pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col].fillna(self.df[col].mean(), inplace=True)
            elif strategy == 'median' and pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col].fillna(self.df[col].median(), inplace=True)
            elif strategy == 'mode':
                mode_val = self.df[col].mode()
                if not mode_val.empty:
                    self.df[col].fillna(mode_val[0], inplace=True)
            elif strategy == 'forward_fill':
                self.df[col].fillna(method='ffill', inplace=True)
            elif strategy == 'backward_fill':
                self.df[col].fillna(method='bfill', inplace=True)
            
            log_msg = f"Handled {missing_count} missing values in '{col}' using {strategy}"
            self.cleaning_log.append(log_msg)
            logger.info(log_msg)
        
        return self.df
    
    def detect_outliers(self, method: str = 'iqr', columns: List[str] = None, threshold: float = 1.5) -> Dict[str, List[int]]:
        """
        Detect outliers in numeric columns
        
        Args:
            method: 'iqr' or 'zscore'
            columns: Specific columns to check (None = all numeric)
            threshold: IQR multiplier or z-score threshold
        
        Returns:
            Dictionary with column names and outlier indices
        """
        outliers = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        target_cols = columns if columns else numeric_cols
        
        for col in target_cols:
            if col not in self.df.columns or not pd.api.types.is_numeric_dtype(self.df[col]):
                continue
            
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                outlier_indices = self.df[outlier_mask].index.tolist()
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(self.df[col].dropna()))
                outlier_indices = self.df[np.abs(stats.zscore(self.df[col])) > threshold].index.tolist()
            
            if outlier_indices:
                outliers[col] = outlier_indices
                log_msg = f"Detected {len(outlier_indices)} outliers in '{col}' using {method}"
                self.cleaning_log.append(log_msg)
                logger.info(log_msg)
        
        return outliers
    
    def remove_outliers(self, method: str = 'iqr', columns: List[str] = None, threshold: float = 1.5) -> pd.DataFrame:
        """Remove detected outliers"""
        outliers = self.detect_outliers(method=method, columns=columns, threshold=threshold)
        
        all_outlier_indices = set()
        for indices in outliers.values():
            all_outlier_indices.update(indices)
        
        initial_rows = len(self.df)
        self.df = self.df.drop(list(all_outlier_indices))
        removed = initial_rows - len(self.df)
        
        log_msg = f"Removed {removed} rows containing outliers"
        self.cleaning_log.append(log_msg)
        logger.info(log_msg)
        
        return self.df
    
    def reformat_columns(self, transformations: Dict[str, str]) -> pd.DataFrame:
        """
        Reformat columns based on transformations
        
        Args:
            transformations: Dict with column names and transformation types
                           ('lowercase', 'uppercase', 'strip', 'int', 'float', 'datetime')
        """
        for col, transform_type in transformations.items():
            if col not in self.df.columns:
                continue
            
            try:
                if transform_type == 'lowercase':
                    self.df[col] = self.df[col].astype(str).str.lower()
                elif transform_type == 'uppercase':
                    self.df[col] = self.df[col].astype(str).str.upper()
                elif transform_type == 'strip':
                    self.df[col] = self.df[col].astype(str).str.strip()
                elif transform_type == 'int':
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce').astype('Int64')
                elif transform_type == 'float':
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                elif transform_type == 'datetime':
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                
                log_msg = f"Reformatted column '{col}' as {transform_type}"
                self.cleaning_log.append(log_msg)
                logger.info(log_msg)
            except Exception as e:
                logger.error(f"Error reformatting column '{col}': {str(e)}")
        
        return self.df
    
    def remove_empty_columns(self) -> pd.DataFrame:
        """Remove columns that are completely empty"""
        initial_cols = len(self.df.columns)
        self.df = self.df.dropna(axis=1, how='all')
        removed = initial_cols - len(self.df.columns)
        
        if removed > 0:
            log_msg = f"Removed {removed} empty columns"
            self.cleaning_log.append(log_msg)
            logger.info(log_msg)
        
        return self.df
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """Get a comprehensive cleaning report"""
        return {
            'original_rows': len(self.original_df),
            'original_columns': len(self.original_df.columns),
            'final_rows': len(self.df),
            'final_columns': len(self.df.columns),
            'rows_removed': len(self.original_df) - len(self.df),
            'columns_removed': len(self.original_df.columns) - len(self.df.columns),
            'cleaning_steps': self.cleaning_log
        }
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """Return cleaned dataframe"""
        return self.df
