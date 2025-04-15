<template>
  <PageLayout navbarText="Takvim">
    <div class="py-4">
      <CalenderPageContent />
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';
import CalenderPageContent from '../page-contents/CalenderPageContent.vue';

export default {
  name: 'CalenderPage',
  components: {
    PageLayout,
    CalenderPageContent
  }
};
</script>
