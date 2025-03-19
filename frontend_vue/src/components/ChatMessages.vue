<template>
  <div ref="messagesContainer" class="d-flex flex-column gap-2 w-75 chat-messages">
    <div 
      v-for="(msg, index) in messages" 
      :key="index"
      class="d-flex align-items-start gap-1"
      :class="msg.sender === 'sender' ? 'justify-content-end' : 'justify-content-start'"
    >
      <div v-if="msg.sender !== 'sender'" class="me-2">
        <img :src="file_path" alt="User" class="chat-avatar rounded-circle">
      </div>
      <div 
        class="p-3 shadow-sm position-relative rounded-3"
        :class="msg.sender === 'sender' ? 'bg-light border border-success sender-message' : 'bg-success text-white receiver-message'"
      >
        {{ msg.text }}
      </div>
    </div>

    <div v-if="loading" class="align-self-start text-muted loading-message animate-blink">
      <i class="bi bi-three-dots"></i> Yapay Zeka sana özel cevap üretiyor
    </div>
  </div>
</template>

<script>
import userAvatar from "../assets/yz-logo.png";

export default {
  props: {
    messages: Array,
    loading: Boolean,
  },
  data() {
    return {
      file_path: userAvatar, 
    };
  },
  watch: {
    messages() {
      this.scrollToBottom();
    },
    loading(newValue) {
      if (newValue) {
        this.scrollToBottom();
      }
    }
  },
  methods: {
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  },
  mounted() {
    this.scrollToBottom();
  }
};
</script>

<style scoped>
.chat-messages {
  height: calc(100vh - 150px);
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding-bottom: 20px; /* Alt kısımda mesaj giriş çubuğu ile çakışmayı engeller */
  margin-bottom: 20px; /* Alt boşluk ekleyerek mesaj giriş kutusunun mesajları kapatmasını önler */
}

.chat-messages::-webkit-scrollbar {
  display: none;
}

.chat-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
}

/* Yanıp sönme animasyonu */
@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.3; }
  100% { opacity: 1; }
}

.animate-blink {
  animation: blink 1.5s infinite;
}

/* Yapay zeka yüklenme mesajı için stil */
.loading-message {
  font-style: italic;
  font-size: 0.9rem;
}
</style>
