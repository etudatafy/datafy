import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import RegisterPage from './pages/RegisterPage.vue';
import LoginPage from './pages/LoginPage.vue';
import ChatPage from './pages/ChatPage.vue';

const routes = [
  { path: '/ana-sayfa', component: HomePage },
  { path: '/kayit-ol', component: RegisterPage },
  { path: '/giris-yap', component: LoginPage },
  { path: '/yapay-zeka-yardim/:chatId?', component: ChatPage, props: true }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
