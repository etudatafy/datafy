<template>
  <PageLayout navbarText="Gelişim Analizi">
    <div class="py-4">
      <ProgressPageContent />
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';
import ProgressPageContent from '../page-contents/ProgressPageContent.vue';

export default {
  name: 'ProgressPage',
  components: {
    PageLayout,
    ProgressPageContent
  }
};
</script>
