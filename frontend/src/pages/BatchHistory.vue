<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
function parse(j) { try { return JSON.parse(j) } catch { return {} } }
onMounted(async () => {
  const r = await getJSON('/api/history')
  items.value = r.items.map(x => ({ ...x, input: parse(x.input_json), result: parse(x.result_json) }))
})
function fmtTime(iso) { return iso ? new Date(iso).toLocaleString() : '' }
</script>
<template>
  <div class="page">
    <h1>估算记录</h1>
    <p class="muted">升数与涂布率/遍数均为写入时的钉选值，不随后来默认值变化。</p>
    <table>
      <thead>
        <tr><th>#</th><th>时间</th><th>房间</th><th>升数</th><th>涂布率 (m²/L)</th><th>遍数</th></tr>
      </thead>
      <tbody>
        <tr v-for="h in items" :key="h.id">
          <td>#{{ h.id }}</td>
          <td>{{ fmtTime(h.created_at) }}</td>
          <td>{{ h.room_id ?? '—' }}</td>
          <td>{{ h.result.liters ?? '—' }}</td>
          <td>{{ h.input.coverage ?? '—' }}</td>
          <td>{{ h.input.coats ?? '—' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<style scoped>
.muted { color: #5a7a8a; }
</style>
