<template>
  <teleport to="body">
    <div v-if="show">
      <div class="modal fade show" style="display: block;" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Oturum Süresi Doldu</h5>
            </div>
            <div class="modal-body">
              <p>Oturumunuzun süresi doldu. Lütfen tekrar giriş yapın.</p>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-primary"
                @click="$emit('confirm')"
              >
                TAMAM
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
  name: 'SessionExpiredWarning',
  props: {
    show: { type: Boolean, required: true }
  }
}
</script>