export default defineNuxtRouteMiddleware((to, from) => {
  const userStore = useUserStore()
  
  // Check if user is authenticated
  if (!userStore.isAuthenticated) {
    // Try to initialize auth from stored tokens
    userStore.initializeAuth().then((isAuthenticated) => {
      if (!isAuthenticated) {
        // Redirect to login if not authenticated
        return navigateTo('/login')
      }
    }).catch(() => {
      // If initialization fails, redirect to login
      return navigateTo('/login')
    })
  }
})

export default defineNuxtRouteMiddleware((to, from) => {
  const userStore = useUserStore()
  
  // Check if user is authenticated
  if (!userStore.isAuthenticated) {
    // Try to initialize auth from stored tokens
    userStore.initializeAuth().then((isAuthenticated) => {
      if (!isAuthenticated) {
        // Redirect to login if not authenticated
        return navigateTo('/login')
      }
    }).catch(() => {
      // If initialization fails, redirect to login
      return navigateTo('/login')
    })
  }
})
