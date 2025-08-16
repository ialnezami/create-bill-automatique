<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Logo and main nav -->
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <NuxtLink to="/" class="text-2xl font-bold text-primary-600">
                InvoicePro
              </NuxtLink>
            </div>
            
            <!-- Navigation links -->
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <NuxtLink 
                to="/dashboard" 
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                :class="[
                  $route.path === '/dashboard' 
                    ? 'border-primary-500 text-gray-900' 
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                ]"
              >
                Dashboard
              </NuxtLink>
              <NuxtLink 
                to="/invoices" 
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                :class="[
                  $route.path.startsWith('/invoices') 
                    ? 'border-primary-500 text-gray-900' 
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                ]"
              >
                Invoices
              </NuxtLink>
              <NuxtLink 
                to="/clients" 
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                :class="[
                  $route.path.startsWith('/clients') 
                    ? 'border-primary-500 text-gray-900' 
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                ]"
              >
                Clients
              </NuxtLink>
              <NuxtLink 
                to="/reports" 
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                :class="[
                  $route.path.startsWith('/reports') 
                    ? 'border-primary-500 text-gray-900' 
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                ]"
              >
                Reports
              </NuxtLink>
            </div>
          </div>
          
          <!-- Right side -->
          <div class="hidden sm:ml-6 sm:flex sm:items-center">
            <!-- Profile dropdown -->
            <div v-if="userStore.isAuthenticated" class="ml-3 relative">
              <div>
                <button 
                  @click="profileDropdownOpen = !profileDropdownOpen"
                  class="max-w-xs bg-white rounded-full flex items-center text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  <span class="sr-only">Open user menu</span>
                  <div class="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center">
                    <span class="text-white font-medium text-sm">
                      {{ userStore.user?.first_name?.charAt(0) }}{{ userStore.user?.last_name?.charAt(0) }}
                    </span>
                  </div>
                </button>
              </div>
              
              <!-- Profile dropdown menu -->
              <div 
                v-if="profileDropdownOpen"
                class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
                role="menu"
              >
                <NuxtLink 
                  to="/profile" 
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  role="menuitem"
                  @click="profileDropdownOpen = false"
                >
                  Your Profile
                </NuxtLink>
                <NuxtLink 
                  to="/settings" 
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  role="menuitem"
                  @click="profileDropdownOpen = false"
                >
                  Settings
                </NuxtLink>
                <button 
                  @click="logout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  Sign out
                </button>
              </div>
            </div>
            
            <!-- Login/Register buttons -->
            <div v-else class="flex space-x-4">
              <NuxtLink 
                to="/login" 
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200"
              >
                Sign in
              </NuxtLink>
              <NuxtLink 
                to="/register" 
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                Sign up
              </NuxtLink>
            </div>
          </div>
          
          <!-- Mobile menu button -->
          <div class="-mr-2 flex items-center sm:hidden">
            <button 
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
            >
              <span class="sr-only">Open main menu</span>
              <svg 
                class="h-6 w-6" 
                :class="{ 'hidden': mobileMenuOpen, 'block': !mobileMenuOpen }"
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg 
                class="h-6 w-6" 
                :class="{ 'block': mobileMenuOpen, 'hidden': !mobileMenuOpen }"
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Mobile menu -->
      <div v-if="mobileMenuOpen" class="sm:hidden">
        <div class="pt-2 pb-3 space-y-1">
          <NuxtLink 
            to="/dashboard" 
            class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
            :class="[
              $route.path === '/dashboard' 
                ? 'bg-primary-50 border-primary-500 text-primary-700' 
                : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
            ]"
            @click="mobileMenuOpen = false"
          >
            Dashboard
          </NuxtLink>
          <NuxtLink 
            to="/invoices" 
            class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
            :class="[
              $route.path.startsWith('/invoices') 
                ? 'bg-primary-50 border-primary-500 text-primary-700' 
                : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
            ]"
            @click="mobileMenuOpen = false"
          >
            Invoices
          </NuxtLink>
          <NuxtLink 
            to="/clients" 
            class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
            :class="[
              $route.path.startsWith('/clients') 
                ? 'bg-primary-50 border-primary-500 text-primary-700' 
                : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
            ]"
            @click="mobileMenuOpen = false"
          >
            Clients
          </NuxtLink>
          <NuxtLink 
            to="/reports" 
            class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
            :class="[
              $route.path.startsWith('/reports') 
                ? 'bg-primary-50 border-primary-500 text-primary-700' 
                : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
            ]"
            @click="mobileMenuOpen = false"
          >
            Reports
          </NuxtLink>
        </div>
        
        <!-- Mobile profile menu -->
        <div v-if="userStore.isAuthenticated" class="pt-4 pb-3 border-t border-gray-200">
          <div class="flex items-center px-4">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center">
                <span class="text-white font-medium">
                  {{ userStore.user?.first_name?.charAt(0) }}{{ userStore.user?.last_name?.charAt(0) }}
                </span>
              </div>
            </div>
            <div class="ml-3">
              <div class="text-base font-medium text-gray-800">
                {{ userStore.user?.first_name }} {{ userStore.user?.last_name }}
              </div>
              <div class="text-sm font-medium text-gray-500">
                {{ userStore.user?.email }}
              </div>
            </div>
          </div>
          <div class="mt-3 space-y-1">
            <NuxtLink 
              to="/profile" 
              class="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              @click="mobileMenuOpen = false"
            >
              Your Profile
            </NuxtLink>
            <NuxtLink 
              to="/settings" 
              class="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              @click="mobileMenuOpen = false"
            >
              Settings
            </NuxtLink>
            <button 
              @click="logout"
              class="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <NuxtPage />
    </main>
    
    <!-- Toast notifications -->
    <Toast />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '~/stores/user'
import Toast from 'vue-toastification'

// Store
const userStore = useUserStore()

// Reactive state
const mobileMenuOpen = ref(false)
const profileDropdownOpen = ref(false)

// Methods
const logout = async () => {
  await userStore.logout()
  await navigateTo('/login')
}

// Lifecycle
onMounted(() => {
  // Close dropdowns when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
      profileDropdownOpen.value = false
    }
  })
})
</script>

<style>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Smooth transitions */
* {
  transition: all 0.2s ease-in-out;
}

/* Focus styles */
.focus-ring:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  box-shadow: 0 0 0 2px #3b82f6;
}
</style>
