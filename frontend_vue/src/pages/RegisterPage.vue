<template>
  <PageLayout navbarText="Kayıt Ol">
    <div class="container-fluid d-flex flex-column align-items-center justify-content-center">
      <RegisterPageContent/>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';
import RegisterPageContent from '../page-contents/RegisterPageContent.vue';
export default {
  components: { PageLayout,
    RegisterPageContent
   },
  // ...
}
</script>
