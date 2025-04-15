<template>
  <teleport to="body">
    <div v-if="show">
      <div class="modal fade show" style="display: block;" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Çıkış Onayı</h5>
              <button type="button" class="btn-close" @click="$emit('close')"></button>
            </div>
            <div class="modal-body">
              <p>Çıkış yapmak istediğinize emin misiniz?</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="$emit('close')">
                İptal
              </button>
              <button type="button" class="btn btn-danger" @click="$emit('confirm')">
                Çıkış Yap
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  </teleport>
</template>

<script>
export default {
  name: 'LogoutWarning',
  props: {
    show: {
      type: Boolean,
      required: true
    }
  }
}
</script>

<style scoped>
</style>
