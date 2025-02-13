<template>
  <AppLayout>
    <div class="chat-container d-flex flex-column w-100 h-100 mt-5 pt-4">
      <div class="chat-messages flex-grow-1 overflow-auto p-3 d-flex flex-column align-items-center">
        <ChatMessages :messages="messages" :loading="loading" />
      </div>

      <ChatInput v-model="userMessage" @send="sendMessage" :loading="loading" />
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from "../components/AppLayout.vue";
import ChatMessages from "../components/ChatMessages.vue";
import ChatInput from "../components/ChatInput.vue";

export default {
  components: { AppLayout, ChatMessages, ChatInput },
  data() {
    return {
      userMessage: "",
      messages: [{ text: "Lütfen bana istediğinizi sorun", sender: "receiver" }],
      loading: false,
      chatId: this.$route.params.chatId || null,
      token: localStorage.getItem("jwt_token") || "",
    };
  },
  created() {
    if (this.chatId) {
      this.loadChatHistory();
    }
  },
  methods: {
    async loadChatHistory() {
      if (!this.token) return;

      try {
        const response = await fetch("http://localhost:3000/api/chat/chat-history", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Authorization": `Bearer ${this.token}` },
          body: JSON.stringify({ chatId: this.chatId }),
        });

        const result = await response.json();
        if (response.ok && result.messages) {
          this.messages = result.messages;
        }
      } catch (error) {
        console.error("Sohbet geçmişi alınırken hata oluştu:", error);
      }
    },
    async sendMessage() {
      if (!this.userMessage.trim()) return;

      this.messages.push({ text: this.userMessage, sender: "sender" });
      const sentMessage = this.userMessage;
      this.userMessage = "";
      this.loading = true;

      if (!this.token) {
        console.error("JWT Token bulunamadı!");
        this.loading = false;
        return;
      }

      const payload = { type: this.chatId ? 2 : 1, message: sentMessage };
      if (this.chatId) payload.chatId = this.chatId;

      try {
        const response = await fetch("http://localhost:3000/api/chat/update-chat", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Authorization": `Bearer ${this.token}` },
          body: JSON.stringify(payload),
        });

        const result = await response.json();
        if (response.ok) {
          if (!this.chatId && result.chatId) {
            this.chatId = result.chatId;
            this.$router.push(`/yapay-zeka-yardim/${this.chatId}`);
          }
          if (result.messages) {
            this.messages = result.messages;
          }
        } else {
          console.error("Hata:", result.error || "Bilinmeyen hata");
        }
      } catch (error) {
        console.error("Bağlantı hatası:", error);
      } finally {
        this.loading = false;
      }
    },
  },
  beforeRouteUpdate(to, from, next) {
    if (to.params.chatId !== from.params.chatId) {
      this.chatId = to.params.chatId;
      this.messages = [{ text: "Lütfen bana istediğinizi sorun", sender: "receiver" }];
      this.loadChatHistory();
    }
    next();
  },
};
</script>

<style scoped>
.chat-container {
  margin-top: 60px; /* Header kadar boşluk bırak */
  padding-top: 20px; /* İçerik header'a yapışmasın */
  height: calc(100vh - 100px); /* Header ve input alanı için alan bırak */
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  width: 100%;
  max-height: calc(100vh - 160px); /* Header ve chat input hesaba katıldı */
}
</style>
