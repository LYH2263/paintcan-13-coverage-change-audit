<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import DefaultsPanel from '../components/DefaultsPanel.vue'
const s = ref({})
async function load() { s.value = await getJSON('/api/settings') }
onMounted(load)
</script>
<template>
  <div class="page">
    <h1>遮盖力参数</h1>
    <p>当前：每升可刷 {{ s.coverage }} m² · 默认 {{ s.coats }} 遍</p>
    <DefaultsPanel @saved="v => s = v" />
  </div>
</template>
