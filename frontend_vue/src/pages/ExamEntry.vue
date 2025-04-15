<template>
  <PageLayout navbarText="Sınav Sonucu Ekleme">
    <div class="container-fluid d-flex flex-column align-items-center justify-content-center">
      <ExamEntryContent/>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';
import ExamEntryContent from '../page-contents/ExamEntryContent.vue';
export default {
  components: { PageLayout,
    ExamEntryContent
   },
  // ...
}
</script>
