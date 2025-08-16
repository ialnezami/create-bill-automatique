export default defineNuxtRouteMiddleware((to, from) => {
  const userStore = useUserStore()
  
  // If user is already authenticated, redirect to dashboard
  if (userStore.isAuthenticated) {
    return navigateTo('/dashboard')
  }
})
