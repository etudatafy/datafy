<template>
  <PageLayout navbarText="SSS">
    <div class="container-fluid d-flex flex-column align-items-center justify-content-center">
      <div class="row w-100">
        <div class="col-12 col-md-10 col-lg-8 mx-auto bg-white">
          <FaqPageContent />
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue'
import FaqPageContent from '../page-contents/FaqPageContent.vue'

export default {
  name: 'FaqPage',
  components: {
    PageLayout,
    FaqPageContent
  }
}
</script>
