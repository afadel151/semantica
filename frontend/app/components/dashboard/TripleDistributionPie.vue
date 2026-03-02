<script setup lang="ts">

import { PolarArea } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, RadialLinearScale, ArcElement } from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale,RadialLinearScale,ArcElement, LinearScale)

import { TrendingUp } from "lucide-vue-next"


const chartData = {
  labels: ['Subjects', 'Predicates', 'Objects'],
  datasets: [
    {
      label: 'Visitors',
      data: [4300, 3800, 2400],
      borderColor: '#fff',
      borderWidth:0,
      backgroundColor: [
        '#ff2159',
        '#1549e6',
        '#ff9900',
      ],
    },
  ],
}
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false, // 🔥 allows full height usage
  
  plugins: {
    legend: {
      display: false, // ❌ remove legend
    },
    tooltip: {
      enabled: true, // keep tooltips if you want
    },
  },
  scales: {
    r: {
      pointLabels: {
        display: false, // ❌ remove Chrome/Safari/etc labels
      },
      ticks: {
        display: false, // ❌ remove radial numbers
      },
      grid: {
        display: false, // optional: remove circular grid
      },
    },
  },
}


</script>

<template>
  <Card class="flex flex-col">
    <CardHeader class="items-center pb-0">
      <CardTitle>Triples Distribution</CardTitle>
    </CardHeader>
    <CardContent class="flex-1 pb-0">
      <PolarArea :options="chartOptions" :data="chartData" />
    </CardContent>
    <CardFooter class="flex-col gap-2 text-sm">
      <div class="flex items-center gap-2 font-medium leading-none">
        Trending up by 5.2% this month
        <TrendingUp class="h-4 w-4" />
      </div>
      <div class="leading-none text-muted-foreground">
        Showing total visitors for the last 6 months
      </div>
    </CardFooter>
  </Card>
</template>
