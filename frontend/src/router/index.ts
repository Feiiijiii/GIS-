import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomeView from '../views/HomeView.vue'
import Register from '../components/Register.vue'
import Login from '../components/Login.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      props: (route) => ({
        showSpots: route.query.showSpots === 'true'
      }),
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/spots-detail',
      name: 'spots-detail',
      component: () => import('../views/SpotsDetailView.vue'),
      props: (route) => ({
        showSpots: true
      }),
      meta: { requiresAuth: true }
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    // 添加服务相关路由
    {
      path: '/hotels',
      name: 'hotels',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/homestays',
      name: 'homestays',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/bus-stops',
      name: 'bus-stops',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/metro-stations',
      name: 'metro-stations',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/parking-lots',
      name: 'parking-lots',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/sichuan-food',
      name: 'sichuan-food',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/hotpot',
      name: 'hotpot',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/snacks',
      name: 'snacks',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/western-food',
      name: 'western-food',
      component: HomeView,
      meta: { requiresAuth: true }
    }
  ],
})

// 添加导航守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果页面需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查用户是否已登录
    if (!authStore.isAuthenticated) {
      // 如果没有登录，重定向到登录页面
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    // 如果已登录且尝试访问登录/注册页面，重定向到首页
    if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      next({ path: '/' })
    } else {
      next()
    }
  }
})

export default router
