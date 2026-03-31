"""
Data Validation Module
"""
import pandas as pd
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidator:
    """Validate data quality and structure"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict:
        """
        Validate dataframe structure and quality
        
        Returns validation report
        """
        report = {
            'valid': True,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isna().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
            'issues': []
        }
        
        # Check for issues
        if df.empty:
            report['issues'].append("DataFrame is empty")
            report['valid'] = False
        
        if report['missing_values']:
            missing_pct = {col: (count/len(df)*100) for col, count in report['missing_values'].items() if count > 0}
            report['missing_percentage'] = missing_pct
        
        if report['duplicate_rows'] > 0:
            report['issues'].append(f"Found {report['duplicate_rows']} duplicate rows")
        
        return report
    
    @staticmethod
    def validate_columns(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """Check if required columns exist"""
        missing = [col for col in required_columns if col not in df.columns]
        return len(missing) == 0, missing
    
    @staticmethod
    def validate_column_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> Dict[str, bool]:
        """Validate column data types"""
        results = {}
        for col, expected_type in expected_types.items():
            if col not in df.columns:
                results[col] = False
                continue
            
            actual_type = str(df[col].dtype)
            results[col] = expected_type.lower() in actual_type.lower()
        
        return results
