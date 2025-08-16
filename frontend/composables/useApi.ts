import { useUserStore } from '~/stores/user'

export const useApi = () => {
  const userStore = useUserStore()
  const config = useRuntimeConfig()
  
  const baseURL = config.public.apiBaseUrl
  
  const getHeaders = () => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    if (userStore.accessToken) {
      headers['Authorization'] = `Bearer ${userStore.accessToken}`
    }
    
    return headers
  }
  
  const handleResponse = async (response: Response) => {
    if (!response.ok) {
      let errorMessage = 'An error occurred'
      
      try {
        const errorData = await response.json()
        errorMessage = errorData.error || errorMessage
      } catch {
        // If we can't parse the error response, use the status text
        errorMessage = response.statusText || errorMessage
      }
      
      // Handle authentication errors
      if (response.status === 401) {
        // Try to refresh token
        try {
          await userStore.refreshAccessToken()
          // Retry the request with new token
          return true
        } catch (refreshError) {
          // Refresh failed, redirect to login
          await userStore.logout()
          await navigateTo('/login')
          throw new Error('Authentication expired. Please log in again.')
        }
      }
      
      throw new Error(errorMessage)
    }
    
    return response.json()
  }
  
  const apiCall = async <T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    const url = `${baseURL}${endpoint}`
    
    const requestOptions: RequestInit = {
      headers: getHeaders(),
      ...options
    }
    
    try {
      const response = await fetch(url, requestOptions)
      return await handleResponse(response)
    } catch (error) {
      console.error(`API call failed for ${endpoint}:`, error)
      throw error
    }
  }
  
  const get = <T>(endpoint: string, params?: Record<string, any>): Promise<T> => {
    let url = endpoint
    
    if (params) {
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value))
        }
      })
      url += `?${searchParams.toString()}`
    }
    
    return apiCall<T>(url, { method: 'GET' })
  }
  
  const post = <T>(endpoint: string, data?: any): Promise<T> => {
    return apiCall<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    })
  }
  
  const put = <T>(endpoint: string, data?: any): Promise<T> => {
    return apiCall<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    })
  }
  
  const del = <T>(endpoint: string): Promise<T> => {
    return apiCall<T>(endpoint, { method: 'DELETE' })
  }
  
  const patch = <T>(endpoint: string, data?: any): Promise<T> => {
    return apiCall<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined
    })
  }
  
  // Specialized API methods
  const uploadFile = async <T>(
    endpoint: string,
    file: File,
    additionalData?: Record<string, any>
  ): Promise<T> => {
    const formData = new FormData()
    formData.append('file', file)
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, String(value))
      })
    }
    
    const headers = getHeaders()
    delete headers['Content-Type'] // Let browser set multipart boundary
    
    return apiCall<T>(endpoint, {
      method: 'POST',
      headers,
      body: formData
    })
  }
  
  const downloadFile = async (endpoint: string, filename?: string): Promise<void> => {
    const url = `${baseURL}${endpoint}`
    
    try {
      const response = await fetch(url, {
        headers: getHeaders()
      })
      
      if (!response.ok) {
        throw new Error('Download failed')
      }
      
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      console.error('File download failed:', error)
      throw error
    }
  }
  
  // Pagination helper
  const getPaginated = async <T>(
    endpoint: string,
    page: number = 1,
    perPage: number = 10,
    additionalParams?: Record<string, any>
  ): Promise<{ data: T[]; pagination: any }> => {
    const params = {
      page,
      per_page: perPage,
      ...additionalParams
    }
    
    return get(endpoint, params)
  }
  
  // Search helper
  const search = async <T>(
    endpoint: string,
    query: string,
    fields?: string[],
    additionalParams?: Record<string, any>
  ): Promise<T[]> => {
    const params = {
      search: query,
      fields: fields?.join(','),
      ...additionalParams
    }
    
    return get(endpoint, params)
  }
  
  return {
    get,
    post,
    put,
    del,
    patch,
    uploadFile,
    downloadFile,
    getPaginated,
    search,
    baseURL
  }
}

// Specialized API composables
export const useInvoiceApi = () => {
  const api = useApi()
  
  return {
    getInvoices: (params?: any) => api.get('/invoices', params),
    getInvoice: (id: string) => api.get(`/invoices/${id}`),
    createInvoice: (data: any) => api.post('/invoices', data),
    updateInvoice: (id: string, data: any) => api.put(`/invoices/${id}`, data),
    deleteInvoice: (id: string) => api.del(`/invoices/${id}`),
    sendInvoice: (id: string) => api.post(`/invoices/${id}/send`),
    downloadPdf: (id: string) => api.downloadFile(`/invoices/${id}/pdf`, `invoice-${id}.pdf`)
  }
}

export const useClientApi = () => {
  const api = useApi()
  
  return {
    getClients: (params?: any) => api.get('/clients', params),
    getClient: (id: string) => api.get(`/clients/${id}`),
    createClient: (data: any) => api.post('/clients', data),
    updateClient: (id: string, data: any) => api.put(`/clients/${id}`, data),
    deleteClient: (id: string) => api.del(`/clients/${id}`),
    getClientTags: () => api.get('/clients/tags')
  }
}

export const usePaymentApi = () => {
  const api = useApi()
  
  return {
    createStripeIntent: (data: any) => api.post('/payments/stripe/create-intent', data),
    createPayPalOrder: (data: any) => api.post('/payments/paypal/create-order', data),
    getPayment: (id: string) => api.get(`/payments/${id}`),
    getInvoicePayments: (invoiceId: string) => api.get(`/payments/invoice/${invoiceId}`)
  }
}

export const useReportApi = () => {
  const api = useApi()
  
  return {
    getDashboard: (params?: any) => api.get('/reports/dashboard', params),
    getRevenue: (params?: any) => api.get('/reports/revenue', params),
    getClients: (params?: any) => api.get('/reports/clients', params),
    exportReport: (data: any) => api.post('/reports/export', data)
  }
}
