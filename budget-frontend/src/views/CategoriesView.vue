<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Manage Categories</h1>
      <router-link to="/" class="btn btn-outline">
        Back to Dashboard
      </router-link>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading categories...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">
            {{ error }}
          </p>
        </div>
      </div>
    </div>

    <!-- Categories content -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Add new category card -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Add New Category</h2>
        <form @submit.prevent="addCategory">
          <div class="mb-4">
            <label for="categoryName" class="form-label">Category Name</label>
            <input type="text" id="categoryName" v-model="newCategory.name" required class="input" placeholder="e.g. Groceries">
          </div>
          
          <div class="mb-6">
            <label for="categoryColor" class="form-label">Color</label>
            <input type="color" id="categoryColor" v-model="newCategory.color" class="w-full h-10 p-1 rounded border border-gray-300">
          </div>
          
          <button type="submit" class="btn btn-primary w-full">
            Add Category
          </button>
        </form>
      </div>
      
      <!-- Category list -->
      <div class="bg-white shadow rounded-lg p-6 md:col-span-2">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Your Categories</h2>
        
        <div v-if="categories.length === 0" class="text-center py-8 text-gray-500">
          No categories defined yet
        </div>
        
        <div v-else class="space-y-4">
          <div v-for="category in categories" :key="category.id" 
               class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div class="flex items-center">
              <div class="w-4 h-4 rounded-full mr-3" :style="{ backgroundColor: category.color }"></div>
              <span>{{ category.name }}</span>
            </div>
            
            <div class="flex space-x-2">
              <button @click="openEditModal(category)" class="text-primary-600 hover:text-primary-800">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
              </button>
              <button @click="deleteCategory(category.id)" class="text-red-600 hover:text-red-800">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Category mappings card -->
      <div class="bg-white shadow rounded-lg p-6 md:col-span-3">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Auto-Categorization Rules</h2>
        <p class="text-gray-500 mb-4">
          Create rules to automatically categorize transactions based on their description.
        </p>
        
        <form @submit.prevent="addMapping" class="mb-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="md:col-span-2">
              <label for="mappingPattern" class="form-label">Description Contains</label>
              <input type="text" id="mappingPattern" v-model="newMapping.pattern" required class="input" 
                     placeholder="e.g. walmart, kroger, uber">
            </div>
            
            <div>
              <label for="mappingCategory" class="form-label">Assign to Category</label>
              <select id="mappingCategory" v-model="newMapping.category_id" required class="input">
                <option value="" disabled>Select category</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="mt-4">
            <button type="submit" class="btn btn-primary">
              Add Rule
            </button>
          </div>
        </form>
        
        <div v-if="Object.keys(mappings).length === 0" class="text-center py-8 text-gray-500">
          No auto-categorization rules defined yet
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description Contains
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assigned Category
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(categoryId, pattern) in mappings" :key="pattern">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ pattern }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ getCategoryNameById(categoryId) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="deleteMapping(pattern)" class="text-red-600 hover:text-red-800">
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Edit category modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-10 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="showEditModal = false"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
              Edit Category
            </h3>
            
            <div class="mt-4">
              <div class="mb-4">
                <label for="editCategoryName" class="form-label">Category Name</label>
                <input type="text" id="editCategoryName" v-model="editCategory.name" required class="input">
              </div>
              
              <div class="mb-4">
                <label for="editCategoryColor" class="form-label">Color</label>
                <input type="color" id="editCategoryColor" v-model="editCategory.color" class="w-full h-10 p-1 rounded border border-gray-300">
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button type="button" @click="updateCategory" class="btn btn-primary sm:ml-3">
              Save Changes
            </button>
            <button type="button" @click="showEditModal = false" class="btn btn-outline mt-3 sm:mt-0">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { apiService } from '../services/api';

// State
const categories = ref([]);
const mappings = ref({});
const loading = ref(false);
const error = ref(null);

// Form state
const newCategory = ref({
  name: '',
  color: '#4CAF50'
});

const newMapping = ref({
  pattern: '',
  category_id: ''
});

// Edit modal state
const showEditModal = ref(false);
const editCategory = ref({});

// Load data
async function loadCategories() {
  loading.value = true;
  error.value = null;
  
  try {
    categories.value = await apiService.getCategories();
  } catch (err) {
    error.value = err.message || 'Failed to load categories';
    console.error(error.value);
  } finally {
    loading.value = false;
  }
}

async function loadMappings() {
  loading.value = true;
  error.value = null;
  
  try {
    mappings.value = await apiService.getMappings();
  } catch (err) {
    error.value = err.message || 'Failed to load category mappings';
    console.error(error.value);
  } finally {
    loading.value = false;
  }
}

// CRUD operations
async function addCategory() {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await apiService.addCategory(newCategory.value);
    categories.value = result.categories;
    newCategory.value = { name: '', color: '#4CAF50' };
  } catch (err) {
    error.value = err.message || 'Failed to add category';
    console.error(error.value);
  } finally {
    loading.value = false;
  }
}

async function updateCategory() {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await apiService.updateCategory(editCategory.value.id, {
      name: editCategory.value.name,
      color: editCategory.value.color
    });
    
    categories.value = result.categories;
    showEditModal.value = false;
  } catch (err) {
    error.value = err.message || 'Failed to update category';
    console.error(error.value);
  } finally {
    loading.value = false;
  }
}

async function deleteCategory(categoryId) {
  if (!confirm('Are you sure you want to delete this category? This will affect all transactions using this category.')) {
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    const result = await apiService.deleteCategory(categoryId);
    categories.value = result.categories;
  } catch (err) {
    error.value = err.message || 'Failed to delete category';
    console.error(error.value);
  } finally {
    loading.value = false;
  }
}

async function addMapping() {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await apiService.addMapping(newMapping.value.pattern, newMapping.value.category_id);
    mappings.value = result.mappings;
    newMapping.value = { pattern: '', category_id: '' };
  } catch (err) {
    error.value = err.message || 'Failed to add mapping';
    console.error(error.value);
  } finally {
    loading.value = false;
  }
}

async function deleteMapping(pattern) {
  if (!confirm('Are you sure you want to delete this auto-categorization rule?')) {
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    const result = await apiService.deleteMapping(pattern);
    mappings.value = result.mappings;
  } catch (err) {
    error.value = err.message || 'Failed to delete mapping';
    console.error(error.value);
  } finally {
    loading.value = false;
  }
}

// Helper functions
function getCategoryNameById(categoryId) {
  const category = categories.value.find(c => c.id === categoryId);
  return category ? category.name : 'Unknown';
}

function openEditModal(category) {
  editCategory.value = { ...category };
  showEditModal.value = true;
}

// Initial data load
onMounted(async () => {
  await loadCategories();
  await loadMappings();
});
</script>