# Configuration settings for the Pharmacy Management System

import os
from datetime import datetime

class Config:
    # Database settings
    DATABASE_NAME = 'pharmacy.db'
    
    # Application settings
    APP_NAME = "Pharmacy Management System"
    VERSION = "1.0.0"
    
    # Default settings
    DEFAULT_STORE_NAME = "My Pharmacy"
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"
    
    # Tax settings
    TAX_RATE = 0.1  # 10% tax rate
    
    # AI settings
    AI_MODEL_PATH = "models/stock_prediction.pkl"
    
    # n8n settings
    N8N_URL = "http://localhost:5678"
    
    # Backup settings
    BACKUP_DIR = "backups"
    AUTO_BACKUP_INTERVAL = 24  # hours
    
    # Invoice settings
    INVOICE_PREFIX = "INV"
    INVOICE_LOGO_PATH = "assets/logo.png"
    
    # Barcode settings
    BARCODE_PREFIX = "MED"
    
    # Notification settings
    SMS_API_KEY = ""
    WHATSAPP_API_KEY = ""
    
    # UI settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    MIN_WINDOW_WIDTH = 1000
    MIN_WINDOW_HEIGHT = 600
    
    # Date format
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    
    # Create directories if they don't exist
    for directory in [BACKUP_DIR, ASSETS_DIR, MODELS_DIR, REPORTS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def get_current_date():
        return datetime.now().strftime(Config.DATE_FORMAT)
    
    @staticmethod
    def get_current_datetime():
        return datetime.now().strftime(Config.DATETIME_FORMAT)