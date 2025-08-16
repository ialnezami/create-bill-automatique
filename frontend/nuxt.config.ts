// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxt/ui'
  ],
  
  css: [
    '~/assets/css/main.css',
    'vue-toastification/dist/index.css'
  ],
  
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api',
      stripePublicKey: process.env.NUXT_PUBLIC_STRIPE_PUBLIC_KEY || '',
      paypalClientId: process.env.NUXT_PUBLIC_PAYPAL_CLIENT_ID || ''
    }
  },
  
  app: {
    head: {
      title: 'Invoice Automation',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Professional invoice automation and management system' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },
  
  build: {
    transpile: ['vue-toastification']
  },
  
  vite: {
    optimizeDeps: {
      include: ['vue-toastification']
    }
  }
})
