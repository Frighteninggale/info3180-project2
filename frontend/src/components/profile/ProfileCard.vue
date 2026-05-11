<template>
  <div class="profile-card" @click="$emit('click', profile)">
    <div class="pc-photo">
      <img v-if="picUrl" :src="picUrl" :alt="profile.first_name" @error="handleImageError" />
      <div v-else class="pc-placeholder">
        <UserCircle :size="54" color="#fff" />
      </div>
    </div>
    <div class="pc-info">
      <div class="pc-header">
        <span class="pc-name">{{ profile.first_name }} {{ profile.last_name }}, {{ profile.age }}</span>
        <span v-if="profile.match_score !== undefined" class="match-score">
          <Percent :size="12" /> {{ profile.match_score }}% match
        </span>
      </div>
      <div class="pc-location" v-if="profile.city">
        <MapPin :size="13" /> {{ profile.city }}, {{ profile.country }}
      </div>
      <p class="pc-bio">{{ profile.bio || 'No bio yet.' }}</p>
      <div class="pc-tags">
        <span v-for="i in profile.interests?.slice(0,4)" :key="i.id" class="tag">{{ i.name }}</span>
      </div>
      <div class="pc-actions" @click.stop>
        <slot name="actions">
          <button v-if="showLike" class="btn btn-success btn-sm" @click="$emit('like', profile)">
            <ThumbsUp :size="14" /> Like
          </button>
          <button v-if="showPass" class="btn btn-secondary btn-sm" @click="$emit('pass', profile)">
            <X :size="14" /> Pass
          </button>
          <button v-if="showFavourite" class="btn btn-sm" :class="isFav ? 'btn-fav-active' : 'btn-outline'" @click="$emit('favourite', profile)">
            <StarOff v-if="isFav" :size="14" /><Star v-else :size="14" />
            {{ isFav ? 'Saved' : 'Save' }}
          </button>
          <router-link :to="`/profile/${profile.user_id}`" class="btn btn-sm btn-secondary">
            <Eye :size="14" /> View
          </router-link>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { profilesAPI } from '@/api'
import { UserCircle, MapPin, ThumbsUp, X, Star, StarOff, Eye, Percent } from 'lucide-vue-next'

const props = defineProps({
  profile: { type: Object, required: true },
  showLike: { type: Boolean, default: false },
  showPass: { type: Boolean, default: false },
  showFavourite: { type: Boolean, default: false },
  isFav: { type: Boolean, default: false },
})
defineEmits(['like', 'pass', 'favourite', 'click'])

const imageLoadError = ref(false)

const picUrl = computed(() => {
  if (imageLoadError.value) {
    return null  // Return null to show placeholder
  }
  return profilesAPI.getPictureUrl(props.profile.profile_picture)
})

const handleImageError = () => {
  imageLoadError.value = true
  console.log(`Failed to load image for ${props.profile.first_name}`)
}

</script>

<style scoped>
.profile-card {
  display: flex; gap: 18px; background: var(--card);
  border-radius: var(--radius); box-shadow: var(--shadow);
  padding: 18px; margin-bottom: 16px; cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  border: 2px solid transparent;
}
.profile-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(108,99,255,0.18); border-color: var(--border); }
.pc-photo { flex-shrink: 0; }
.pc-photo img {
  width: 90px; height: 90px; border-radius: 50%; object-fit: cover;
  border: 3px solid var(--primary);
}
.pc-placeholder {
  width: 90px; height: 90px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex; align-items: center; justify-content: center;
}
.pc-info { flex: 1; min-width: 0; }
.pc-header { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }
.pc-name { font-size: 1.1rem; font-weight: 700; }
.match-score { display:inline-flex; align-items:center; gap:3px; }
.pc-location { display: flex; align-items: center; gap: 4px; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 6px; }
.pc-bio { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 8px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.pc-tags { margin-bottom: 10px; }
.pc-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn-fav-active { background: #fff3cd; color: #b8860b; border: 2px solid #f0c040; }
</style>
