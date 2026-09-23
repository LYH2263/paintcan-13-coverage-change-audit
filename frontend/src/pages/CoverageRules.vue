<script setup>
import { ref } from 'vue'
import DefaultsEditor from '../components/DefaultsEditor.vue'
import ChangeHistory from '../components/ChangeHistory.vue'
const history = ref(null)
</script>
<template>
  <div class="page">
    <h1>遮盖力参数</h1>
    <DefaultsEditor @saved="history.load()" />
    <ChangeHistory ref="history" />
  </div>
</template>
