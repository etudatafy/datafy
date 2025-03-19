<template>
  <div class="app-layout bg-light">
    <header class="chat-header bg-success text-white py-3 text-center shadow">
      <h2 class="fw-bold">Yapay Zeka Yardım</h2>
    </header>
    
    <main class="container d-flex flex-column align-items-center justify-content-start pt-3">
      <slot></slot>
    </main>
  </div>
</template>

<script>
export default {};
</script>

<style scoped>
.chat-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
}
</style>
