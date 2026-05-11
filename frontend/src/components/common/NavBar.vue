<template>
  <nav class="navbar">
    <div class="nav-inner">
      <router-link to="/dashboard" class="nav-brand">
        <HeartHandshake :size="24" /> DriftDater
      </router-link>

      <button class="nav-hamburger" @click="menuOpen = !menuOpen" aria-label="Menu">
        <Menu :size="22" />
      </button>

      <div class="nav-links" :class="{ open: menuOpen }" @click="menuOpen = false">
        <router-link to="/dashboard"><LayoutDashboard :size="16" /> Dashboard</router-link>
        <router-link to="/matches">
          <Heart :size="16" /> Matches
          <span v-if="matchCount > 0" class="nav-badge">{{ matchCount }}</span>
        </router-link>
        <router-link to="/messages"><MessageCircle :size="16" /> Messages</router-link>
        <router-link to="/search"><Search :size="16" /> Search</router-link>
        <router-link to="/favourites"><Star :size="16" /> Saved</router-link>
        <router-link to="/profile/edit" class="nav-profile-link">
          <img v-if="profilePic && !navImageError" :src="profilePic" class="nav-avatar" alt="Profile" @error="navImageError = true" />
          <span v-else class="nav-avatar-placeholder">{{ initials }}</span>
          {{ displayName }}
        </router-link>
        <button class="btn btn-sm btn-outline" @click="handleLogout">
          <LogOut :size="15" /> Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { matchesAPI, profilesAPI } from '@/api'
import {
  HeartHandshake, Heart, MessageCircle, Search,
  Star, LayoutDashboard, LogOut, Menu
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const menuOpen = ref(false)
const matchCount = ref(0)
const profilePic = ref(null)
const navImageError = ref(false)

const displayName = computed(() => auth.user?.username || '')
const initials = computed(() => (auth.user?.username || 'U').charAt(0).toUpperCase())

onMounted(async () => {
  try {
    const [mc, me] = await Promise.all([matchesAPI.getCount(), profilesAPI.getMe()])
    matchCount.value = mc.data.count
    if (me.data.profile?.profile_picture) {
      profilePic.value = profilesAPI.getPictureUrl(me.data.profile.profile_picture)
    }
  } catch { /* silent */ }
})

async function handleLogout() {
  await auth.logout()
  router.push('/')
}
</script>

<style scoped>
.navbar {
  background: #fff;
  border-bottom: 2px solid var(--border);
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 2px 12px rgba(108,99,255,0.08);
}
.nav-inner {
  max-width: 1100px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; height: 62px;
}
.nav-brand {
  font-size: 1.3rem; font-weight: 900; color: var(--primary);
  text-decoration: none; letter-spacing: -0.5px;
  display: flex; align-items: center; gap: 8px;
}
.nav-links {
  display: flex; align-items: center; gap: 4px; flex-wrap: wrap;
}
.nav-links a {
  padding: 7px 12px; border-radius: 50px; font-weight: 600; font-size: 0.88rem;
  color: var(--text-muted); text-decoration: none; transition: all 0.2s;
  display: flex; align-items: center; gap: 5px; position: relative;
}
.nav-links a:hover, .nav-links a.router-link-active {
  background: var(--border); color: var(--primary);
}
.nav-badge {
  background: var(--secondary); color: #fff; border-radius: 50px;
  font-size: 0.7rem; padding: 1px 6px; font-weight: 700;
}
.nav-avatar {
  width: 26px; height: 26px; border-radius: 50%; object-fit: cover;
  border: 2px solid var(--primary);
}
.nav-avatar-placeholder {
  width: 26px; height: 26px; border-radius: 50%;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; font-weight: 700;
}
.nav-profile-link { font-weight: 700 !important; }
.nav-hamburger {
  display: none; background: none; border: none; cursor: pointer;
  padding: 4px; color: var(--text);
}

@media (max-width: 768px) {
  .nav-hamburger { display: flex; }
  .nav-links {
    display: none; position: absolute; top: 62px; left: 0; right: 0;
    background: #fff; padding: 12px; flex-direction: column; align-items: flex-start;
    border-bottom: 2px solid var(--border); box-shadow: var(--shadow);
  }
  .nav-links.open { display: flex; }
}
</style>
