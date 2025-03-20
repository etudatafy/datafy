import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import RegisterPage from './pages/RegisterPage.vue';
import LoginPage from './pages/LoginPage.vue';
import ChatPage from './pages/ChatPage.vue';
import ExamEntry from './pages/ExamEntry.vue';
import CalenderPage from './pages/CalenderPage.vue';
import ProgressPage from './pages/ProgressPage.vue';

const routes = [
  { path: '/ana-sayfa', component: HomePage },
  { path: '/kayit-ol', component: RegisterPage },
  { path: '/giris-yap', component: LoginPage },
  { path: '/yapay-zeka-yardim/:chatId?', component: ChatPage, props: true },
  { path: '/deneme-gir/:id', component: ExamEntry, props: true },
  { path: '/takvim', component: CalenderPage },
  { path: '/gelisim-analiz', component: ProgressPage }

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;