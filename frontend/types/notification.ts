export interface Notification {
  id: string
  user: string
  title: string
  message: string
  notification_type: 'info' | 'success' | 'warning' | 'error'
  data: Record<string, any>
  is_read: boolean
  read_at?: string
  created_at: string
  updated_at: string
}

export interface NotificationResponse {
  notifications: Notification[]
  pagination: {
    page: number
    per_page: number
    total: number
    pages: number
  }
}

export interface UnreadCountResponse {
  unread_count: number
}

export interface MarkAsReadResponse {
  message: string
  notification: Notification
}

export interface MarkAllAsReadResponse {
  message: string
}

export interface DeleteNotificationResponse {
  message: string
}
