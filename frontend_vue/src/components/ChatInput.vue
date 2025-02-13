<template>
  <div class="input-group p-3 w-75 mx-auto chat-input">
    <input 
      type="text" 
      class="form-control border-success" 
      v-model="message"
      :disabled="loading"
      placeholder="Mesajınızı yazın..." 
      @keyup.enter="send"
    />
    <button class="btn btn-success" @click="send" :disabled="loading">
      <span v-if="loading" class="spinner-border spinner-border-sm"></span>
      <span v-else><i class="bi bi-send"></i></span>
    </button>
  </div>
</template>

<script>
export default {
  props: {
    modelValue: String,
    loading: Boolean,
  },
  computed: {
    message: {
      get() { return this.modelValue; },
      set(value) { this.$emit("update:modelValue", value); },
    },
  },
  methods: {
    send() {
      if (this.message.trim()) {
        this.$emit("send");
      }
    },
  },
};
</script>

<style scoped>
.chat-input {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 75%;
  background: white;
  box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}
</style>
