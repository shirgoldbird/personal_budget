# Personal Budgeting Backend

A simple and efficient backend for a personal budgeting application that connects to your bank accounts through Teller API, allows transaction categorization, and exports to Google Sheets.

## Features

- Secure connection to bank accounts via Teller API
- Auto-categorization of transactions based on description patterns
- Custom transaction categories with color coding
- Export of transactions to Google Sheets
- RESTful API for future frontend integration

## Prerequisites

- Python 3.8 or higher
- A Teller API account with certificates (for production use)
- A Google Cloud Platform account with Sheets API enabled
- A Google Sheet set up with a "Transactions" tab

### Set up Teller

Sign up at https://teller.io/ and save the downloaded credentials.

### Set up Google Sheets

1. Create a Google Cloud Platform project
2. Enable the Google Sheets API
3. Create a service account and download the credentials JSON file
4. Create a Google Sheet and share it with the service account email

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

### 4. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration. We recommend creating a `creds/` directory to store the various files (anything in there will be automatically git ignored).

```
# Teller API Configuration
TELLER_BASE_URL=https://api.teller.io
TELLER_CERT_PATH=path/to/cert.pem
TELLER_KEY_PATH=path/to/key.pem

# Google Sheets Configuration
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDS_PATH=path/to/google_credentials.json

# App Configuration
PORT=5000
DEBUG=False
```

### 5. Set up categories and transaction mappings

Create initial category and mapping files:

```bash
cp categories.json.example categories.json
cp transaction_mappings.json.example transaction_mappings.json
```

## Running the application

```bash
# Development mode
python app.py

# Production mode with gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

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