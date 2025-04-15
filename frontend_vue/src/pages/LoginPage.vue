<template>
  <PageLayout navbarText="Giriş Yap">
    <div class="container-fluid d-flex flex-column align-items-center justify-content-center">
      <LoginPageContent/>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';
import LoginPageContent from '../page-contents/LoginPageContent.vue';
export default {
  components: { PageLayout,
    LoginPageContent
   },
  // ...
}
</script>
