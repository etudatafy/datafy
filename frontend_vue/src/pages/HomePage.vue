<template>
  <PageLayout navbarText="Ana Sayfa">
    <div class="container-fluid vh-100 d-flex flex-column align-items-center justify-content-center">
      <HomePageContent/>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';
import HomePageContent from '../page-contents/HomePageContent.vue';
export default {
  components: { PageLayout,
    HomePageContent
   },
  // ...
}
</script>
