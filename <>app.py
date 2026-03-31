"""
Main Flask Application for Data Cleaning System
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from api.routes import api_bp
from config import Config

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Data Cleaning System is running'}), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to Data Cleaning System API'}), 200

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False), host='0.0.0.0', port=5000)
