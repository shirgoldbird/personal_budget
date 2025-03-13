import { createApp } from "vue";
import { pinia } from "./stores";
import router from "./router";
import App from "./App.vue";
import "./style.css";

// Create Vue app instance
const app = createApp(App);

// Use plugins
app.use(pinia);
app.use(router);

// Mount app to DOM
app.mount("#app");
