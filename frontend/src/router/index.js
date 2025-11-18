import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import ProfileView from '../views/ProfileView.vue'
import ContactsView from '../views/ContactsView.vue'
import ContactCreateView from '../views/ContactCreateView.vue'
import ContactEditView from '../views/ContactEditView.vue'

const routes = [
  {
    path: '/',
    redirect: '/contacts',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { public: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { public: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  {
    path: '/contacts',
    name: 'Contacts',
    component: ContactsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/contacts/new',
    name: 'ContactCreate',
    component: ContactCreateView,
    meta: { requiresAuth: true },
  },
  {
    path: '/contacts/:id/edit',
    name: 'ContactEdit',
    component: ContactEditView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Route guard
router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuth()

  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    // Redirect to login if not authenticated
    next('/login')
  } else if (to.meta.public && isAuthenticated.value) {
    // Redirect to contacts if already authenticated and trying to access public routes
    next('/contacts')
  } else {
    // Allow navigation
    next()
  }
})

export default router
