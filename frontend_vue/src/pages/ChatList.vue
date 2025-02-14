<template>
  <div class="chat-list">
    <h3>Mesaj Atabileceğiniz Kişiler</h3>
    <ul>
      <li v-for="user in availableUsers" :key="user.id">
        {{ user.name }}
        <button @click="startChat(user.id)">Sohbet Et</button>
      </li>
    </ul>

    <h3>Geçmiş Konuşmalar</h3>
    <ul>
      <li v-for="chat in chatHistory" :key="chat.id">
        {{ chat.name }}
        <button @click="openChat(chat.id)">Sohbeti Aç</button>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      availableUsers: [],
      chatHistory: [],
    };
  },
  async created() {
    const response = await axios.get("/api/chat-users");
    this.availableUsers = response.data.users;
    this.chatHistory = response.data.history;
  },
  methods: {
    startChat(userId) {
      this.$router.push(`/sohbet/${userId}`);
    },
    openChat(chatId) {
      this.$router.push(`/sohbet/${chatId}`);
    }
  }
};
</script>
