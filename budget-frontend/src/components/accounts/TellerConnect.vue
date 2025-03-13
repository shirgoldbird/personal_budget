<template>
  <div>
    <button @click="openTellerConnect" class="btn btn-primary">
      <span v-if="!loading">Connect Bank Account</span>
      <span v-else>Connecting...</span>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useBankStore } from '../../stores/bankStore';

const bankStore = useBankStore();
const loading = ref(false);
const tellerConnect = ref(null);

onMounted(() => {
  // Load Teller Connect script if not already loaded
  if (!document.getElementById('teller-connect-script')) {
    const script = document.createElement('script');
    script.id = 'teller-connect-script';
    script.src = 'https://cdn.teller.io/connect/connect.js';
    script.async = true;
    
    script.onload = initializeTellerConnect;
    
    document.body.appendChild(script);
  } else {
    initializeTellerConnect();
  }
});

function initializeTellerConnect() {
  if (window.TellerConnect) {
    tellerConnect.value = window.TellerConnect.setup({
      applicationId: import.meta.env.VITE_TELLER_APP_ID || 'app_pb2s7s7kc4918jnrms000',
      environment: import.meta.env.VITE_TELLER_ENVIRONMENT || 'sandbox',
      products: ["transactions", "balance", "identity", "verify"],
      
      onInit: function() {
        console.log("Teller Connect has initialized");
      },
      
      // Called when the user completes enrollment successfully
      onSuccess: async function(enrollment) {
        loading.value = true;
        console.log("Enrollment successful:", enrollment);
        
        try {
          await bankStore.storeToken(enrollment);
          console.log("Token stored successfully");
        } catch (error) {
          console.error("Error storing token:", error);
        } finally {
          loading.value = false;
        }
      },
      
      // Called when the user exits without enrolling
      onExit: function() {
        console.log("User exited Teller Connect without enrolling");
        loading.value = false;
      },
      
      onFailure: function(failure) {
        console.log("Failure occurred", failure);
        loading.value = false;
      },
    });
  }
}

function openTellerConnect() {
  if (tellerConnect.value) {
    loading.value = true;
    tellerConnect.value.open();
  } else {
    console.error("Teller Connect not initialized");
  }
}
</script>