<template>
  <PageLayout navbarText="Sayfa Bulunamadı">
    <div
      class="container-fluid bg-success-subtle"
      style="min-height: calc(100vh - 60px);"
    >
      <div class="row h-100 justify-content-center align-items-center pt-3">
        <div class="col-12 col-md-8 col-lg-6">
          <NotFoundPageContent />
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue'
import NotFoundPageContent from '../page-contents/NotFoundPageContent.vue'

export default {
  name: 'NotFoundPage',
  components: {
    PageLayout,
    NotFoundPageContent
  }
}
</script>
