import { createRouter, createWebHistory } from "vue-router";
import Bot from "../views/Bot.vue";
import Providers from "../views/Providers.vue";
import Agents from "../views/Agents.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/bot" },
    { path: "/bot", component: Bot },
    { path: "/providers", component: Providers },
    { path: "/agents", component: Agents },
  ],
});
