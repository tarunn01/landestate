import axios from 'axios'

const API_BASE_URL = '/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getItems = () => apiClient.get('/items')
export const createItem = (item) => apiClient.post('/items', item)
