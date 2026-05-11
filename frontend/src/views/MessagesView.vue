<template>
  <div class="page">
    <h1 class="page-title"><MessageCircle :size="26" /> Messages</h1>
    <div v-if="loading" class="spinner"></div>
    <div v-else-if="conversations.length === 0" class="empty-state">
      <MailOpen :size="54" color="#ccc" />
      <p>No conversations yet. Match with someone to start chatting!</p>
      <router-link to="/matches" class="btn btn-primary" style="margin-top:16px">
        <Heart :size="16" /> View Matches
      </router-link>
    </div>
    <div v-else class="conv-list">
      <router-link v-for="conv in conversations" :key="conv.partner_id" :to="`/messages/${conv.partner_id}`" class="conv-item">
        <div class="conv-avatar">
          <img v-if="getPic(conv)" :src="getPic(conv)" :alt="conv.profile?.first_name"  @error="handleImageError(conv.partner_id)" />
          <div v-if="!getPic(conv) || imageLoadError[conv.partner_id]" class="conv-placeholder"><UserCircle :size="38" color="#fff" /></div>
        </div>
        <div class="conv-info">
          <div class="conv-header">
            <span class="conv-name">{{ conv.profile?.first_name }} {{ conv.profile?.last_name }}</span>
            <span class="conv-time" v-if="conv.last_message">{{ formatTime(conv.last_message.created_at) }}</span>
          </div>
          <div class="conv-preview">
            <span v-if="conv.last_message">{{ conv.last_message.content }}</span>
            <span v-else class="no-msg"><MessageSquareDashed :size="13" /> No messages yet</span>
          </div>
        </div>
        <span v-if="conv.unread_count > 0" class="unread-badge">{{ conv.unread_count }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { messagesAPI, profilesAPI } from '@/api'
import { MessageCircle, MailOpen, Heart, UserCircle, MessageSquareDashed } from 'lucide-vue-next'

const loading = ref(true)
const conversations = ref([])
const imageLoadError = ref({})

function handleImageError(partnerId) {
  imageLoadError.value[partnerId] = true
}

function getPic(conv) {
  if (imageLoadError.value[conv.partner_id]) return null
  return profilesAPI.getPictureUrl(conv.profile?.profile_picture)
}

onMounted(async () => {
  try { const res = await messagesAPI.getConversations(); conversations.value = res.data.conversations }
  catch {} finally { loading.value = false }
})
function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso), now = new Date()
  return (now - d) < 86400000
    ? d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : d.toLocaleDateString()
}
</script>

<style scoped>
.conv-list { display:flex; flex-direction:column; gap:8px; }
.conv-item {
  display:flex; align-items:center; gap:14px; background:var(--card);
  border-radius:var(--radius); padding:14px 18px; box-shadow:var(--shadow);
  text-decoration:none; color:var(--text); transition:all 0.15s; position:relative;
}
.conv-item:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(108,99,255,0.15); }
.conv-avatar { flex-shrink:0; }
.conv-avatar img { width:52px; height:52px; border-radius:50%; object-fit:cover; border:2px solid var(--primary); }
.conv-placeholder {
  width:52px; height:52px; border-radius:50%;
  background:linear-gradient(135deg,var(--primary),var(--secondary));
  display:flex; align-items:center; justify-content:center;
}
.conv-info { flex:1; min-width:0; }
.conv-header { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:3px; }
.conv-name { font-weight:700; font-size:1rem; }
.conv-time { font-size:0.78rem; color:var(--text-muted); }
.conv-preview { font-size:0.87rem; color:var(--text-muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.no-msg { display:flex; align-items:center; gap:4px; }
.unread-badge { background:var(--secondary); color:#fff; border-radius:50%; width:22px; height:22px; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; flex-shrink:0; }
.empty-state { text-align:center; padding:60px 20px; color:var(--text-muted); display:flex; flex-direction:column; align-items:center; gap:14px; }
</style>
