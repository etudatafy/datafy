<template>
  <div class="card shadow flex-fill d-flex flex-column">
    <!-- Başlık -->
    <div class="card-header bg-white text-center">
      <h5 class="mb-0">Sohbet</h5>
    </div>

    <!-- Mesajlar -->
    <div
      ref="messagesContainer"
      class="card-body overflow-auto flex-fill p-3"
    >
      <ChatMessages :messages="messages" :loading="loading" />
    </div>

    <!-- Girdi -->
    <div class="card-footer bg-white border-0 p-3">
      <ChatInput
        v-model="userMessage"
        @send="sendMessage"
        :loading="loading"
      />
    </div>
    <SessionExpiredWarning
      :show="showSessionExpired"
      @confirm="handleSessionExpiredConfirm"
    />
  </div>
</template>

<script>
import ChatMessages from "../components/ChatMessages.vue";
import ChatInput from "../components/ChatInput.vue";
import SessionExpiredWarning from "../warnings/SessionExpiredWarning.vue";

export default {
  components: { ChatMessages, ChatInput, SessionExpiredWarning },
  data() {
    return {
      userMessage: "",
      messages: [{ text: "Lütfen bana istediğinizi sorun", sender: "receiver" }],
      loading: false,
      chatId: this.$route.params.chatId || null,
      token: localStorage.getItem("jwt_token") || "",
      showSessionExpired: false
    };
  },
  created() {
    if (this.chatId) {
      this.loadChatHistory();
    }
  },
  methods: {
    handleSessionExpiredConfirm() {
      this.showSessionExpired = false;
      localStorage.removeItem("jwt_token");
      this.$router.push("/giris-yap");
    },
    async loadChatHistory() {
      if (!this.token) return;

      try {
        const response = await fetch("http://localhost:3000/api/chat/chat-history", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Authorization": `Bearer ${this.token}` },
          body: JSON.stringify({ chatId: this.chatId }),
        });

        const result = await response.json();

        if (response.status === 401 && result.msg === "Token has expired") {
          this.showSessionExpired = true;
          return;
        }

        if (response.ok && result.messages) {
          this.messages = result.messages;
          this.scrollToBottom();
        }
      } catch (error) {
        console.error("Sohbet geçmişi alınırken hata oluştu:", error);
      }
    },
    async sendMessage() {
      if (!this.userMessage.trim()) return;

      this.messages.push({ text: this.userMessage, sender: "sender" });
      this.$nextTick(() => this.scrollToBottom()); // Mesaj eklendiğinde en alta kaydır

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
        if (response.status === 401 && result.msg === "Token has expired") {
          this.showSessionExpired = true;
          return;
        }

        if (response.ok) {
          if (!this.chatId && result.chatId) {
            this.chatId = result.chatId;
            this.$router.push(`/yapay-zeka-yardim/${this.chatId}`);
          }
          if (result.messages) {
            this.messages = result.messages;
          }
          this.$nextTick(() => this.scrollToBottom()); // Yapay zekadan gelen mesajda da kaydır
        } else {
          console.error("Hata:", result.error || "Bilinmeyen hata");
        }
      } catch (error) {
        console.error("Bağlantı hatası:", error);
      } finally {
        this.loading = false;
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
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
/* tamamen flex ve overflow-auto ile halledildi */
</style>
