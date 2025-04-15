<template>
  <PageLayout navbarText="Yapay Zeka Sohbet">
    <div
      class="container-fluid"
      style="height: calc(100vh - 60px);"
    >
      <div class="row h-100 justify-content-center align-items-center">
        <div class="col-12 col-md-10 col-lg-9 d-flex flex-column">
          <ChatPageContent :key="$route.params.chatId"/>
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';
import ChatPageContent from '../page-contents/ChatPageContent.vue';

export default {
  name: 'ChatPage',
  components: { PageLayout, ChatPageContent }
};
</script>
