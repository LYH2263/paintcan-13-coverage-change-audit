<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const FIELD_LABELS = { coverage: '默认涂布率 (m²/L)', coats: '默认遍数' }

const settings = ref({ coverage: '', coats: '' })
const history = ref([])
const message = ref('')
const error = ref('')
const saving = ref(false)

async function load() {
  const [s, h] = await Promise.all([getJSON('/api/settings'), getJSON('/api/settings/history')])
  settings.value = { coverage: s.coverage ?? '', coats: s.coats ?? '' }
  history.value = h.items
}

const emit = defineEmits(['saved'])
async function save() {
  message.value = ''; error.value = ''; saving.value = true
  try {
    const body = { coverage: Number(settings.value.coverage), coats: Number(settings.value.coats) }
    const r = await postJSON('/api/settings', body)
    settings.value = { coverage: r.settings.coverage ?? '', coats: r.settings.coats ?? '' }
    message.value = r.changed.length
      ? `已记录 ${r.changed.length} 项变更`
      : '值未变化，未追加履历'
    history.value = (await getJSON('/api/settings/history')).items
    emit('saved', r.settings)
  } catch (e) {
    error.value = String(e.message || e)
  } finally {
    saving.value = false
  }
}

function fmtTime(iso) {
  return iso ? new Date(iso).toLocaleString() : ''
}

onMounted(load)
</script>

<template>
  <section>
    <div class="defaults-form">
      <label v-for="f in ['coverage', 'coats']" :key="f">
        {{ FIELD_LABELS[f] }}
        <input v-model.number="settings[f]" type="number" min="0.1" :step="f === 'coats' ? 1 : 0.1" />
      </label>
      <button :disabled="saving" @click="save">保存默认值</button>
      <span v-if="message" class="ok">{{ message }}</span>
      <span v-if="error" class="err">{{ error }}</span>
    </div>
    <h2>变更履历</h2>
    <p v-if="!history.length" class="muted">暂无变更记录</p>
    <table v-else>
      <thead><tr><th>时间</th><th>字段</th><th>变更前</th><th></th><th>变更后</th></tr></thead>
      <tbody>
        <tr v-for="h in history" :key="h.id">
          <td>{{ fmtTime(h.changed_at) }}</td>
          <td>{{ FIELD_LABELS[h.field] || h.field }}</td>
          <td>{{ h.old_value || '—' }}</td>
          <td>→</td>
          <td>{{ h.new_value }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.defaults-form { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; }
.defaults-form input { width: 6rem; padding: 0.3rem; }
.ok { color: #2a7d4f; }
.err { color: #b03030; }
.muted { color: #5a7a8a; }
h2 { margin-top: 1.25rem; }
</style>
