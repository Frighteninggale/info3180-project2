<template>
  <div class="page">
    <div v-if="loading" class="spinner"></div>
    <div v-else-if="!profile" class="empty-state">Profile not found.</div>
    <template v-else>
      <div class="card profile-hero">
        <div class="ph-top">
          <img v-if="picUrl && !imageLoadError" :src="picUrl" class="ph-avatar" alt="Profile" @error="imageLoadError = true" />
          <div v-else class="ph-placeholder"><UserCircle :size="70" color="#fff" /></div>
          <div class="ph-main">
            <h1>{{ profile.first_name }} {{ profile.last_name }}, {{ profile.age }}</h1>
            <div class="ph-meta">
              <span v-if="profile.city"><MapPin :size="14" /> {{ profile.city }}, {{ profile.country }}</span>
              <span><Users :size="14" /> {{ profile.gender }}</span>
              <span v-if="profile.occupation"><Briefcase :size="14" /> {{ profile.occupation }}</span>
              <span v-if="profile.education_level"><GraduationCap :size="14" /> {{ profile.education_level }}</span>
            </div>
            <div v-if="profile.match_score !== undefined" class="match-score" style="font-size:1rem;padding:8px 16px;margin:8px 0;display:inline-flex;align-items:center;gap:5px;">
              <Percent :size="15" /> {{ profile.match_score }}% compatibility
            </div>
            <p class="ph-bio">{{ profile.bio || 'No bio yet.' }}</p>
          </div>
        </div>

        <div class="ph-interests" v-if="profile.interests?.length">
          <h3><Sparkles :size="16" /> Interests</h3>
          <div><span v-for="i in profile.interests" :key="i.id" class="tag">{{ i.name }}</span></div>
        </div>

        <div class="ph-actions">
          <template v-if="!isOwnProfile">
            <button v-if="myAction !== 'like'" class="btn btn-success" @click="handleLike">
              <ThumbsUp :size="16" /> Like
            </button>
            <button v-else class="btn btn-secondary" disabled>
              <Check :size="16" /> Liked
            </button>
            <button v-if="myAction !== 'pass'" class="btn btn-secondary" @click="handlePass">
              <X :size="16" /> Pass
            </button>
            <button class="btn" :class="isFav ? 'btn-fav-active' : 'btn-outline'" @click="toggleFav">
              <StarOff v-if="isFav" :size="16" /><Star v-else :size="16" />
              {{ isFav ? 'Saved' : 'Save' }}
            </button>
            <router-link v-if="isMutual" :to="`/messages/${profile.user_id}`" class="btn btn-primary">
              <MessageCircle :size="16" /> Message
            </router-link>
            <span v-if="isMutual" class="badge badge-success" style="display:flex;align-items:center;gap:4px;padding:8px 14px;">
              <HeartHandshake :size="15" /> Mutual Match!
            </span>
          </template>
          <router-link to="/dashboard" class="btn btn-secondary">
            <ChevronLeft :size="16" /> Back
          </router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { profilesAPI, matchesAPI, favouritesAPI } from '@/api'
import {
  UserCircle, MapPin, Users, Briefcase, GraduationCap, Percent,
  Sparkles, ThumbsUp, Check, X, Star, StarOff, MessageCircle,
  HeartHandshake, ChevronLeft
} from 'lucide-vue-next'

const route = useRoute()
const auth = useAuthStore()
const loading = ref(true)
const profile = ref(null), picUrl = ref(null)
const myAction = ref(null), isMutual = ref(false), isFav = ref(false)
const imageLoadError = ref(false)
const isOwnProfile = computed(() => profile.value?.user_id === auth.user?.id)

onMounted(async () => {
  const userId = Number(route.params.userId)
  try {
    const [pRes, statusRes, favRes] = await Promise.all([
      profilesAPI.getById(userId), matchesAPI.getStatus(userId), favouritesAPI.check(userId)
    ])
    profile.value = pRes.data.profile
    picUrl.value = profilesAPI.getPictureUrl(profile.value?.profile_picture)
    myAction.value = statusRes.data.my_action
    isMutual.value = statusRes.data.is_mutual
    isFav.value = favRes.data.is_favourite
  } catch {} finally { loading.value = false }
})

async function handleLike() {
  const res = await matchesAPI.action(profile.value.user_id, 'like')
  myAction.value = 'like'
  if (res.data.is_mutual) { isMutual.value = true; alert("It's a match!") }
}
async function handlePass() { await matchesAPI.action(profile.value.user_id, 'pass'); myAction.value = 'pass' }
async function toggleFav() {
  if (isFav.value) { await favouritesAPI.remove(profile.value.id); isFav.value = false }
  else { await favouritesAPI.add(profile.value.id); isFav.value = true }
}
</script>

<style scoped>
.ph-top { display:flex; gap:24px; flex-wrap:wrap; margin-bottom:20px; }
.ph-avatar { width:130px; height:130px; border-radius:50%; object-fit:cover; border:4px solid var(--primary); flex-shrink:0; }
.ph-placeholder {
  width:130px; height:130px; border-radius:50%;
  background:linear-gradient(135deg,var(--primary),var(--secondary));
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.ph-main { flex:1; min-width:0; }
h1 { font-size:1.8rem; font-weight:800; margin-bottom:8px; }
.ph-meta { display:flex; gap:14px; flex-wrap:wrap; color:var(--text-muted); font-size:0.9rem; margin-bottom:10px; }
.ph-meta span { display:flex; align-items:center; gap:4px; }
.ph-bio { color:var(--text-muted); line-height:1.6; }
.ph-interests { margin-bottom:20px; }
.ph-interests h3 { font-size:1rem; font-weight:700; margin-bottom:8px; color:var(--primary); display:flex; align-items:center; gap:5px; }
.ph-actions { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
.empty-state { text-align:center; padding:60px; color:var(--text-muted); }
.btn-fav-active { background:#fff3cd; color:#b8860b; border:2px solid #f0c040; }
</style>
