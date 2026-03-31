"""
API Routes for Data Cleaning System
"""
from flask import Blueprint, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import pandas as pd
from data_cleaner import DataCleaner, DataValidator, DataPreprocessor
from .upload_handler import UploadHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx', 'xls', 'xml', 'parquet', 'tsv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process data file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Read file based on extension
        handler = UploadHandler()
        df = handler.read_file(filepath)
        
        # Validate
        validator = DataValidator()
        validation_report = validator.validate_dataframe(df)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': filename,
            'filepath': filepath,
            'validation': validation_report
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clean', methods=['POST'])
def clean_data():
    """Clean data based on provided configuration"""
    try:
        data = request.json
        filepath = data.get('filepath')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 400
        
        # Read file
        handler = UploadHandler()
        df = handler.read_file(filepath)
        
        # Preprocess
        preprocessor = DataPreprocessor()
        df = preprocessor.standardize_column_names(df)
        df = preprocessor.remove_whitespace(df)
        
        # Clean
        cleaner = DataCleaner(df)
        
        # Apply cleaning operations
        if data.get('remove_duplicates', True):
            cleaner.remove_duplicates()
        
        if data.get('handle_missing_values', True):
            strategy = data.get('missing_value_strategy', 'mean')
            cleaner.handle_missing_values(strategy=strategy)
        
        if data.get('remove_outliers', False):
            method = data.get('outlier_method', 'iqr')
            cleaner.remove_outliers(method=method)
        
        if data.get('reformat_columns'):
            cleaner.reformat_columns(data.get('reformat_columns', {}))
        
        cleaner.remove_empty_columns()
        
        # Get results
        cleaned_df = cleaner.get_cleaned_data()
        report = cleaner.get_cleaning_report()
        
        # Save cleaned file
        cleaned_filename = f"cleaned_{os.path.basename(filepath)}"
        cleaned_filepath = os.path.join(UPLOAD_FOLDER, cleaned_filename)
        handler.write_file(cleaned_df, cleaned_filepath)
        
        return jsonify({
            'success': True,
            'message': 'Data cleaned successfully',
            'report': report,
            'cleaned_file': cleaned_filename,
            'cleaned_filepath': cleaned_filepath
        }), 200
    
    except Exception as e:
        logger.error(f"Error cleaning data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download cleaned file"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/validate', methods=['POST'])
def validate_data():
    """Validate uploaded data"""
    try:
        data = request.json
        filepath = data.get('filepath')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 400
        
        handler = UploadHandler()
        df = handler.read_file(filepath)
        
        validator = DataValidator()
        report = validator.validate_dataframe(df)
        
        return jsonify({
            'success': True,
            'validation_report': report
        }), 200
    
    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/preview/<filename>', methods=['GET'])
def preview_data(filename):
    """Preview file contents"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        handler = UploadHandler()
        df = handler.read_file(filepath)
        
        preview_data = df.head(10).to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'preview': preview_data,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns)
        }), 200
    
    except Exception as e:
        logger.error(f"Error previewing file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats/<filename>', methods=['GET'])
def get_statistics(filename):
    """Get data statistics"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        handler = UploadHandler()
        df = handler.read_file(filepath)
        
        stats = {
            'numeric_stats': df.describe().to_dict(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_count': df.isna().sum().to_dict(),
            'unique_count': df.nunique().to_dict()
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500
