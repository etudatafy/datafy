import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import RegisterPage from './pages/RegisterPage.vue';
import LoginPage from './pages/LoginPage.vue';
import ChatPage from './pages/ChatPage.vue';
import ExamEntry from './pages/ExamEntry.vue';
import CalenderPage from './pages/CalenderPage.vue';
import ProgressPage from './pages/ProgressPage.vue';
import NotFoundPage from './pages/NotFoundPage.vue';
import FaqPage from './pages/FaqPage.vue';

const routes = [
  { path: '/ana-sayfa', component: HomePage },
  { path: '/kayit-ol', component: RegisterPage },
  { path: '/giris-yap', component: LoginPage },
  { path: '/yapay-zeka-yardim/:chatId?', component: ChatPage, props: true },
  { path: '/deneme-gir/:id', component: ExamEntry, props: true },
  { path: '/takvim', component: CalenderPage },
  { path: '/gelisim-analiz', component: ProgressPage },
  { path: '/sayfa-bulunamadi', component: NotFoundPage },
  { path: '/sikca-sorulan-sorular', component: FaqPage },
  { path: '/:pathMatch(.*)*', redirect: '/sayfa-bulunamadi' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('jwt_token');
  const isAuth = !!token;
  const publicPages = ['/giris-yap', '/kayit-ol', '/sayfa-bulunamadi'];

  if (!isAuth && !publicPages.includes(to.path)) {
    return next('/giris-yap');
  }

  if (isAuth && ['/giris-yap', '/kayit-ol'].includes(to.path)) {
    return next('/ana-sayfa');
  }

  next();
});

export default router;
