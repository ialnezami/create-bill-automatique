<template>
  <div class="py-6">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Create New Invoice</h1>
            <p class="mt-2 text-gray-600">Create a professional invoice for your client</p>
          </div>
          <NuxtLink 
            to="/invoices" 
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Invoices
          </NuxtLink>
        </div>
      </div>

      <!-- Invoice Form -->
      <form @submit.prevent="handleSubmit" class="space-y-8">
        <!-- Client Selection -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Client Information</h3>
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="client" class="block text-sm font-medium text-gray-700">Client *</label>
              <select
                id="client"
                v-model="form.client_id"
                required
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                @change="onClientChange"
              >
                <option value="">Select a client</option>
                <option v-for="client in clients" :key="client.id" :value="client.id">
                  {{ client.company_name }}
                </option>
              </select>
            </div>
            
            <div>
              <label for="due_date" class="block text-sm font-medium text-gray-700">Due Date *</label>
              <input
                id="due_date"
                v-model="form.due_date"
                type="date"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
            </div>
          </div>
        </div>

        <!-- Invoice Items -->
        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Invoice Items</h3>
            <button
              type="button"
              @click="addItem"
              class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Item
            </button>
          </div>
          
          <div class="space-y-4">
            <div v-for="(item, index) in form.items" :key="index" class="grid grid-cols-12 gap-4 items-end border-b border-gray-200 pb-4">
              <div class="col-span-5">
                <label :for="`description-${index}`" class="block text-sm font-medium text-gray-700">Description *</label>
                <input
                  :id="`description-${index}`"
                  v-model="item.description"
                  type="text"
                  required
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  placeholder="Item description"
                >
              </div>
              
              <div class="col-span-2">
                <label :for="`quantity-${index}`" class="block text-sm font-medium text-gray-700">Qty *</label>
                <input
                  :id="`quantity-${index}`"
                  v-model.number="item.quantity"
                  type="number"
                  min="0.01"
                  step="0.01"
                  required
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  @input="calculateItemTotal(index)"
                >
              </div>
              
              <div class="col-span-2">
                <label :for="`unit_price-${index}`" class="block text-sm font-medium text-gray-700">Unit Price *</label>
                <input
                  :id="`unit_price-${index}`"
                  v-model.number="item.unit_price"
                  type="number"
                  min="0.01"
                  step="0.01"
                  required
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  @input="calculateItemTotal(index)"
                >
              </div>
              
              <div class="col-span-1">
                <label :for="`tax_rate-${index}`" class="block text-sm font-medium text-gray-700">Tax %</label>
                <input
                  :id="`tax_rate-${index}`"
                  v-model.number="item.tax_rate"
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  @input="calculateItemTotal(index)"
                >
              </div>
              
              <div class="col-span-1">
                <label :for="`discount_rate-${index}`" class="block text-sm font-medium text-gray-700">Discount %</label>
                <input
                  :id="`discount_rate-${index}`"
                  v-model.number="item.discount_rate"
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  @input="calculateItemTotal(index)"
                >
              </div>
              
              <div class="col-span-1">
                <label class="block text-sm font-medium text-gray-700">Total</label>
                <div class="mt-1 text-sm text-gray-900 font-medium">
                  {{ formatCurrency(item.total || 0) }}
                </div>
              </div>
              
              <div class="col-span-1">
                <button
                  type="button"
                  @click="removeItem(index)"
                  class="text-red-600 hover:text-red-800"
                  :disabled="form.items.length === 1"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Charges -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Additional Charges</h3>
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="shipping_fee" class="block text-sm font-medium text-gray-700">Shipping Fee</label>
              <input
                id="shipping_fee"
                v-model.number="form.shipping_fee"
                type="number"
                min="0"
                step="0.01"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                @input="calculateTotals"
              >
            </div>
            
            <div>
              <label for="handling_fee" class="block text-sm font-medium text-gray-700">Handling Fee</label>
              <input
                id="handling_fee"
                v-model.number="form.handling_fee"
                type="number"
                min="0"
                step="0.01"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                @input="calculateTotals"
              >
            </div>
          </div>
        </div>

        <!-- Totals Summary -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Invoice Summary</h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">Subtotal:</span>
              <span class="font-medium">{{ formatCurrency(totals.subtotal) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Tax Total:</span>
              <span class="font-medium">{{ formatCurrency(totals.tax_total) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Discount Total:</span>
              <span class="font-medium">{{ formatCurrency(totals.discount_total) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Shipping Fee:</span>
              <span class="font-medium">{{ formatCurrency(form.shipping_fee || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Handling Fee:</span>
              <span class="font-medium">{{ formatCurrency(form.handling_fee || 0) }}</span>
            </div>
            <div class="border-t pt-3">
              <div class="flex justify-between text-lg font-bold">
                <span>Total Amount:</span>
                <span>{{ formatCurrency(totals.total_amount) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Notes and Terms -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Additional Information</h3>
          <div class="space-y-4">
            <div>
              <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
              <textarea
                id="notes"
                v-model="form.notes"
                rows="3"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                placeholder="Additional notes for the client"
              ></textarea>
            </div>
            
            <div>
              <label for="terms_conditions" class="block text-sm font-medium text-gray-700">Terms & Conditions</label>
              <textarea
                id="terms_conditions"
                v-model="form.terms_conditions"
                rows="3"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                placeholder="Payment terms and conditions"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="flex justify-end space-x-4">
          <button
            type="button"
            @click="saveDraft"
            :disabled="isSubmitting"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Save as Draft
          </button>
          
          <button
            type="submit"
            :disabled="isSubmitting || !isFormValid"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isSubmitting ? 'Creating Invoice...' : 'Create Invoice' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '~/stores/user'

definePageMeta({
  middleware: 'auth'
})

const userStore = useUserStore()
const router = useRouter()

// Form data
const form = reactive({
  client_id: '',
  due_date: '',
  items: [
    {
      description: '',
      quantity: 1,
      unit_price: 0,
      tax_rate: 0,
      discount_rate: 0,
      total: 0
    }
  ],
  shipping_fee: 0,
  handling_fee: 0,
  notes: '',
  terms_conditions: ''
})

// State
const clients = ref([])
const isSubmitting = ref(false)

// Computed properties
const totals = computed(() => {
  let subtotal = 0
  let tax_total = 0
  let discount_total = 0
  
  form.items.forEach(item => {
    const itemSubtotal = (item.quantity || 0) * (item.unit_price || 0)
    const itemDiscount = itemSubtotal * ((item.discount_rate || 0) / 100)
    const itemTax = (itemSubtotal - itemDiscount) * ((item.tax_rate || 0) / 100)
    
    subtotal += itemSubtotal
    discount_total += itemDiscount
    tax_total += itemTax
  })
  
  const total_amount = subtotal - discount_total + tax_total + (form.shipping_fee || 0) + (form.handling_fee || 0)
  
  return {
    subtotal,
    tax_total,
    discount_total,
    total_amount
  }
})

const isFormValid = computed(() => {
  return form.client_id && 
         form.due_date && 
         form.items.length > 0 &&
         form.items.every(item => 
           item.description && 
           item.quantity > 0 && 
           item.unit_price > 0
         )
})

// Methods
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount || 0)
}

const addItem = () => {
  form.items.push({
    description: '',
    quantity: 1,
    unit_price: 0,
    tax_rate: 0,
    discount_rate: 0,
    total: 0
  })
}

const removeItem = (index) => {
  if (form.items.length > 1) {
    form.items.splice(index, 1)
    calculateTotals()
  }
}

const calculateItemTotal = (index) => {
  const item = form.items[index]
  const subtotal = (item.quantity || 0) * (item.unit_price || 0)
  const discount = subtotal * ((item.discount_rate || 0) / 100)
  const tax = (subtotal - discount) * ((item.tax_rate || 0) / 100)
  
  item.total = subtotal - discount + tax
}

const calculateTotals = () => {
  form.items.forEach((_, index) => {
    calculateItemTotal(index)
  })
}

const onClientChange = () => {
  // You could load client-specific settings here
  console.log('Client changed:', form.client_id)
}

const loadClients = async () => {
  try {
    const response = await $fetch('/api/clients', {
      headers: {
        'Authorization': `Bearer ${userStore.accessToken}`
      }
    })
    
    if (response.clients) {
      clients.value = response.clients
    }
  } catch (error) {
    console.error('Error loading clients:', error)
  }
}

const saveDraft = async () => {
  // Implementation for saving as draft
  console.log('Saving as draft...')
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    const response = await $fetch('/api/invoices', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: {
        client_id: form.client_id,
        due_date: form.due_date,
        items: form.items.map(item => ({
          description: item.description,
          quantity: item.quantity,
          unit_price: item.unit_price,
          tax_rate: item.tax_rate,
          discount_rate: item.discount_rate
        })),
        shipping_fee: form.shipping_fee,
        handling_fee: form.handling_fee,
        notes: form.notes,
        terms_conditions: form.terms_conditions
      }
    })
    
    if (response.invoice) {
      // Redirect to the new invoice
      await router.push(`/invoices/${response.invoice.id}`)
    }
    
  } catch (error) {
    console.error('Error creating invoice:', error)
    // Handle error (show notification, etc.)
  } finally {
    isSubmitting.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadClients()
  
  // Set default due date to 30 days from now
  const defaultDate = new Date()
  defaultDate.setDate(defaultDate.getDate() + 30)
  form.due_date = defaultDate.toISOString().split('T')[0]
})
</script>
