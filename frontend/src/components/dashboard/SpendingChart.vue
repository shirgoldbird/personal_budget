<template>
  <div>
    <div class="flex flex-col md:flex-row">
      <div class="w-full md:w-1/2">
        <div class="chart-container">
          <Doughnut 
            :data="chartData" 
            :options="chartOptions" 
            :height="200" 
          />
        </div>
      </div>
      <div class="w-full md:w-1/2 mt-4 md:mt-0">
        <h4 class="font-medium text-gray-900 mb-2">Spending Breakdown</h4>
        <div class="space-y-2">
          <div v-for="(item, index) in spendingData" :key="index" class="flex justify-between">
            <div class="flex items-center">
              <span class="w-3 h-3 rounded-full mr-2" :style="{ backgroundColor: item.color || getRandomColor(index) }"></span>
              <span class="text-sm text-gray-800">{{ item.category }}</span>
            </div>
            <div class="text-sm font-medium">
              ${{ item.amount.toFixed(2) }}
              <span class="text-xs text-gray-500 ml-1">
                ({{ getPercentage(item.amount) }}%)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  spendingData: {
    type: Array,
    required: true
  }
});

// Calculate the total spending
const totalSpending = computed(() => {
  return props.spendingData.reduce((total, item) => total + item.amount, 0);
});

// Format data for Chart.js
const chartData = computed(() => {
  return {
    labels: props.spendingData.map(item => item.category),
    datasets: [
      {
        data: props.spendingData.map(item => item.amount),
        backgroundColor: props.spendingData.map((item, index) => item.color || getRandomColor(index)),
        borderWidth: 1
      }
    ]
  };
});

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.label || '';
          const value = context.raw || 0;
          const percentage = (value / totalSpending.value * 100).toFixed(1);
          return `${label}: $${value.toFixed(2)} (${percentage}%)`;
        }
      }
    }
  }
};

// Get the percentage of total spending
function getPercentage(amount) {
  return (amount / totalSpending.value * 100).toFixed(1);
}

// Generate a random color for categories without assigned colors
function getRandomColor(index) {
  const colors = [
    '#4CAF50', '#2196F3', '#9C27B0', '#E91E63',
    '#FF5722', '#607D8B', '#00BCD4', '#8BC34A',
    '#FFC107', '#3F51B5', '#CDDC39', '#795548'
  ];
  
  return colors[index % colors.length];
}
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 200px;
}
</style>