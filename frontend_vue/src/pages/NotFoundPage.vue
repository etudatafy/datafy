<template>
  <PageLayout navbarText="Sayfa Bulunamadı">
    <div class="container-fluid vh-100 d-flex flex-column align-items-center justify-content-center">
      <NotFoundPageContent/>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';
import NotFoundPageContent from '../page-contents/NotFoundPageContent.vue';
export default {
  components: { PageLayout,
    NotFoundPageContent
   },
  // ...
}
</script>
