<template>
  <div class="chat-room">
    <h3>{{ otherUserName }} ile Sohbet</h3>
    <div class="messages">
      <div v-for="msg in messages" :key="msg.timestamp" :class="msg.sender === userId ? 'sent' : 'received'">
        {{ msg.text }}
      </div>
    </div>
    <input v-model="messageText" @keyup.enter="sendMessage" placeholder="Mesajınızı yazın...">
    <button @click="sendMessage">Gönder</button>
  </div>
</template>

<script>
import { io } from "socket.io-client";

export default {
  data() {
    return {
      socket: null,
      messages: [],
      messageText: "",
      otherUserId: this.$route.params.userId,
      userId: localStorage.getItem("userId"),
    };
  },
  created() {
    this.socket = io("http://localhost:5000", { auth: { token: localStorage.getItem("token") } });

    this.socket.emit("join_room", { otherUserId: this.otherUserId });

    this.socket.on("receive_message", (message) => {
      this.messages.push(message);
    });
  },
  methods: {
    sendMessage() {
      if (this.messageText.trim()) {
        this.socket.emit("send_message", { otherUserId: this.otherUserId, message: this.messageText });
        this.messages.push({ sender: this.userId, text: this.messageText });
        this.messageText = "";
      }
    }
  }
};
</script>
