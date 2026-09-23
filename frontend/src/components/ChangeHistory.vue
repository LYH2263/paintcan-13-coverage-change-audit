<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const FIELD_LABELS = { coverage: '默认涂布率(m²/L)', coats: '默认遍数' }

async function load() {
  items.value = (await getJSON('/api/settings/history')).items
}

onMounted(load)
defineExpose({ load })
</script>

<template>
  <section>
    <h2>变更履历</h2>
    <p v-if="items.length === 0">暂无变更记录</p>
    <table v-else>
      <thead>
        <tr><th>时间</th><th>项目</th><th>原值</th><th>新值</th></tr>
      </thead>
      <tbody>
        <tr v-for="h in items" :key="h.id">
          <td>{{ h.changed_at }}</td>
          <td>{{ FIELD_LABELS[h.field] || h.field }}</td>
          <td>{{ h.old_value === null ? '(无)' : h.old_value }}</td>
          <td>{{ h.new_value }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
