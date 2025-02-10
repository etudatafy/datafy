import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import RegisterPage from './pages/RegisterPage.vue';
import LoginPage from './pages/LoginPage.vue';
import ChatPage from './pages/ChatPage.vue';

const routes = [
  { path: '/home', component: HomePage },
  { path: '/register', component: RegisterPage },
  { path: '/login', component: LoginPage },
  { path: '/chat', component: ChatPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;