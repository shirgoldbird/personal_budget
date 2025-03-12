import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import uuid

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
class Config:
    TELLER_BASE_URL = os.environ.get('TELLER_BASE_URL', 'https://api.teller.io')
    CERT_PATH = os.environ.get('TELLER_CERT_PATH')
    KEY_PATH = os.environ.get('TELLER_KEY_PATH')
    GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
    GOOGLE_CREDS_PATH = os.environ.get('GOOGLE_CREDS_PATH')
    CATEGORIES_FILE = os.environ.get('CATEGORIES_FILE', 'categories.json')
    TRANSACTION_MAPPING_FILE = os.environ.get('TRANSACTION_MAPPING_FILE', 'transaction_mappings.json')

# Teller client
class TellerClient:
    def __init__(self, access_token=None):
        self.base_url = Config.TELLER_BASE_URL
        self.cert = (Config.CERT_PATH, Config.KEY_PATH) if Config.CERT_PATH and Config.KEY_PATH else None
        self.access_token = access_token

    def list_accounts(self):
        return self._request('GET', '/accounts')

    def get_account_details(self, account_id):
        return self._request('GET', f'/accounts/{account_id}/details')

    def get_account_balances(self, account_id):
        return self._request('GET', f'/accounts/{account_id}/balances')

    def list_transactions(self, account_id):
        return self._request('GET', f'/accounts/{account_id}/transactions')

    def _request(self, method, path, data=None):
        url = self.base_url + path
        headers = {}
        auth = (self.access_token, '') if self.access_token else None
        
        response = requests.request(
            method, 
            url, 
            json=data, 
            cert=self.cert,
            auth=auth,
            headers=headers
        )
        
        if response.status_code >= 400:
            return {'error': response.text, 'status_code': response.status_code}
        
        return response.json()

# Google Sheets client
class GoogleSheetsClient:
    def __init__(self):
        self.creds = None
        self.sheet_id = Config.GOOGLE_SHEET_ID
        
        if Config.GOOGLE_CREDS_PATH:
            self.creds = Credentials.from_service_account_file(
                Config.GOOGLE_CREDS_PATH,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=self.creds)
            self.sheet = self.service.spreadsheets()

    def append_transactions(self, transactions):
        if not self.creds or not self.sheet_id:
            return {'error': 'Google Sheets credentials or Sheet ID not configured'}
        
        values = []
        for tx in transactions:
            values.append([
                tx.get('id', ''),
                tx.get('date', ''),
                tx.get('account_id', ''),
                tx.get('description', ''),
                tx.get('amount', ''),
                tx.get('category', ''),
                tx.get('notes', ''),
                datetime.now().isoformat()
            ])
        
        body = {
            'values': values
        }
        
        result = self.sheet.values().append(
            spreadsheetId=self.sheet_id,
            range='Transactions!A:H',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return result

# Category Manager
class CategoryManager:
    def __init__(self):
        self.categories_file = Config.CATEGORIES_FILE
        self.mappings_file = Config.TRANSACTION_MAPPING_FILE
        self.categories = self._load_categories()
        self.mappings = self._load_mappings()
    
    def _load_categories(self):
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading categories: {e}")
            return []
    
    def _load_mappings(self):
        try:
            if os.path.exists(self.mappings_file):
                with open(self.mappings_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading mappings: {e}")
            return {}
    
    def _save_categories(self):
        try:
            with open(self.categories_file, 'w') as f:
                json.dump(self.categories, f, indent=2)
        except Exception as e:
            print(f"Error saving categories: {e}")
    
    def _save_mappings(self):
        try:
            with open(self.mappings_file, 'w') as f:
                json.dump(self.mappings, f, indent=2)
        except Exception as e:
            print(f"Error saving mappings: {e}")
    
    def get_categories(self):
        return self.categories
    
    def add_category(self, category):
        if not category or 'name' not in category:
            return False
        
        # Check if name already exists
        for existing in self.categories:
            if existing.get('name') == category.get('name'):
                return False
        
        # Add unique ID if not provided
        if 'id' not in category:
            category['id'] = str(uuid.uuid4())
        
        self.categories.append(category)
        self._save_categories()
        return True
    
    def update_category(self, category_id, updated_category):
        for i, cat in enumerate(self.categories):
            if cat.get('id') == category_id:
                # Preserve the ID
                updated_category['id'] = category_id
                self.categories[i] = updated_category
                self._save_categories()
                return True
        return False
    
    def delete_category(self, category_id):
        for i, cat in enumerate(self.categories):
            if cat.get('id') == category_id:
                del self.categories[i]
                self._save_categories()
                return True
        return False
    
    def get_mappings(self):
        return self.mappings
    
    def add_mapping(self, pattern, category_id):
        self.mappings[pattern] = category_id
        self._save_mappings()
        return True
    
    def delete_mapping(self, pattern):
        if pattern in self.mappings:
            del self.mappings[pattern]
            self._save_mappings()
            return True
        return False
    
    def categorize_transaction(self, transaction):
        """Auto-categorize a transaction based on mappings"""
        description = transaction.get('description', '').lower()
        
        # Check for direct matches in mappings
        for pattern, category_id in self.mappings.items():
            if pattern.lower() in description:
                # Find category name
                for cat in self.categories:
                    if cat.get('id') == category_id:
                        return cat.get('name')
        
        # Default to "Uncategorized" if no match
        return "Uncategorized"


# Initialize clients
teller_client = TellerClient()
sheets_client = GoogleSheetsClient()
category_manager = CategoryManager()

# Routes
@app.route('/api/accounts', methods=['GET'])
def list_accounts():
    access_token = request.headers.get('X-Teller-Token')
    if not access_token:
        return jsonify({'error': 'X-Teller-Token header is required'}), 401
    
    client = TellerClient(access_token)
    accounts = client.list_accounts()
    return jsonify(accounts)

@app.route('/api/accounts/<account_id>/transactions', methods=['GET'])
def list_transactions(account_id):
    access_token = request.headers.get('X-Teller-Token')
    if not access_token:
        return jsonify({'error': 'X-Teller-Token header is required'}), 401
    
    client = TellerClient(access_token)
    transactions = client.list_transactions(account_id)
    
    # Add category field to each transaction if missing
    for tx in transactions:
        if 'category' not in tx:
            tx['category'] = category_manager.categorize_transaction(tx)
    
    return jsonify(transactions)

@app.route('/api/transactions/categorize', methods=['POST'])
def categorize_transactions():
    data = request.json
    if not data or 'transactions' not in data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    transactions = data['transactions']
    categorized = []
    
    for tx in transactions:
        # If category not provided, auto-categorize
        if 'category' not in tx:
            tx['category'] = category_manager.categorize_transaction(tx)
        categorized.append(tx)
    
    return jsonify(categorized)

@app.route('/api/transactions/export', methods=['POST'])
def export_transactions():
    data = request.json
    if not data or 'transactions' not in data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    result = sheets_client.append_transactions(data['transactions'])
    return jsonify(result)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(category_manager.get_categories())

@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    success = category_manager.add_category(data)
    if success:
        return jsonify({'success': True, 'categories': category_manager.get_categories()})
    return jsonify({'error': 'Failed to add category'}), 400

@app.route('/api/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    success = category_manager.update_category(category_id, data)
    if success:
        return jsonify({'success': True, 'categories': category_manager.get_categories()})
    return jsonify({'error': 'Category not found'}), 404

@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    success = category_manager.delete_category(category_id)
    if success:
        return jsonify({'success': True, 'categories': category_manager.get_categories()})
    return jsonify({'error': 'Category not found'}), 404

@app.route('/api/mappings', methods=['GET'])
def get_mappings():
    return jsonify(category_manager.get_mappings())

@app.route('/api/mappings', methods=['POST'])
def add_mapping():
    data = request.json
    if not data or 'pattern' not in data or 'category_id' not in data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    success = category_manager.add_mapping(data['pattern'], data['category_id'])
    if success:
        return jsonify({'success': True, 'mappings': category_manager.get_mappings()})
    return jsonify({'error': 'Failed to add mapping'}), 400

@app.route('/api/mappings/<pattern>', methods=['DELETE'])
def delete_mapping(pattern):
    success = category_manager.delete_mapping(pattern)
    if success:
        return jsonify({'success': True, 'mappings': category_manager.get_mappings()})
    return jsonify({'error': 'Mapping not found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')