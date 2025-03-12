import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import uuid
import uvicorn
from teller_token_manager import TellerTokenManager
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Personal Budgeting API", 
              description="API for personal budgeting with Teller integration")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
class Config:
    TELLER_BASE_URL = os.environ.get('TELLER_BASE_URL', 'https://api.teller.io')
    CERT_PATH = os.environ.get('TELLER_CERT_PATH')
    KEY_PATH = os.environ.get('TELLER_KEY_PATH')
    GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
    GOOGLE_CREDS_PATH = os.environ.get('GOOGLE_CREDS_PATH')
    CATEGORIES_FILE = os.environ.get('CATEGORIES_FILE', 'categories.json')
    TRANSACTION_MAPPING_FILE = os.environ.get('TRANSACTION_MAPPING_FILE', 'transaction_mappings.json')
    CREDS_DIR = os.environ.get('CREDS_DIR', 'creds')

# Pydantic models
class Category(BaseModel):
    id: Optional[str] = None
    name: str
    color: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class Mapping(BaseModel):
    pattern: str
    category_id: str

class Transaction(BaseModel):
    id: str
    date: str
    account_id: str
    description: str
    amount: str
    category: Optional[str] = None
    notes: Optional[str] = None

class TransactionBatch(BaseModel):
    transactions: List[Transaction]

class TellerEnrollment(BaseModel):
    accessToken: str
    user: Dict[str, Any]
    enrollment: Dict[str, Any]
    signatures: Optional[List[str]] = None

class TellerTokenInfo(BaseModel):
    institution_name: str
    access_token: Optional[str] = None
    institution_id: Optional[str] = None
    user_id: Optional[str] = None
    enrollment_id: Optional[str] = None

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
            
            # Check and set up the transactions sheet if needed
            self._ensure_transactions_sheet()

    def _ensure_transactions_sheet(self):
        """Ensures the Transactions sheet exists with proper headers"""
        if not self.creds or not self.sheet_id:
            return
            
        try:
            # Check if sheet exists
            metadata = self.sheet.get(spreadsheetId=self.sheet_id).execute()
            sheet_exists = False
            
            for sheet in metadata.get('sheets', []):
                if sheet.get('properties', {}).get('title') == 'Transactions':
                    sheet_exists = True
                    break
            
            # If sheet doesn't exist, create it
            if not sheet_exists:
                request = {
                    'addSheet': {
                        'properties': {
                            'title': 'Transactions',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    }
                }
                
                body = {'requests': [request]}
                self.sheet.batchUpdate(spreadsheetId=self.sheet_id, body=body).execute()
                print("Created 'Transactions' sheet")
            
            # Check if headers exist
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range='Transactions!A1:H1'
            ).execute()
            
            headers = result.get('values', [[]])[0] if 'values' in result else []
            expected_headers = [
                'Transaction ID', 'Date', 'Account ID', 'Description', 
                'Amount', 'Category', 'Notes', 'Timestamp'
            ]
            
            # If no headers or incomplete headers, add them
            if len(headers) < len(expected_headers):
                body = {
                    'values': [expected_headers]
                }
                
                self.sheet.values().update(
                    spreadsheetId=self.sheet_id,
                    range='Transactions!A1:H1',
                    valueInputOption='RAW',
                    body=body
                ).execute()
                print("Added headers to Transactions sheet")
                
        except Exception as e:
            print(f"Error setting up Google Sheet: {e}")

    def append_transactions(self, transactions):
        if not self.creds or not self.sheet_id:
            return {'error': 'Google Sheets credentials or Sheet ID not configured'}
        
        # Ensure sheet is set up before appending
        self._ensure_transactions_sheet()
        
        values = []
        for tx in transactions:
            values.append([
                tx.id,
                tx.date,
                tx.account_id,
                tx.description,
                tx.amount,
                tx.category,
                tx.notes or '',
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
    
    def add_category(self, category_data):
        # Check if name already exists
        for existing in self.categories:
            if existing.get('name') == category_data.name:
                return False
        
        # Add unique ID if not provided
        category_dict = category_data.dict()
        if not category_dict.get('id'):
            category_dict['id'] = str(uuid.uuid4())
        
        self.categories.append(category_dict)
        self._save_categories()
        return True
    
    def update_category(self, category_id, updated_category):
        for i, cat in enumerate(self.categories):
            if cat.get('id') == category_id:
                # Update only provided fields while preserving the ID
                update_dict = updated_category.dict(exclude_unset=True)
                self.categories[i].update(update_dict)
                self.categories[i]['id'] = category_id  # Ensure ID doesn't change
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
        description = transaction.description.lower()
        
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
token_manager = TellerTokenManager(Config.CREDS_DIR)

# Dependency to get Teller token from header or parameter
async def get_teller_token(
    x_teller_token: Optional[str] = Header(None), 
    institution: Optional[str] = None
):
    # If a specific header token is provided, use that
    if x_teller_token:
        return x_teller_token
    
    # If an institution name is provided, try to get token for that institution
    if institution:
        token = token_manager.get_token_by_institution(institution)
        if token:
            return token
    
    # If no valid token can be found, raise an error
    raise HTTPException(
        status_code=401, 
        detail="Valid Teller token required. Provide X-Teller-Token header or institution parameter."
    )

# Routes
@app.get("/api/accounts")
async def list_accounts(
    token: str = Depends(get_teller_token),
    institution: Optional[str] = None
):
    client = TellerClient(token)
    accounts = client.list_accounts()
    
    if 'error' in accounts:
        raise HTTPException(status_code=accounts.get('status_code', 400), detail=accounts['error'])
    
    return accounts

@app.get("/api/accounts/{account_id}/transactions")
async def list_transactions(
    account_id: str, 
    token: str = Depends(get_teller_token),
    institution: Optional[str] = None
):
    client = TellerClient(token)
    transactions = client.list_transactions(account_id)
    
    if 'error' in transactions:
        raise HTTPException(status_code=transactions.get('status_code', 400), detail=transactions['error'])
    
    # Add category field to each transaction if missing
    for tx in transactions:
        if 'category' not in tx:
            # Convert dict to Transaction model and back for categorization
            tx_model = Transaction(
                id=tx.get('id', ''),
                date=tx.get('date', ''),
                account_id=tx.get('account_id', ''),
                description=tx.get('description', ''),
                amount=tx.get('amount', '')
            )
            tx['category'] = category_manager.categorize_transaction(tx_model)
    
    return transactions

@app.post("/api/transactions/categorize")
async def categorize_transactions(data: TransactionBatch):
    categorized = []
    
    for tx in data.transactions:
        # If category not provided, auto-categorize
        if not tx.category:
            tx.category = category_manager.categorize_transaction(tx)
        categorized.append(tx)
    
    return categorized

@app.post("/api/transactions/export")
async def export_transactions(data: TransactionBatch):
    result = sheets_client.append_transactions(data.transactions)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result

@app.get("/api/categories")
async def get_categories():
    return category_manager.get_categories()

@app.post("/api/categories")
async def add_category(category: Category):
    success = category_manager.add_category(category)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add category. Name may already exist.")
    
    return {"success": True, "categories": category_manager.get_categories()}

@app.put("/api/categories/{category_id}")
async def update_category(category_id: str, category: CategoryUpdate):
    success = category_manager.update_category(category_id, category)
    
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"success": True, "categories": category_manager.get_categories()}

@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: str):
    success = category_manager.delete_category(category_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"success": True, "categories": category_manager.get_categories()}

@app.get("/api/mappings")
async def get_mappings():
    return category_manager.get_mappings()

@app.post("/api/mappings")
async def add_mapping(mapping: Mapping):
    success = category_manager.add_mapping(mapping.pattern, mapping.category_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add mapping")
    
    return {"success": True, "mappings": category_manager.get_mappings()}

@app.delete("/api/mappings/{pattern}")
async def delete_mapping(pattern: str):
    success = category_manager.delete_mapping(pattern)
    
    if not success:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    return {"success": True, "mappings": category_manager.get_mappings()}

# Teller Connect integration endpoints
@app.post("/api/teller/store-token")
async def store_teller_token(enrollment: TellerEnrollment):
    """
    Store a Teller access token received from Teller Connect
    This endpoint is intended to be called from your frontend after successful enrollment
    """
    success = token_manager.store_teller_enrollment(enrollment.dict())
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to store token")
    
    return {"success": True, "message": "Token stored successfully"}

@app.get("/api/teller/tokens")
async def list_teller_tokens():
    """List all stored Teller tokens with institution information"""
    tokens = token_manager.get_all_tokens()
    
    # Sanitize the response to not include the actual tokens in the response
    sanitized_tokens = []
    for token in tokens:
        sanitized_tokens.append({
            "institution_name": token.get("institution_name"),
            "institution_id": token.get("institution_id"),
            "enrollment_id": token.get("enrollment_id"),
            "created_at": token.get("created_at"),
            "last_updated": token.get("last_updated")
        })
    
    return sanitized_tokens

@app.delete("/api/teller/tokens/{institution_name}")
async def delete_teller_token(institution_name: str):
    """Delete a Teller token for a specific institution"""
    token = token_manager.get_token_by_institution(institution_name)
    
    if not token:
        raise HTTPException(status_code=404, detail=f"No token found for institution: {institution_name}")
    
    success = token_manager.delete_token(token)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete token")
    
    return {"success": True, "message": f"Token for {institution_name} deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=os.environ.get('DEBUG', 'False').lower() == 'true')