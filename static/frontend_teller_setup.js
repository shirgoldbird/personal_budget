// Example JavaScript code to implement in your frontend
// This shows how to initialize Teller Connect and handle the enrollment

const API_BASE_URL = 'http://localhost:8000/api';

function setupTellerConnect() {
    // Initialize Teller Connect
    const tellerConnect = TellerConnect.setup({
      applicationId: 'app_pb2s7s7kc4918jnrms000', // Replace with your Teller application ID
      environment: 'sandbox', // Use "development" or "production" for real data
      //products: ["transactions", "balance", "identity", "verify"], // Add needed products

      onInit: function () {
        console.log("Teller Connect has initialized");
      },

      // Called when the user completes enrollment successfully
      onSuccess: async function (enrollment) {
        console.log("Enrollment successful:", enrollment);

        try {
          // Send the enrollment data to your backend
          const response = await fetch(`${API_BASE_URL}/teller/store-token`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(enrollment),
          });

          const result = await response.json();

          if (result.success) {
            console.log("Token stored successfully");
            // Update UI to show the new connection or redirect to accounts page
            loadInstitutions();
          } else {
            console.error("Failed to store token:", result);
            alert("Failed to store your bank connection. Please try again.");
          }
        } catch (error) {
          console.error("Error storing token:", error);
          alert("An error occurred while saving your bank connection.");
        }
      },

      // Called when the user exits without enrolling
      onExit: function () {
        console.log("User exited Teller Connect without enrolling");
      },

      onFailure: function (failure) {
        console.log("Failure occurred", failure);
      },
    });
    
    return tellerConnect;
}

// Function to load and display connected institutions
async function loadInstitutions() {
    try {
        const response = await fetch(`${API_BASE_URL}/teller/tokens`);
        const institutions = await response.json();
        
        const institutionsList = document.getElementById('institutions-list');
        institutionsList.innerHTML = '';
        
        if (institutions.length === 0) {
            institutionsList.innerHTML = '<p>No bank accounts connected. Click "Connect a Bank" to get started.</p>';
            return;
        }
        
        institutions.forEach(institution => {
            const item = document.createElement('div');
            item.className = 'institution-item';
            item.innerHTML = `
                <h3>${institution.institution_name}</h3>
                <p>Connected: ${new Date(institution.created_at).toLocaleDateString()}</p>
                <button class="view-accounts-btn" data-institution="${institution.institution_name}">View Accounts</button>
                <button class="disconnect-btn" data-institution="${institution.institution_name}">Disconnect</button>
            `;
            institutionsList.appendChild(item);
        });
        
        // Add event listeners for buttons
        document.querySelectorAll('.view-accounts-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                const institutionName = e.target.dataset.institution;
                await loadAccounts(institutionName);
            });
        });
        
        document.querySelectorAll('.disconnect-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                const institutionName = e.target.dataset.institution;
                await disconnectInstitution(institutionName);
            });
        });
        
    } catch (error) {
        console.error("Error loading institutions:", error);
    }
}

// Function to load accounts for a specific institution
async function loadAccounts(institutionName) {
    try {
        const response = await fetch(`${API_BASE_URL}/accounts?institution=${encodeURIComponent(institutionName)}`);
        const accounts = await response.json();
        
        // Display accounts...
        console.log("Accounts:", accounts);
        
        // Implement your UI here to show accounts
        
    } catch (error) {
        console.error("Error loading accounts:", error);
    }
}

// Function to disconnect an institution
async function disconnectInstitution(institutionName) {
    if (!confirm(`Are you sure you want to disconnect ${institutionName}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/teller/tokens/${encodeURIComponent(institutionName)}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`Disconnected ${institutionName} successfully`);
            // Reload the institutions list
            loadInstitutions();
        } else {
            console.error("Failed to disconnect institution:", result);
            alert("Failed to disconnect bank. Please try again.");
        }
    } catch (error) {
        console.error("Error disconnecting institution:", error);
    }
}

// Function to load transactions for a specific account
async function loadTransactions(accountId, institutionName) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/accounts/${accountId}/transactions?institution=${encodeURIComponent(institutionName)}`
        );
        const transactions = await response.json();
        
        // Display transactions...
        console.log("Transactions:", transactions);
        
        // Implement your UI for transaction display and categorization
        
    } catch (error) {
        console.error("Error loading transactions:", error);
    }
}

// Function to categorize and export transactions
async function categorizeAndExportTransactions(transactions) {
    try {
        // First, auto-categorize the transactions
        const categorizeResponse = await fetch(`${API_BASE_URL}/transactions/categorize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transactions })
        });
        
        const categorizedTransactions = await categorizeResponse.json();
        
        // Then export them to Google Sheets
        const exportResponse = await fetch(`${API_BASE_URL}/transactions/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transactions: categorizedTransactions })
        });
        
        const exportResult = await exportResponse.json();
        
        if (exportResult.updatedRange) {
            console.log("Transactions exported successfully to Google Sheets");
            alert("Transactions exported successfully to Google Sheets");
        } else {
            console.error("Failed to export transactions:", exportResult);
            alert("Failed to export transactions to Google Sheets");
        }
        
    } catch (error) {
        console.error("Error categorizing and exporting transactions:", error);
    }
}

// Initialize everything when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Set up Teller Connect button
    const connectButton = document.getElementById('connect-bank-btn');
    const tellerConnect = setupTellerConnect();
    
    connectButton.addEventListener('click', function() {
        tellerConnect.open();
    });
    
    // Load existing institutions
    loadInstitutions();
});