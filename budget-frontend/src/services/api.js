import axios from "axios";

// Create axios instance with base URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// API Service object with methods for each endpoint
export const apiService = {
  // Teller tokens and bank connection
  async listTellerTokens() {
    const response = await api.get("/teller/tokens");
    return response.data;
  },

  async storeTellerToken(enrollmentData) {
    const response = await api.post("/teller/store-token", enrollmentData);
    return response.data;
  },

  async deleteTellerToken(institutionName) {
    const response = await api.delete(
      `/teller/tokens/${encodeURIComponent(institutionName)}`
    );
    return response.data;
  },

  // Accounts
  async listAccounts(institution) {
    const params = institution ? { institution } : {};
    const response = await api.get("/accounts", { params });
    return response.data;
  },

  async getBalance(accountId, institution) {
    const params = institution ? { institution } : {};
    const response = await api.get(`/accounts/${accountId}/balances`, {
      params,
    });
    return response.data;
  },

  // Transactions
  async listTransactions(accountId, institution) {
    const params = institution ? { institution } : {};
    const response = await api.get(`/accounts/${accountId}/transactions`, {
      params,
    });
    return response.data;
  },

  async categorizeTransactions(transactions) {
    const response = await api.post("/transactions/categorize", {
      transactions,
    });
    return response.data;
  },

  async exportTransactions(transactions) {
    const response = await api.post("/transactions/export", { transactions });
    return response.data;
  },

  // Categories
  async getCategories() {
    const response = await api.get("/categories");
    return response.data;
  },

  async addCategory(category) {
    const response = await api.post("/categories", category);
    return response.data;
  },

  async updateCategory(categoryId, category) {
    const response = await api.put(`/categories/${categoryId}`, category);
    return response.data;
  },

  async deleteCategory(categoryId) {
    const response = await api.delete(`/categories/${categoryId}`);
    return response.data;
  },

  // Mappings for auto-categorization
  async getMappings() {
    const response = await api.get("/mappings");
    return response.data;
  },

  async addMapping(pattern, categoryId) {
    const response = await api.post("/mappings", {
      pattern,
      category_id: categoryId,
    });
    return response.data;
  },

  async deleteMapping(pattern) {
    const response = await api.delete(
      `/mappings/${encodeURIComponent(pattern)}`
    );
    return response.data;
  },
};

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response || error);
    return Promise.reject(error);
  }
);

export default api;
