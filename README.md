# Personal Budgeting Backend

A simple and efficient FastAPI backend for a personal budgeting application that connects to your bank accounts through Teller API, allows transaction categorization, and exports to Google Sheets.

<img width="1165" alt="image" src="https://github.com/user-attachments/assets/10e3334e-ae3c-4b39-8da5-d80336fc13f8" />
<img width="1171" alt="image" src="https://github.com/user-attachments/assets/dcd9de9c-7845-456c-b59e-1a74fb948d77" />
<img width="1195" alt="image" src="https://github.com/user-attachments/assets/14267c9b-3817-45e6-99d2-822e033f284d" />
<img width="1201" alt="image" src="https://github.com/user-attachments/assets/7c019b8f-15e1-47c0-a9bc-73cc4fd31dde" />
<img width="909" alt="image" src="https://github.com/user-attachments/assets/c139d8d8-cb90-4f01-8eb5-e8fb6580cc85" />

## Features

- Secure connection to bank accounts via Teller API
- Integration with Teller Connect for user authentication
- Management of multiple bank connection tokens
- Auto-categorization of transactions based on description patterns
- Custom transaction categories with color coding
- Export of transactions to Google Sheets
- Modern FastAPI backend with automatic OpenAPI documentation
- Simple web interface to connect to banks and manage transactions
- OpenAPI specification in JSON and YAML formats
- Type validation with Pydantic models
- RESTful API for future frontend integration

## Prerequisites

- Python 3.8 or higher
- A Teller API account with certificates (for production use)
- A Google Cloud Platform account with Sheets API enabled
- A Google Sheet set up with a "Transactions" tab

## Installation

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/personal-budgeting-backend.git
cd personal-budgeting-backend
```

### 2. Set up a virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the setup script

```bash
python setup.py
```

This will create the required directories and copy example files to their proper locations.

### 5. Configure environment variables

Edit the `.env` file with your configuration:

```
# Teller API Configuration
TELLER_BASE_URL=https://api.teller.io
TELLER_CERT_PATH=path/to/cert.pem
TELLER_KEY_PATH=path/to/key.pem

# Google Sheets Configuration
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDS_PATH=path/to/google_credentials.json

# App Configuration
PORT=8000
DEBUG=False

# File paths
CATEGORIES_FILE=categories.json
TRANSACTION_MAPPING_FILE=transaction_mappings.json
CREDS_DIR=creds
STATIC_DIR=static
HTML_TEMPLATE_DIR=templates
```

### 5. Set up categories and transaction mappings

Create initial category and mapping files:

```bash
cp categories.json.example categories.json
cp transaction_mappings.json.example transaction_mappings.json
```

### 6. Set up Google Sheets

1. Create a Google Cloud Platform project
2. Enable the Google Sheets API
3. Create a service account and download the credentials JSON file
4. Create a Google Sheet and share it with the service account email
5. Set up a sheet named "Transactions" with these columns:
   - Transaction ID
   - Date
   - Account ID
   - Description
   - Amount
   - Category
   - Notes
   - Timestamp

## Running the application

```bash
# Development mode with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or directly through the app
python app.py

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Using the Application

Once the server is running:

1. Open your browser and navigate to `http://localhost:8000`
2. Click "Connect a Bank" button to launch Teller Connect
3. Follow the prompts to connect your bank account
4. After connecting, you'll see your institutions listed
5. Click on an institution to view accounts
6. View and categorize transactions
7. Export transactions to Google Sheets

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

You can also access the OpenAPI specification directly:

- JSON format: http://localhost:8000/api/openapi.json
- YAML format: http://localhost:8000/api/openapi.yaml

The OpenAPI specification can be used by other tools or LLMs to generate frontend clients.

## Deployment Options

### Docker

A Dockerfile is not included in this version, but for containerization, you would:

1. Create a Dockerfile
2. Build the Docker image
3. Run with proper volume mounts for persistent storage

### Hosting Providers

This app can be deployed to:

- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk
- Google Cloud Run
- or any other Python application hosting service

Remember to set all environment variables in your hosting provider's dashboard.

## API Endpoints

### Accounts and Transactions

- `GET /api/accounts` - List all accounts
- `GET /api/accounts/{account_id}/transactions` - List transactions for an account

### Categories

- `GET /api/categories` - List all categories
- `POST /api/categories` - Create a new category
- `PUT /api/categories/{category_id}` - Update a category
- `DELETE /api/categories/{category_id}` - Delete a category

### Transaction Mappings

- `GET /api/mappings` - List all transaction mappings
- `POST /api/mappings` - Create a new mapping
- `DELETE /api/mappings/{pattern}` - Delete a mapping

### Transaction Processing

- `POST /api/transactions/categorize` - Auto-categorize transactions
- `POST /api/transactions/export` - Export transactions to Google Sheets

### Teller Token Management

- `POST /api/teller/store-token` - Store a token from Teller Connect
- `GET /api/teller/tokens` - List all stored Teller tokens
- `DELETE /api/teller/tokens/{institution_name}` - Delete a token for a specific institution

## Security Considerations

- The Teller client certificate is sensitive and should be kept secure
- Google API credentials are also sensitive
- Environment variables should never be committed to version control
- Always use HTTPS in production

## Local Development Tips

- Use `DEBUG=True` in your .env file for development
- You can use Teller's sandbox environment for testing

## Extending the Application

This backend is designed to be modular and extensible:

- Add authentication for multi-user support
- Implement more sophisticated transaction categorization
- Add budget tracking features
- Create reporting and visualization endpoints

## License

MIT

---

This application is for personal use only. Always be careful with financial data and credentials.
