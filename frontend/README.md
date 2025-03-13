# Personal Budget Tracker Frontend

A Vue.js frontend for the Personal Budget Tracker application that connects to your bank accounts, categorizes transactions, and helps you manage your finances.

## Features

- Connect to bank accounts via Teller API
- View all accounts in one dashboard
- Categorize transactions automatically and manually
- Track spending by category with visual charts
- Export transactions to Google Sheets
- Responsive design for mobile and desktop

## Tech Stack

- **Vue 3** with Composition API
- **Vite** for lightning-fast development
- **Tailwind CSS** for styling
- **Vue Router** for navigation
- **Pinia** for state management
- **Chart.js** and **vue-chartjs** for data visualization
- **Axios** for API requests

## Prerequisites

- Node.js 16+
- Backend API running (see the main repository README)
- Teller API credentials

## Installation

1. Clone this repository
```bash
git clone https://github.com/yourusername/budget-frontend.git
cd budget-frontend
```

2. Install dependencies
```bash
npm install
```

3. Create environment file from example
```bash
cp .env.example .env
```

4. Update environment variables in `.env`
```
VITE_API_URL=http://localhost:8000/api
VITE_TELLER_APP_ID=your_teller_app_id
VITE_TELLER_ENVIRONMENT=sandbox  # or development, production
```

## Development

Start the development server:
```bash
npm run dev
```

This will start the development server at http://localhost:5173/

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory and can be served using any static file server.

## Connecting with the Backend

This frontend is designed to work with the FastAPI backend from the main repository. Make sure the backend is running at the URL specified in your `.env` file.

## Usage Flow

1. **Dashboard**: Connect your bank accounts and view your financial overview
2. **Accounts**: View all your connected accounts
3. **Transactions**: View, search, and categorize your transactions
4. **Categories**: Manage categories and set up auto-categorization rules

## Customization

- Edit `tailwind.config.js` to change colors and theme
- Modify components in `src/components` to adjust UI

## Integration with Teller

The Teller Connect integration is in `src/components/accounts/TellerConnect.vue`. You'll need to update the `applicationId` with your own from the Teller Dashboard.

## License

MIT