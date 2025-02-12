<template>
  <div :key="$route.params.chatId">
    <div>
      <div v-for="(msg, index) in messages" :key="index" :class="msg.sender">
        {{ msg.text }}
      </div>
    </div>
    <input v-model="userMessage" @keyup.enter="sendMessage" placeholder="Mesajınızı yazın..." />
    <button @click="sendMessage">Gönder</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userMessage: "",
      messages: [{ text: "Lütfen bana istediğini sor", sender: "receiver" }],
      chatId: this.$route.params.chatId || null,
      token: localStorage.getItem("jwt_token") || "",
    };
  },
  created() {
    if (this.chatId) {
      this.fetchChatHistory();
    }
  },
  methods: {
    async fetchChatHistory() {
      if (!this.token) return;

      try {
        const response = await fetch("http://localhost:3000/api/chat/chat-history", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${this.token}`,
          },
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

      if (!this.token) {
        console.error("JWT Token bulunamadı!");
        return;
      }

      const payload = {
        type: this.chatId ? 2 : 1,
        message: this.userMessage,
      };

      if (this.chatId) {
        payload.chatId = this.chatId;
      }

      try {
        const response = await fetch("http://localhost:3000/api/chat/update-chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${this.token}`,
          },
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
      }

      this.userMessage = "";
    },
  },
  beforeRouteUpdate(to, from, next) {
    if (to.params.chatId !== from.params.chatId) {
      this.chatId = to.params.chatId;
      this.messages = [{ text: "Lütfen bana istediğini sor", sender: "receiver" }];
      this.fetchChatHistory();
    }
    next();
  },
};
</script>
