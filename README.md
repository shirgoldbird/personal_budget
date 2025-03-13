# Personal Budget Tracker

A comprehensive personal finance application that connects to your bank accounts through the Teller API, categorizes transactions, visualizes spending patterns, and helps you manage your budget effectively.

<img width="1165" alt="Dashboard view showing spending overview" src="https://github.com/user-attachments/assets/10e3334e-ae3c-4b39-8da5-d80336fc13f8" />

<img width="1171" alt="Transactions page with filtering and categorization" src="https://github.com/user-attachments/assets/dcd9de9c-7845-456c-b59e-1a74fb948d77" />

<img width="1195" alt="Accounts view displaying connected banks" src="https://github.com/user-attachments/assets/14267c9b-3817-45e6-99d2-822e033f284d" />

<img width="1201" alt="Categories management page" src="https://github.com/user-attachments/assets/7c019b8f-15e1-47c0-a9bc-73cc4fd31dde" />

<img width="909" alt="Auto-categorization rules setup" src="https://github.com/user-attachments/assets/c139d8d8-cb90-4f01-8eb5-e8fb6580cc85" />

## Features

- **Bank Integration**: Secure connection to financial institutions via Teller API
- **Transaction Management**: View, search, and categorize your transactions
- **Automated Categorization**: Define rules to automatically categorize transactions based on description patterns 
- **Data Visualization**: Charts and graphs to visualize spending patterns
- **Category Management**: Create and customize transaction categories with color coding
- **Google Sheets Export**: Export transactions for additional analysis or record-keeping
- **Responsive Design**: Works on desktop and mobile devices
- **Multi-bank Support**: Connect and manage multiple bank accounts in one place

## Project Structure

The application consists of two main components:

- **Backend**: FastAPI application that handles API requests, Teller integration, and data processing
- **Frontend**: Vue.js application with a responsive UI for managing your finances

## Prerequisites

- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)
- A Teller API account with application ID ([Sign up here](https://teller.io))
- For production: Teller API certificates
- Optional: Google Cloud Platform account with Sheets API enabled (for Google Sheets export)

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/shirgoldbird/personal_budget.git
cd personal_budget
```

### 2. Backend Setup

#### Set up a virtual environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Run the setup script

```bash
python setup.py
```

This will create the required directories and copy example files to their proper locations.

#### Configure environment variables

Edit the `.env` file in the backend directory:

```
# Teller API Configuration
TELLER_BASE_URL=https://api.teller.io
TELLER_CERT_PATH=path/to/cert.pem
TELLER_KEY_PATH=path/to/key.pem

# Google Sheets Configuration (Optional)
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

#### Google Sheets Setup (Optional)

If you want to use the Google Sheets export feature:

1. Create a Google Cloud Platform project
2. Enable the Google Sheets API
3. Create a service account and download the credentials JSON file
4. Create a Google Sheet and share it with the service account email
5. Run the setup script:

```bash
python setup_google_sheet.py --creds path/to/credentials.json --sheet-name "My Budget Tracker"
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

#### Configure environment variables

Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:8000/api
VITE_TELLER_APP_ID=your_teller_app_id
VITE_TELLER_ENVIRONMENT=sandbox  # or development, production
```

## Running the Application

### Start the Backend

```bash
# From the backend directory
# Development mode with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or directly
python app.py
```

### Start the Frontend

```bash
# From the frontend directory
npm run dev
```

The frontend will be available at `http://localhost:5173` by default.

## Using the Application

1. Open your browser and navigate to the frontend URL
2. Click "Connect Bank Account" on the dashboard to launch Teller Connect
3. Follow the prompts to connect your bank account
4. After connecting, you'll see your accounts and transactions
5. Use the categories page to set up custom categories
6. Set up auto-categorization rules for recurring transactions
7. View your spending breakdown on the dashboard
8. Export transactions to Google Sheets if needed

## Development and Customization

### Backend API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Customization

- Edit `tailwind.config.js` to customize the theme colors
- Modify components in `src/components` to adjust the UI
- Add new pages by creating Vue components in `src/views` and updating the router

## Deployment

### Backend Deployment

#### Using Docker

A Dockerfile is not included in this version, but for containerization, you would:

1. Create a Dockerfile in the backend directory
2. Build the Docker image
3. Run with proper volume mounts for persistent storage

#### Hosting Providers

The backend can be deployed to:

- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk
- Google Cloud Run
- or any other Python application hosting service

### Frontend Deployment

Build the frontend for production:

```bash
cd frontend
npm run build
```

The built files will be in the `dist` directory and can be served using any static file server.

Popular hosting options for the frontend include:

- Netlify
- Vercel
- GitHub Pages
- Firebase Hosting
- AWS S3 + CloudFront

## Security Considerations

- The Teller client certificate is sensitive and should be kept secure
- Google API credentials should be protected
- Environment variables should never be committed to version control
- Always use HTTPS in production
- Consider adding user authentication for multi-user environments

## Teller API Integration Details

### Sandbox Mode

For testing, you can use Teller's sandbox environment:

1. Set `VITE_TELLER_ENVIRONMENT=sandbox` in your frontend `.env` file
2. Use the following credentials in Teller Connect:
   - Username: `verify.microdeposit` or any other Teller sandbox username
   - Password: `password`

### Production Mode

For production:

1. Set `VITE_TELLER_ENVIRONMENT=production` in your frontend `.env`
2. Ensure you have valid Teller API certificates
3. Update the backend `.env` file with your certificate paths

## License

MIT

---

This application is for personal use only. Always be careful with financial data and credentials.