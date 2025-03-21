import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from pathlib import Path
from pydantic import BaseModel, Field
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import uuid
import uvicorn
import yaml
from teller_token_manager import TellerTokenManager
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Personal Budgeting API", 
              description="API for personal budgeting with Teller integration")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Simple Budget API",
        version="1.0.0",
        description="API for a simple budgeting app",
        routes=app.routes,
    )
        
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
    STATIC_DIR = os.environ.get('STATIC_DIR', 'static')
    HTML_TEMPLATE_DIR = os.environ.get('HTML_TEMPLATE_DIR', 'templates')

# Set up static file serving
static_dir = Path(Config.STATIC_DIR)
templates_dir = Path(Config.HTML_TEMPLATE_DIR)
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Personal Budget Tracker API",
        version="1.0.0",
        description="API for personal budgeting with Teller integration",
        routes=app.routes,
    )
    
    # Add info about API security
    openapi_schema["components"]["securitySchemes"] = {
        "TellerToken": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Teller-Token",
            "description": "Teller access token or specify institution parameter"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Generate OpenAPI spec file
@app.get("/api/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    return JSONResponse(content=app.openapi())

@app.get("/api/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    schema = app.openapi()
    yaml_content = yaml.dump(schema)
    return HTMLResponse(content=yaml_content, media_type="text/yaml")

# Save OpenAPI spec to file system
def save_openapi_spec():
    # Ensure the app has been initialized
    schema = get_openapi(
        title="Personal Budget Tracker API",
        version="1.0.0",
        description="API for personal budgeting with Teller integration",
        routes=app.routes,
    )
    
    # Add security schemes
    if "components" not in schema:
        schema["components"] = {}
    schema["components"]["securitySchemes"] = {
        "TellerToken": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Teller-Token",
            "description": "Teller access token or specify institution parameter"
        }
    }
    
    # Save JSON spec
    json_path = static_dir / "openapi.json"
    with open(json_path, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"✓ Saved OpenAPI JSON spec to {json_path}")
    
    # Save YAML spec
    try:
        yaml_path = static_dir / "openapi.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(schema, f)
        print(f"✓ Saved OpenAPI YAML spec to {yaml_path}")
    except ImportError:
        print("✗ PyYAML not installed - skipping YAML export")

# Copy the frontend files to the static directory if they don't exist
def setup_static_files():
    # JavaScript file
    js_file = static_dir / "frontend_teller_setup.js"
    if not js_file.exists():
        example_js = Path("frontend_teller_setup.js.example")
        if example_js.exists():
            js_file.write_text(example_js.read_text())
    
    # HTML file
    html_file = templates_dir / "index.html"
    if not html_file.exists():
        example_html = Path("index.html.example")
        if example_html.exists():
            html_file.write_text(example_html.read_text())

    save_openapi_spec()

setup_static_files()

# Mount the static directory
app.mount("/static", StaticFiles(directory=Config.STATIC_DIR), name="static")

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
    account_name: str
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
        """Ensures the Transactions sheet exists with proper headers and returns the sheet ID"""
        if not self.creds or not self.sheet_id:
            return None
            
        try:
            # Check if sheet exists
            metadata = self.sheet.get(spreadsheetId=self.sheet_id).execute()
            sheet_exists = False
            sheet_id = None
            
            for sheet in metadata.get('sheets', []):
                if sheet.get('properties', {}).get('title') == 'Transactions':
                    sheet_exists = True
                    sheet_id = sheet.get('properties', {}).get('sheetId')
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
                response = self.sheet.batchUpdate(spreadsheetId=self.sheet_id, body=body).execute()
                
                # Get the sheet ID from the response
                sheet_id = response.get('replies', [{}])[0].get('addSheet', {}).get('properties', {}).get('sheetId')
                print("Created 'Transactions' sheet")
            
            # Check if headers exist
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range='Transactions!A1:I1'
            ).execute()
            
            headers = result.get('values', [[]])[0] if 'values' in result else []
            expected_headers = [
                'Transaction ID', 'Account ID', 'Date', 'Account Name', 'Description', 
                'Amount', 'Category', 'Notes', 'Timestamp'
            ]
            
            # If no headers or incomplete headers, add them
            if len(headers) < len(expected_headers):
                body = {
                    'values': [expected_headers]
                }
                
                self.sheet.values().update(
                    spreadsheetId=self.sheet_id,
                    range='Transactions!A1:I1',
                    valueInputOption='RAW',
                    body=body
                ).execute()
                print("Added headers to Transactions sheet")
            
            return sheet_id
                
        except Exception as e:
            print(f"Error setting up Google Sheet: {e}")
            return None

    def _get_existing_transactions(self):
        """Retrieve all existing transaction IDs and their row numbers"""
        if not self.creds or not self.sheet_id:
            return {}
            
        try:
            # Get all data from the sheet
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range='Transactions!A:I'
            ).execute()
            
            values = result.get('values', [])
            if not values or len(values) <= 1:  # Only headers or empty
                return {}
                
            # Create a map of transaction IDs to row numbers (0-based index)
            # Skip the header row (index 0)
            tx_map = {}
            for i, row in enumerate(values[1:], 1):  # Start from row 1 (after header)
                if row and len(row) > 0:
                    tx_id = row[0]  # Transaction ID is in the first column
                    tx_map[tx_id] = i
                    
            return tx_map
                
        except Exception as e:
            print(f"Error retrieving existing transactions: {e}")
            return {}

    def append_transactions(self, transactions):
        """
        Add transactions to the Google Sheet.
        - Adds new transactions at the top of the sheet (after the header)
        - Detects and updates existing transactions
        - Skips unchanged transactions
        """
        if not self.creds or not self.sheet_id:
            return {'error': 'Google Sheets credentials or Sheet ID not configured'}
        
        # Ensure sheet is set up before proceeding and get the sheet ID
        sheet_id = self._ensure_transactions_sheet()
        if not sheet_id:
            return {'error': 'Could not get or create Transactions sheet'}
        
        # Get existing transaction IDs and their row numbers
        existing_transactions = self._get_existing_transactions()
        
        # Separate transactions into new and existing
        new_transactions = []
        updates = []
        
        for tx in transactions:
            # Format the transaction data
            tx_data = [
                tx.id,
                tx.account_id,
                tx.date,
                tx.account_name,
                tx.description,
                tx.amount,
                tx.category or '',
                tx.notes or '',
                datetime.now().isoformat()
            ]
            
            if tx.id in existing_transactions:
                # Get current row data to compare
                row_num = existing_transactions[tx.id]
                row_range = f'Transactions!A{row_num+1}:I{row_num+1}'  # +1 because sheets are 1-indexed
                
                try:
                    # Get the current row data
                    current_data_result = self.sheet.values().get(
                        spreadsheetId=self.sheet_id,
                        range=row_range
                    ).execute()
                    
                    current_data = current_data_result.get('values', [[]])[0]
                    
                    # Check if the transaction has changed (ignore timestamp)
                    # Compare first 8 columns (everything except timestamp)
                    changed = False
                    for i in range(min(len(current_data), 8)):
                        if i < len(tx_data) and str(current_data[i]) != str(tx_data[i]):
                            changed = True
                            break
                    
                    if changed:
                        # Update the existing row
                        updates.append({
                            'range': row_range,
                            'values': [tx_data]
                        })
                except Exception as e:
                    print(f"Error checking existing transaction {tx.id}: {e}")
                    # Add to new transactions as fallback
                    new_transactions.append(tx_data)
            else:
                # New transaction
                new_transactions.append(tx_data)
        
        results = {}
        
        # Process updates for existing transactions
        if updates:
            try:
                update_body = {
                    'valueInputOption': 'RAW',
                    'data': updates
                }
                update_result = self.sheet.values().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body=update_body
                ).execute()
                results['updated'] = len(updates)
            except Exception as e:
                print(f"Error updating existing transactions: {e}")
                results['update_error'] = str(e)
        
        # Insert new transactions at the top (after header row)
        if new_transactions:
            try:
                # Insert rows after header
                insert_body = {
                    'requests': [{
                        'insertRange': {
                            'range': {
                                'sheetId': sheet_id,  # Using the actual sheet ID
                                'startRowIndex': 1,  # After header row
                                'endRowIndex': 1 + len(new_transactions),
                                'startColumnIndex': 0,
                                'endColumnIndex': 9  # 9 columns
                            },
                            'shiftDimension': 'ROWS'
                        }
                    }]
                }
                
                # First, insert the rows
                self.sheet.batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body=insert_body
                ).execute()
                
                # Then, populate the inserted rows with data
                populate_body = {
                    'values': new_transactions
                }
                
                insert_result = self.sheet.values().update(
                    spreadsheetId=self.sheet_id,
                    range='Transactions!A2',  # Start after header
                    valueInputOption='RAW',
                    body=populate_body
                ).execute()
                
                results['inserted'] = len(new_transactions)
            except Exception as e:
                print(f"Error inserting new transactions: {e}")
                results['insert_error'] = str(e)
        
        return results

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
                account_id=tx.get('account_id', ''),
                date=tx.get('date', ''),
                account_name=tx.get('account_name', ''),
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

# Routes for HTML pages
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main index.html page"""
    index_path = templates_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text())
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Personal Budget Tracker</title>
        </head>
        <body>
            <h1>Personal Budget Tracker</h1>
            <p>Welcome to your personal budget tracker. The page template could not be found.</p>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=os.environ.get('DEBUG', 'False').lower() == 'true')