<template>
  <div class="relative">
    <!-- Notification Bell Button -->
    <button
      @click="toggleDropdown"
      class="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors duration-200"
      :class="{ 'bg-gray-100': isDropdownOpen }"
    >
      <BellIcon class="h-6 w-6" />
      
      <!-- Unread Badge -->
      <span
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
      
      <!-- Connection Status Indicator -->
      <span
        class="absolute -bottom-1 -right-1 h-3 w-3 rounded-full border-2 border-white"
        :class="isConnected ? 'bg-green-500' : 'bg-red-500'"
        :title="isConnected ? 'Connected' : 'Disconnected'"
      />
    </button>

    <!-- Notifications Dropdown -->
    <div
      v-if="isDropdownOpen"
      class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">
          Notifications
        </h3>
        <div class="flex items-center space-x-2">
          <button
            v-if="unreadCount > 0"
            @click="markAllAsRead"
            class="text-sm text-blue-600 hover:text-blue-800 font-medium"
            :disabled="isMarkingAllAsRead"
          >
            {{ isMarkingAllAsRead ? 'Marking...' : 'Mark all read' }}
          </button>
          <button
            @click="closeDropdown"
            class="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
      </div>

      <!-- Notifications List -->
      <div class="max-h-96 overflow-y-auto">
        <div v-if="isLoading" class="p-4 text-center text-gray-500">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-2">Loading notifications...</p>
        </div>
        
        <div v-else-if="notifications.length === 0" class="p-4 text-center text-gray-500">
          <BellSlashIcon class="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p>No notifications yet</p>
        </div>
        
        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="p-4 hover:bg-gray-50 transition-colors duration-150"
            :class="{ 'bg-blue-50': !notification.is_read }"
          >
            <div class="flex items-start space-x-3">
              <!-- Notification Icon -->
              <div class="flex-shrink-0">
                <div
                  class="h-8 w-8 rounded-full flex items-center justify-center"
                  :class="getNotificationIconClass(notification.notification_type)"
                >
                  <component
                    :is="getNotificationIcon(notification.notification_type)"
                    class="h-4 w-4 text-white"
                  />
                </div>
              </div>

              <!-- Notification Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between">
                  <p class="text-sm font-medium text-gray-900">
                    {{ notification.title }}
                  </p>
                  <div class="flex items-center space-x-2">
                    <span class="text-xs text-gray-500">
                      {{ formatTime(notification.created_at) }}
                    </span>
                    <button
                      v-if="!notification.is_read"
                      @click="markAsRead(notification.id)"
                      class="text-xs text-blue-600 hover:text-blue-800"
                    >
                      Mark read
                    </button>
                  </div>
                </div>
                <p class="text-sm text-gray-600 mt-1">
                  {{ notification.message }}
                </p>
                
                <!-- Action Buttons -->
                <div v-if="notification.data.action" class="mt-2 flex space-x-2">
                  <button
                    v-if="notification.data.invoice_id"
                    @click="viewInvoice(notification.data.invoice_id)"
                    class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 transition-colors"
                  >
                    View Invoice
                  </button>
                  <button
                    v-if="notification.data.client_id"
                    @click="viewClient(notification.data.client_id)"
                    class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200 transition-colors"
                  >
                    View Client
                  </button>
                </div>
              </div>

              <!-- Delete Button -->
              <button
                @click="deleteNotification(notification.id)"
                class="text-gray-400 hover:text-red-600 transition-colors"
                title="Delete notification"
              >
                <TrashIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div v-if="notifications.length > 0" class="p-4 border-t border-gray-200">
        <button
          @click="viewAllNotifications"
          class="w-full text-center text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          View all notifications
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  BellIcon, 
  BellSlashIcon, 
  XMarkIcon, 
  TrashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '~/stores/notifications'
import { useUserStore } from '~/stores/user'
import type { Notification } from '~/types/notification'

// Props
interface Props {
  maxNotifications?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxNotifications: 10
})

// Composables
const notificationStore = useNotificationStore()
const userStore = useUserStore()

// State
const isDropdownOpen = ref(false)
const isMarkingAllAsRead = ref(false)

// Computed
const notifications = computed(() => 
  notificationStore.notifications.slice(0, props.maxNotifications)
)
const unreadCount = computed(() => notificationStore.unreadCount)
const isLoading = computed(() => notificationStore.isLoading)
const isConnected = computed(() => notificationStore.isConnected)

// Methods
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
  if (isDropdownOpen.value) {
    loadNotifications()
  }
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const loadNotifications = async () => {
  try {
    await notificationStore.fetchNotifications(1, props.maxNotifications)
  } catch (error) {
    console.error('Error loading notifications:', error)
  }
}

const markAsRead = async (notificationId: string) => {
  try {
    await notificationStore.markAsRead(notificationId)
  } catch (error) {
    console.error('Error marking notification as read:', error)
  }
}

const markAllAsRead = async () => {
  try {
    isMarkingAllAsRead.value = true
    await notificationStore.markAllAsRead()
  } catch (error) {
    console.error('Error marking all notifications as read:', error)
  } finally {
    isMarkingAllAsRead.value = false
  }
}

const deleteNotification = async (notificationId: string) => {
  try {
    await notificationStore.deleteNotification(notificationId)
  } catch (error) {
    console.error('Error deleting notification:', error)
  }
}

const viewInvoice = (invoiceId: string) => {
  closeDropdown()
  navigateTo(`/invoices/${invoiceId}`)
}

const viewClient = (clientId: string) => {
  closeDropdown()
  navigateTo(`/clients/${clientId}`)
}

const viewAllNotifications = () => {
  closeDropdown()
  navigateTo('/notifications')
}

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'success':
      return CheckCircleIcon
    case 'warning':
      return ExclamationTriangleIcon
    case 'error':
      return XCircleIcon
    default:
      return InformationCircleIcon
  }
}

const getNotificationIconClass = (type: string) => {
  switch (type) {
    case 'success':
      return 'bg-green-500'
    case 'warning':
      return 'bg-yellow-500'
    case 'error':
      return 'bg-red-500'
    default:
      return 'bg-blue-500'
  }
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
  return date.toLocaleDateString()
}

// Click outside to close
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    isDropdownOpen.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Initialize notifications if user is authenticated
  if (userStore.isAuthenticated && userStore.user) {
    notificationStore.initializeSocket(userStore.user.id)
    notificationStore.fetchUnreadCount()
  }
  
  // Add click outside listener
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  notificationStore.disconnectSocket()
  document.removeEventListener('click', handleClickOutside)
})

// Watch for authentication changes
watch(() => userStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated && userStore.user) {
    notificationStore.initializeSocket(userStore.user.id)
    notificationStore.fetchUnreadCount()
  } else {
    notificationStore.disconnectSocket()
    notificationStore.clearNotifications()
  }
})
</script>
