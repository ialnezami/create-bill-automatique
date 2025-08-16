import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '~/types/notification'

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const socket = ref<any>(null)
  const isConnected = ref(false)

  // Getters
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.is_read)
  )
  
  const readNotifications = computed(() => 
    notifications.value.filter(n => n.is_read)
  )
  
  const hasUnread = computed(() => unreadCount.value > 0)

  // Actions
  const initializeSocket = (userId: string) => {
    try {
      // Initialize Socket.IO connection
      const { $io } = useNuxtApp()
      
      if ($io) {
        socket.value = $io
        
        // Join user room
        socket.value.emit('join', { user_id: userId })
        
        // Listen for notifications
        socket.value.on('notification', (notification: Notification) => {
          addNotification(notification)
          unreadCount.value++
        })
        
        // Listen for unread count updates
        socket.value.on('unread_count', (data: { count: number }) => {
          unreadCount.value = data.count
        })
        
        // Connection events
        socket.value.on('connect', () => {
          isConnected.value = true
          console.log('Connected to notification service')
        })
        
        socket.value.on('disconnect', () => {
          isConnected.value = false
          console.log('Disconnected from notification service')
        })
        
        isConnected.value = true
      }
    } catch (error) {
      console.error('Error initializing socket:', error)
    }
  }

  const disconnectSocket = () => {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
    }
  }

  const addNotification = (notification: Notification) => {
    // Add to beginning of list
    notifications.value.unshift(notification)
    
    // Keep only last 100 notifications
    if (notifications.value.length > 100) {
      notifications.value = notifications.value.slice(0, 100)
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      const { $api } = useNuxtApp()
      
      await $api.put(`/notifications/${notificationId}/read`)
      
      // Update local state
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      }
      
      // Update unread count
      if (unreadCount.value > 0) {
        unreadCount.value--
      }
      
      // Emit socket event
      if (socket.value) {
        socket.value.emit('mark_read', { 
          notification_id: notificationId,
          user_id: useUserStore().user?.id 
        })
      }
      
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      const { $api } = useNuxtApp()
      
      await $api.put('/notifications/mark-all-read')
      
      // Update local state
      notifications.value.forEach(n => {
        n.is_read = true
        n.read_at = new Date().toISOString()
      })
      
      unreadCount.value = 0
      
      // Emit socket event
      if (socket.value) {
        socket.value.emit('mark_all_read', { 
          user_id: useUserStore().user?.id 
        })
      }
      
    } catch (error) {
      console.error('Error marking all notifications as read:', error)
    }
  }

  const deleteNotification = async (notificationId: string) => {
    try {
      const { $api } = useNuxtApp()
      
      await $api.delete(`/notifications/${notificationId}`)
      
      // Remove from local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index > -1) {
        const notification = notifications.value[index]
        if (!notification.is_read && unreadCount.value > 0) {
          unreadCount.value--
        }
        notifications.value.splice(index, 1)
      }
      
    } catch (error) {
      console.error('Error deleting notification:', error)
    }
  }

  const fetchNotifications = async (page = 1, perPage = 20, unreadOnly = false) => {
    try {
      isLoading.value = true
      
      const { $api } = useNuxtApp()
      
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
        unread_only: unreadOnly.toString()
      })
      
      const response = await $api.get(`/notifications?${params}`)
      
      if (page === 1) {
        // Replace notifications for first page
        notifications.value = response.notifications
      } else {
        // Append notifications for subsequent pages
        notifications.value.push(...response.notifications)
      }
      
      return response
      
    } catch (error) {
      console.error('Error fetching notifications:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const { $api } = useNuxtApp()
      
      const response = await $api.get('/notifications/unread-count')
      unreadCount.value = response.unread_count
      
    } catch (error) {
      console.error('Error fetching unread count:', error)
    }
  }

  const clearNotifications = () => {
    notifications.value = []
    unreadCount.value = 0
  }

  const showToast = (notification: Notification) => {
    const { $toast } = useNuxtApp()
    
    if ($toast) {
      const toastType = notification.type === 'error' ? 'error' : 
                       notification.type === 'warning' ? 'warning' : 
                       notification.type === 'success' ? 'success' : 'info'
      
      $toast[toastType](notification.message, {
        title: notification.title,
        timeout: 5000,
        closeOnClick: true,
        pauseOnFocusLoss: true
      })
    }
  }

  return {
    // State
    notifications,
    unreadCount,
    isLoading,
    socket,
    isConnected,
    
    // Getters
    unreadNotifications,
    readNotifications,
    hasUnread,
    
    // Actions
    initializeSocket,
    disconnectSocket,
    addNotification,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    fetchNotifications,
    fetchUnreadCount,
    clearNotifications,
    showToast
  }
})
