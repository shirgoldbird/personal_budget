import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../components/dashboard/Dashboard.vue";
import AccountsView from "../views/AccountsView.vue";
import TransactionsView from "../views/TransactionsView.vue";
import CategoriesView from "../views/CategoriesView.vue";

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: Dashboard,
  },
  {
    path: "/accounts",
    name: "Accounts",
    component: AccountsView,
  },
  {
    path: "/transactions",
    name: "Transactions",
    component: TransactionsView,
  },
  {
    path: "/categories",
    name: "Categories",
    component: CategoriesView,
  },
  // Redirect any unmatched routes to the home page
  {
    path: "/:pathMatch(.*)*",
    redirect: { name: "Dashboard" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    // Always scroll to top when navigating
    return { top: 0 };
  },
});

export default router;
