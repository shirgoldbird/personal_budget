import { defineStore } from "pinia";
import { apiService } from "../services/api";

export const useBankStore = defineStore("bank", {
  state: () => ({
    institutions: [],
    accounts: [],
    selectedInstitution: null,
    selectedAccount: null,
    loading: false,
    error: null,
  }),

  getters: {
    hasInstitutions: (state) => state.institutions.length > 0,
    hasAccounts: (state) => state.accounts.length > 0,
  },

  actions: {
    async fetchInstitutions() {
      this.loading = true;
      this.error = null;

      try {
        this.institutions = await apiService.listTellerTokens();
      } catch (err) {
        this.error = err.message || "Failed to fetch institutions";
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async fetchAccounts(institution) {
      this.loading = true;
      this.error = null;

      try {
        this.accounts = await apiService.listAccounts(institution);
        this.selectedInstitution = institution;
      } catch (err) {
        this.error = err.message || "Failed to fetch accounts";
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },

    selectAccount(account) {
      this.selectedAccount = account;
    },

    async disconnectInstitution(institutionName) {
      this.loading = true;
      this.error = null;

      try {
        await apiService.deleteTellerToken(institutionName);
        // Remove the institution from the list
        this.institutions = this.institutions.filter(
          (inst) => inst.institution_name !== institutionName
        );

        // Clear accounts if they were from this institution
        if (this.selectedInstitution === institutionName) {
          this.accounts = [];
          this.selectedInstitution = null;
          this.selectedAccount = null;
        }
      } catch (err) {
        this.error = err.message || "Failed to disconnect institution";
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async storeToken(enrollmentData) {
      this.loading = true;
      this.error = null;

      try {
        await apiService.storeTellerToken(enrollmentData);
        await this.fetchInstitutions(); // Refresh the institutions list
      } catch (err) {
        this.error = err.message || "Failed to store token";
        console.error(this.error);
        throw err; // Re-throw to allow handling in the component
      } finally {
        this.loading = false;
      }
    },

    reset() {
      this.institutions = [];
      this.accounts = [];
      this.selectedInstitution = null;
      this.selectedAccount = null;
      this.error = null;
    },
  },
});
