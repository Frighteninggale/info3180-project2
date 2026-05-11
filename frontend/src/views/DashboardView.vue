<template>
  <div class="page">
    <div v-if="loading" class="spinner"></div>
    <template v-else>
      <!-- My Profile Summary -->
      <div class="card dash-header" v-if="myProfile">
        <div class="dash-profile">
          <img v-if="picUrl && !ownImageError" :src="picUrl" class="dash-avatar" alt="Profile" @error="ownImageError = true" />
          <div v-else class="dash-avatar-placeholder">
            <UserCircle :size="60" color="#fff" />
          </div>
          <div class="dash-info">
            <h2>Welcome, {{ myProfile.first_name }}!</h2>
            <div class="dash-meta">
              <span><CalendarDays :size="14" /> Age {{ myProfile.age }}</span>
              <span v-if="myProfile.city"><MapPin :size="14" /> {{ myProfile.city }}, {{ myProfile.country }}</span>
              <span v-if="myProfile.occupation"><Briefcase :size="14" /> {{ myProfile.occupation }}</span>
            </div>
            <p class="dash-bio">{{ myProfile.bio || 'No bio yet.' }}</p>
            <router-link to="/profile/edit" class="btn btn-primary btn-sm">
              <Pencil :size="14" /> Edit Profile
            </router-link>
          </div>
        </div>
        <div class="dash-stats">
          <div class="stat-box">
            <div class="stat-num">{{ matchCount }}</div>
            <div class="stat-label"><Heart :size="13" /> Matches</div>
          </div>
          <div class="stat-box">
            <div class="stat-num">{{ browseProfiles.length }}</div>
            <div class="stat-label"><Users :size="13" /> To Browse</div>
          </div>
        </div>
      </div>

      <h3 class="section-title"><Compass :size="20" /> Browse Potential Matches</h3>

      <div class="card filter-bar">
        <div class="filter-input-wrap">
          <Search :size="16" class="filter-icon" />
          <input v-model="filterName" type="text" placeholder="Search by name or bio…" class="filter-input" />
        </div>
        <select v-model="filterAge" class="filter-select">
          <option value="">All Ages</option>
          <option value="18-25">18–25</option>
          <option value="26-35">26–35</option>
          <option value="36-50">36–50</option>
          <option value="50+">50+</option>
        </select>
        <div class="filter-input-wrap">
          <MapPin :size="16" class="filter-icon" />
          <input v-model="filterCity" type="text" placeholder="Filter by location…" class="filter-input" />
        </div>
        <button class="btn btn-secondary btn-sm" @click="resetFilters"><X :size="14" /> Reset</button>
      </div>

      <div v-if="filteredProfiles.length === 0" class="empty-state">
        <SearchX :size="48" color="#ccc" />
        <p>No profiles to browse right now. Check back later!</p>
      </div>

      <ProfileCard
        v-for="p in filteredProfiles"
        :key="p.user_id"
        :profile="p"
        :show-like="true"
        :show-pass="true"
        :show-favourite="true"
        :is-fav="favouriteIds.has(p.id)"
        @like="handleLike"
        @pass="handlePass"
        @favourite="toggleFavourite"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { profilesAPI, matchesAPI, favouritesAPI } from '@/api'
import ProfileCard from '@/components/profile/ProfileCard.vue'
import {
  UserCircle, MapPin, Briefcase, CalendarDays, Pencil, Heart,
  Users, Compass, Search, X, SearchX
} from 'lucide-vue-next'

const loading = ref(true)
const myProfile = ref(null)
const picUrl = ref(null)
const browseProfiles = ref([])
const matchCount = ref(0)
const favouriteIds = ref(new Set())

const filterName = ref('')
const filterAge = ref('')
const filterCity = ref('')
const ownImageError = ref(false)

const filteredProfiles = computed(() => {
  let list = browseProfiles.value
  if (filterName.value) {
    const q = filterName.value.toLowerCase()
    list = list.filter(p => `${p.first_name} ${p.last_name} ${p.bio || ''}`.toLowerCase().includes(q))
  }
  if (filterCity.value) {
    const q = filterCity.value.toLowerCase()
    list = list.filter(p => (p.city || '').toLowerCase().includes(q) || (p.country || '').toLowerCase().includes(q))
  }
  if (filterAge.value) {
    const [minA, maxA] = filterAge.value === '50+' ? [50, 999] : filterAge.value.split('-').map(Number)
    list = list.filter(p => p.age >= minA && p.age <= maxA)
  }
  return list
})

function resetFilters() { filterName.value = ''; filterAge.value = ''; filterCity.value = '' }

onMounted(async () => {
  try {
    const [me, browse, mc, favs] = await Promise.all([
      profilesAPI.getMe(), profilesAPI.browse(),
      matchesAPI.getCount(), favouritesAPI.getAll(),
    ])
    myProfile.value = me.data.profile
    picUrl.value = profilesAPI.getPictureUrl(myProfile.value?.profile_picture)
    browseProfiles.value = browse.data.profiles
    matchCount.value = mc.data.count
    favouriteIds.value = new Set(favs.data.favourites.map(f => f.id))
  } catch (e) { console.error(e) } finally { loading.value = false }
})

async function handleLike(profile) {
  try {
    const res = await matchesAPI.action(profile.user_id, 'like')
    browseProfiles.value = browseProfiles.value.filter(p => p.user_id !== profile.user_id)
    if (res.data.is_mutual) { matchCount.value++; alert(`It's a match with ${profile.first_name}!`) }
  } catch (e) { alert(e.response?.data?.error || 'Error') }
}
async function handlePass(profile) {
  try {
    await matchesAPI.action(profile.user_id, 'pass')
    browseProfiles.value = browseProfiles.value.filter(p => p.user_id !== profile.user_id)
  } catch {}
}
async function toggleFavourite(profile) {
  try {
    if (favouriteIds.value.has(profile.id)) {
      await favouritesAPI.remove(profile.id); favouriteIds.value.delete(profile.id)
    } else {
      await favouritesAPI.add(profile.id); favouriteIds.value.add(profile.id)
    }
    favouriteIds.value = new Set(favouriteIds.value)
  } catch (e) { alert(e.response?.data?.error || 'Error') }
}
</script>

<style scoped>
.dash-header { margin-bottom:24px; }
.dash-profile { display:flex; gap:20px; flex-wrap:wrap; margin-bottom:20px; }
.dash-avatar { width:100px; height:100px; border-radius:50%; object-fit:cover; border:3px solid var(--primary); flex-shrink:0; }
.dash-avatar-placeholder {
  width:100px; height:100px; border-radius:50%;
  background:linear-gradient(135deg,var(--primary),var(--secondary));
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.dash-info { flex:1; min-width:0; }
h2 { font-size:1.5rem; font-weight:800; margin-bottom:6px; }
.dash-meta { display:flex; gap:14px; color:var(--text-muted); font-size:0.88rem; margin-bottom:8px; flex-wrap:wrap; align-items:center; }
.dash-meta span { display:flex; align-items:center; gap:4px; }
.dash-bio { color:var(--text-muted); font-size:0.9rem; margin-bottom:12px; }
.dash-stats { display:flex; gap:16px; }
.stat-box { text-align:center; background:var(--bg); border-radius:12px; padding:16px 28px; }
.stat-num { font-size:2rem; font-weight:900; color:var(--primary); }
.stat-label { font-size:0.8rem; color:var(--text-muted); font-weight:600; display:flex; align-items:center; justify-content:center; gap:4px; margin-top:2px; }
.section-title { font-size:1.2rem; font-weight:800; color:var(--primary); margin:20px 0 12px; display:flex; align-items:center; gap:8px; }
.filter-bar { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:20px; padding:14px 16px; align-items:center; }
.filter-input-wrap { position:relative; display:flex; align-items:center; flex:1; min-width:140px; }
.filter-icon { position:absolute; left:12px; color:var(--text-muted); pointer-events:none; }
.filter-input { padding:9px 14px 9px 36px; border:2px solid var(--border); border-radius:50px; font-size:0.9rem; outline:none; width:100%; }
.filter-input:focus { border-color:var(--primary); }
.filter-select { padding:9px 14px; border:2px solid var(--border); border-radius:50px; font-size:0.9rem; outline:none; }
.filter-select:focus { border-color:var(--primary); }
.empty-state { text-align:center; padding:60px 20px; color:var(--text-muted); display:flex; flex-direction:column; align-items:center; gap:14px; }
</style>
