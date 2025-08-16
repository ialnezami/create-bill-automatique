import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Language {
  code: string
  name: string
  flag?: string
}

export const useLanguageStore = defineStore('language', () => {
  // State
  const currentLanguage = ref('en')
  const supportedLanguages = ref<Language[]>([
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'it', name: 'Italiano', flag: '🇮🇹' },
    { code: 'pt', name: 'Português', flag: '🇵🇹' },
    { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
    { code: 'pl', name: 'Polski', flag: '🇵🇱' },
    { code: 'ru', name: 'Русский', flag: '🇷🇺' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'ko', name: '한국어', flag: '🇰🇷' },
    { code: 'zh', name: '中文', flag: '🇨🇳' },
    { code: 'ar', name: 'العربية', flag: '🇸🇦' },
    { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' }
  ])
  
  const isLoading = ref(false)
  const translations = ref<Record<string, any>>({})

  // Getters
  const currentLanguageInfo = computed(() => 
    supportedLanguages.value.find(lang => lang.code === currentLanguage.value)
  )
  
  const isRTL = computed(() => 
    ['ar', 'he', 'fa', 'ur'].includes(currentLanguage.value)
  )

  // Actions
  const setLanguage = async (languageCode: string) => {
    try {
      isLoading.value = true
      
      // Check if language is supported
      const language = supportedLanguages.value.find(lang => lang.code === languageCode)
      if (!language) {
        throw new Error(`Language ${languageCode} is not supported`)
      }
      
      // Update local state
      currentLanguage.value = languageCode
      
      // Save to localStorage
      localStorage.setItem('preferred_language', languageCode)
      
      // Update user preference on backend
      const userStore = useUserStore()
      if (userStore.isAuthenticated) {
        const { $api } = useNuxtApp()
        await $api.put('/languages/set', { language: languageCode })
      }
      
      // Load translations
      await loadTranslations(languageCode)
      
      // Update document attributes
      document.documentElement.lang = languageCode
      document.documentElement.dir = isRTL.value ? 'rtl' : 'ltr'
      
      // Emit language change event
      window.dispatchEvent(new CustomEvent('languageChanged', { 
        detail: { language: languageCode } 
      }))
      
    } catch (error) {
      console.error('Error setting language:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const detectLanguage = async () => {
    try {
      const { $api } = useNuxtApp()
      
      const response = await $api.get('/languages/detect')
      
      if (response.detected_language && response.supported) {
        await setLanguage(response.detected_language)
        return response.detected_language
      }
      
      return null
      
    } catch (error) {
      console.error('Error detecting language:', error)
      return null
    }
  }

  const loadTranslations = async (languageCode: string) => {
    try {
      const { $api } = useNuxtApp()
      
      const response = await $api.get(`/languages/translations/${languageCode}`)
      translations.value = response.translations
      
    } catch (error) {
      console.error('Error loading translations:', error)
      // Load fallback translations
      translations.value = getFallbackTranslations()
    }
  }

  const getFallbackTranslations = () => {
    return {
      dashboard: 'Dashboard',
      invoices: 'Invoices',
      clients: 'Clients',
      payments: 'Payments',
      reports: 'Reports',
      settings: 'Settings',
      profile: 'Profile',
      logout: 'Logout',
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      create: 'Create',
      search: 'Search',
      filter: 'Filter',
      export: 'Export',
      import: 'Import'
    }
  }

  const getText = (key: string, fallback?: string) => {
    return translations.value[key] || fallback || key
  }

  const formatCurrency = async (amount: number, currency: string = 'USD') => {
    try {
      const { $api } = useNuxtApp()
      
      const response = await $api.post('/languages/format/currency', {
        amount,
        currency,
        locale: currentLanguage.value
      })
      
      return response.formatted
      
    } catch (error) {
      console.error('Error formatting currency:', error)
      // Fallback formatting
      return new Intl.NumberFormat(currentLanguage.value, {
        style: 'currency',
        currency: currency
      }).format(amount)
    }
  }

  const formatDate = async (date: string | Date, formatType: string = 'long') => {
    try {
      const { $api } = useNuxtApp()
      
      const dateStr = typeof date === 'string' ? date : date.toISOString()
      
      const response = await $api.post('/languages/format/date', {
        date: dateStr,
        format_type: formatType,
        locale: currentLanguage.value
      })
      
      return response.formatted
      
    } catch (error) {
      console.error('Error formatting date:', error)
      // Fallback formatting
      const dateObj = typeof date === 'string' ? new Date(date) : date
      return dateObj.toLocaleDateString(currentLanguage.value, {
        year: 'numeric',
        month: formatType === 'long' ? 'long' : 'numeric',
        day: 'numeric'
      })
    }
  }

  const getTaxRules = async (countryCode: string) => {
    try {
      const { $api } = useNuxtApp()
      
      const response = await $api.get(`/languages/tax-rules/${countryCode}`)
      return response.tax_rules
      
    } catch (error) {
      console.error('Error getting tax rules:', error)
      return null
    }
  }

  const initializeLanguage = async () => {
    try {
      // Try to get from localStorage first
      const savedLanguage = localStorage.getItem('preferred_language')
      if (savedLanguage && supportedLanguages.value.find(lang => lang.code === savedLanguage)) {
        await setLanguage(savedLanguage)
        return
      }
      
      // Try to detect from browser
      const detectedLanguage = await detectLanguage()
      if (detectedLanguage) {
        return
      }
      
      // Fallback to default
      await setLanguage('en')
      
    } catch (error) {
      console.error('Error initializing language:', error)
      // Fallback to default
      await setLanguage('en')
    }
  }

  const getSupportedLanguages = async () => {
    try {
      const { $api } = useNuxtApp()
      
      const response = await $api.get('/languages/supported')
      supportedLanguages.value = Object.entries(response.languages).map(([code, name]) => ({
        code,
        name: name as string,
        flag: getFlagForLanguage(code)
      }))
      
    } catch (error) {
      console.error('Error fetching supported languages:', error)
    }
  }

  const getFlagForLanguage = (languageCode: string): string => {
    const flagMap: Record<string, string> = {
      'en': '🇺🇸', 'es': '🇪🇸', 'fr': '🇫🇷', 'de': '🇩🇪',
      'it': '🇮🇹', 'pt': '🇵🇹', 'nl': '🇳🇱', 'pl': '🇵🇱',
      'ru': '🇷🇺', 'ja': '🇯🇵', 'ko': '🇰🇷', 'zh': '🇨🇳',
      'ar': '🇸🇦', 'hi': '🇮🇳'
    }
    return flagMap[languageCode] || '🌐'
  }

  return {
    // State
    currentLanguage,
    supportedLanguages,
    isLoading,
    translations,
    
    // Getters
    currentLanguageInfo,
    isRTL,
    
    // Actions
    setLanguage,
    detectLanguage,
    loadTranslations,
    getText,
    formatCurrency,
    formatDate,
    getTaxRules,
    initializeLanguage,
    getSupportedLanguages
  }
})
