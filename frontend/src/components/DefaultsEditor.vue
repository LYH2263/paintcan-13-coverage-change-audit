<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const emit = defineEmits(['saved'])
const coverage = ref(null)
const coats = ref(null)
const status = ref('')
const saving = ref(false)

async function load() {
  const s = await getJSON('/api/settings')
  coverage.value = s.coverage === undefined ? null : Number(s.coverage)
  coats.value = s.coats === undefined ? null : Number(s.coats)
}

async function save() {
  saving.value = true
  status.value = ''
  try {
    const body = {}
    if (coverage.value !== null) body.coverage = coverage.value
    if (coats.value !== null) body.coats = coats.value
    const r = await postJSON('/api/settings', body)
    await load()
    if (r.changed.length === 0) {
      status.value = '数值未变化，未追加变更记录'
    } else {
      status.value = `已保存 ${r.changed.length} 项变更`
      emit('saved')
    }
  } catch (e) {
    status.value = `保存失败：${e.message}`
  } finally {
    saving.value = false
  }
}

onMounted(load)
defineExpose({ load })
</script>

<template>
  <section>
    <h2>默认值</h2>
    <p>
      <label>默认涂布率 (m²/L) <input v-model.number="coverage" type="number" min="0" step="0.1" /></label>
    </p>
    <p>
      <label>默认遍数 <input v-model.number="coats" type="number" min="1" step="1" /></label>
    </p>
    <button :disabled="saving" @click="save">保存</button>
    <span v-if="status" style="margin-left:0.75rem">{{ status }}</span>
  </section>
</template>
