<template>
  <NavigationBar :title="navbarText" />
  <div class="page-content">
    <slot />
  </div>
</template>

<script>
import NavigationBar from './NavigationBar.vue';

export default {
  name: 'PageLayout',
  components: { NavigationBar },
  props: {
    navbarText: { type: String, default: '' }
  }
}
</script>

<style scoped>
.page-content {
  padding-top: 60px;
}
</style>
