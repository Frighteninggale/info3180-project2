<template>
  <div class="page">
    <h1 class="page-title">Edit Profile</h1>
    <div v-if="pageLoading" class="spinner"></div>
    <div v-else class="card">
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <div class="form-row">
        <div class="form-group">
          <label>First Name</label>
          <input v-model="form.first_name" type="text" />
        </div>
        <div class="form-group">
          <label>Last Name</label>
          <input v-model="form.last_name" type="text" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Date of Birth</label>
          <input v-model="form.date_of_birth" type="date" />
        </div>
        <div class="form-group">
          <label>Gender</label>
          <select v-model="form.gender">
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="non-binary">Non-binary</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>Looking For</label>
        <select v-model="form.looking_for">
          <option value="any">Any</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      </div>
      <div class="form-group">
        <label>Bio</label>
        <textarea v-model="form.bio" rows="3"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>City</label>
          <input v-model="form.city" type="text" />
        </div>
        <div class="form-group">
          <label>Country</label>
          <input v-model="form.country" type="text" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Occupation</label>
          <input v-model="form.occupation" type="text" />
        </div>
        <div class="form-group">
          <label>Education Level</label>
          <select v-model="form.education_level">
            <option value="high_school">High School</option>
            <option value="bachelor">Bachelor's</option>
            <option value="master">Master's</option>
            <option value="phd">PhD</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>Interests</label>
        <InterestSelector v-model="form.interests" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Min Age Preference</label>
          <input v-model.number="form.min_age_preference" type="number" min="18" max="99" />
        </div>
        <div class="form-group">
          <label>Max Age Preference</label>
          <input v-model.number="form.max_age_preference" type="number" min="18" max="99" />
        </div>
      </div>
      <div class="form-group">
        <label>Max Distance (km)</label>
        <input v-model.number="form.max_distance_km" type="number" min="1" max="20000" />
      </div>
      <div class="form-group">
        <label>Profile Picture</label>
        <div v-if="existingPic && !previewImageError" class="pic-preview"><img :src="existingPic" alt="Current" @error="previewImageError = true" /></div>
        <input type="file" accept="image/*" @change="onFileChange" style="margin-top:8px" />
      </div>
      <div class="form-group">
        <label><input type="checkbox" v-model="form.is_public" /> Make profile public</label>
      </div>

      <div class="form-actions">
        <button class="btn btn-primary btn-lg" @click="handleSave" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save Changes' }}
        </button>
        <router-link to="/dashboard" class="btn btn-secondary btn-lg">Cancel</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { profilesAPI } from '@/api'
import InterestSelector from '@/components/profile/InterestSelector.vue'

const pageLoading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const selectedFile = ref(null)
const existingPic = ref(null)

const form = reactive({
  first_name: '', last_name: '', date_of_birth: '', gender: '', looking_for: 'any',
  bio: '', city: '', country: '', occupation: '', education_level: '',
  interests: [], min_age_preference: 18, max_age_preference: 99,
  max_distance_km: 100, is_public: true,
})

onMounted(async () => {
  try {
    const res = await profilesAPI.getMe()
    const p = res.data.profile
    Object.keys(form).forEach(k => {
      if (k === 'interests') form.interests = p.interests?.map(i => i.name) || []
      else if (k in p) form[k] = p[k]
    })
    if (p.profile_picture) existingPic.value = profilesAPI.getPictureUrl(p.profile_picture)
  } catch (e) { error.value = 'Failed to load profile' } finally { pageLoading.value = false }
})

function onFileChange(e) {
  selectedFile.value = e.target.files[0]
  if (selectedFile.value) existingPic.value = URL.createObjectURL(selectedFile.value)
}

async function handleSave() {
  error.value = ''; success.value = ''
  saving.value = true
  try {
    const fd = new FormData()
    Object.entries(form).forEach(([k, v]) => {
      if (k === 'interests') v.forEach(i => fd.append('interests', i))
      else fd.append(k, String(v))
    })
    if (selectedFile.value) fd.append('profile_picture', selectedFile.value)
    await profilesAPI.updateMe(fd)
    success.value = 'Profile updated successfully!'
  } catch (e) { error.value = e.response?.data?.error || 'Failed to save' }
  finally { saving.value = false }
}
</script>

<style scoped>
.form-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.pic-preview img { width:100px; height:100px; border-radius:50%; object-fit:cover; border:3px solid var(--primary); }
.form-actions { display:flex; gap:12px; margin-top:8px; flex-wrap:wrap; }
@media(max-width:500px){.form-row{grid-template-columns:1fr;}}
</style>
