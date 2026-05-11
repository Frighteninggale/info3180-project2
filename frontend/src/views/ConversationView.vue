<template>
  <div class="page conv-page">
    <div class="conv-header">
      <router-link to="/messages" class="btn btn-secondary btn-sm"><ChevronLeft :size="16" /> Back</router-link>
      <div v-if="partnerProfile" class="conv-partner">
        <img v-if="partnerPic && !partnerImageError" :src="partnerPic" class="partner-avatar" @error="partnerImageError = true" />
        <div v-else class="partner-placeholder"><UserCircle :size="34" color="#fff" /></div>
        <div>
          <strong>{{ partnerProfile.first_name }} {{ partnerProfile.last_name }}</strong>
          <div class="partner-loc" v-if="partnerProfile.city"><MapPin :size="11" /> {{ partnerProfile.city }}</div>
        </div>
      </div>
      <router-link v-if="partnerProfile" :to="`/profile/${partnerId}`" class="btn btn-outline btn-sm">
        <Eye :size="14" /> Profile
      </router-link>
    </div>

    <div class="messages-box" ref="msgBox">
      <div v-if="loading" class="spinner"></div>
      <div v-else-if="messages.length === 0" class="empty-msg">
        <Hand :size="32" color="#ccc" /><p>Say hello! Start the conversation.</p>
      </div>
      <template v-else>
        <div v-for="msg in messages" :key="msg.id" class="msg-bubble"
          :class="msg.sender_id === currentUserId ? 'msg-mine' : 'msg-theirs'">
          <div class="msg-content">{{ msg.content }}</div>
          <div class="msg-time"><Clock :size="10" /> {{ formatTime(msg.created_at) }}</div>
        </div>
      </template>
    </div>

    <div class="msg-input-bar">
      <input v-model="newMessage" type="text" placeholder="Type a message…"
        @keydown.enter="sendMessage" :disabled="sending" />
      <button class="btn btn-primary" @click="sendMessage" :disabled="!newMessage.trim() || sending">
        <Send :size="16" /> {{ sending ? '…' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { messagesAPI, profilesAPI } from '@/api'
import { ChevronLeft, UserCircle, MapPin, Eye, Hand, Clock, Send } from 'lucide-vue-next'

const route = useRoute()
const auth = useAuthStore()
const partnerId = Number(route.params.userId)
const currentUserId = computed(() => auth.user?.id)
const loading = ref(true), sending = ref(false)
const messages = ref([]), newMessage = ref('')
const partnerProfile = ref(null), partnerPic = ref(null)
const msgBox = ref(null)
const partnerImageError = ref(false)
let pollInterval = null

onMounted(async () => {
  try {
    const [msgs, profile] = await Promise.all([
      messagesAPI.getConversation(partnerId), profilesAPI.getById(partnerId)
    ])
    messages.value = msgs.data.messages
    partnerProfile.value = profile.data.profile
    partnerPic.value = profilesAPI.getPictureUrl(partnerProfile.value?.profile_picture)
  } catch {} finally { loading.value = false; scrollToBottom() }

  pollInterval = setInterval(async () => {
    try {
      const res = await messagesAPI.getConversation(partnerId)
      if (res.data.messages.length !== messages.value.length) {
        messages.value = res.data.messages; scrollToBottom()
      }
    } catch {}
  }, 3000)
})
onUnmounted(() => clearInterval(pollInterval))

async function sendMessage() {
  const content = newMessage.value.trim()
  if (!content || sending.value) return
  sending.value = true
  try {
    const res = await messagesAPI.send(partnerId, content)
    messages.value.push(res.data.data)
    newMessage.value = ''
    scrollToBottom()
  } catch (e) { alert(e.response?.data?.error || 'Failed to send') }
  finally { sending.value = false }
}
async function scrollToBottom() {
  await nextTick()
  if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
}
function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.conv-page { display:flex; flex-direction:column; height:calc(100vh - 62px); padding-bottom:0; }
.conv-header {
  display:flex; align-items:center; gap:14px; padding:12px 16px;
  background:var(--card); border-radius:var(--radius); margin-bottom:12px;
  box-shadow:var(--shadow); flex-wrap:wrap; flex-shrink:0;
}
.conv-partner { display:flex; align-items:center; gap:10px; flex:1; }
.partner-avatar { width:44px; height:44px; border-radius:50%; object-fit:cover; border:2px solid var(--primary); }
.partner-placeholder {
  width:44px; height:44px; border-radius:50%;
  background:linear-gradient(135deg,var(--primary),var(--secondary));
  display:flex; align-items:center; justify-content:center;
}
.partner-loc { font-size:0.78rem; color:var(--text-muted); display:flex; align-items:center; gap:3px; margin-top:2px; }
.messages-box {
  background:var(--card); border-radius:var(--radius); box-shadow:var(--shadow);
  padding:16px; flex:1; overflow-y:auto;
  display:flex; flex-direction:column; gap:10px; margin-bottom:12px;
}
.empty-msg { display:flex; flex-direction:column; align-items:center; gap:10px; color:var(--text-muted); margin:auto; text-align:center; }
.msg-bubble { display:flex; flex-direction:column; max-width:72%; }
.msg-mine { align-self:flex-end; align-items:flex-end; }
.msg-theirs { align-self:flex-start; align-items:flex-start; }
.msg-content { padding:10px 16px; border-radius:20px; font-size:0.95rem; line-height:1.5; word-break:break-word; }
.msg-mine .msg-content { background:var(--primary); color:#fff; border-bottom-right-radius:4px; }
.msg-theirs .msg-content { background:var(--border); color:var(--text); border-bottom-left-radius:4px; }
.msg-time { font-size:0.72rem; color:var(--text-muted); margin-top:3px; display:flex; align-items:center; gap:3px; }
.msg-input-bar {
  display:flex; gap:10px; background:var(--card); border-radius:var(--radius);
  padding:12px; box-shadow:var(--shadow); flex-shrink:0;
}
.msg-input-bar input { flex:1; padding:10px 16px; border:2px solid var(--border); border-radius:50px; font-size:0.95rem; outline:none; }
.msg-input-bar input:focus { border-color:var(--primary); }
</style>
