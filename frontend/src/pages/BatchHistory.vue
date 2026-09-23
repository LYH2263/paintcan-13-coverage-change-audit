<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const expandedId = ref(null)

function pinned(h) {
  // 钉选的涂布率/遍数/升数以 result_json 为准（种子记录的 input_json 仅含 room_id）
  try {
    return JSON.parse(h.result_json)
  } catch {
    return {}
  }
}
function toggle(id) { expandedId.value = expandedId.value === id ? null : id }

onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template>
  <div class="page">
    <h1>估算记录</h1>
    <table>
      <thead>
        <tr><th>ID</th><th>时间</th><th>升数</th><th>涂布率(m²/L)</th><th>遍数</th><th></th></tr>
      </thead>
      <tbody>
        <template v-for="h in items" :key="h.id">
          <tr style="cursor:pointer" @click="toggle(h.id)">
            <td>#{{ h.id }}</td>
            <td>{{ h.created_at }}</td>
            <td>{{ pinned(h).liters }}</td>
            <td>{{ pinned(h).coverage }}</td>
            <td>{{ pinned(h).coats }}</td>
            <td>{{ expandedId === h.id ? '收起' : '展开' }}</td>
          </tr>
          <tr v-if="expandedId === h.id">
            <td colspan="6">
              <ul>
                <li>写入时升数：<strong>{{ pinned(h).liters }} 升</strong></li>
                <li>钉选涂布率：<strong>{{ pinned(h).coverage }} m²/L</strong></li>
                <li>钉选遍数：<strong>{{ pinned(h).coats }}</strong></li>
                <li v-if="pinned(h).net_m2 !== undefined">净面积：{{ pinned(h).net_m2 }} m²</li>
                <li>房间ID：{{ h.room_id }}</li>
              </ul>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
