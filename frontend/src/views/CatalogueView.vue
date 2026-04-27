<template>
  <div class="cv-page">
    <div class="cv-header">
      <h2 class="cv-title">Catalogue Articles</h2>
      <button class="cv-btn-add" @click="showModal = true">
        <v-icon size="14">mdi-plus</v-icon> Ajouter un article
      </button>
    </div>

    <!-- Filtres -->
    <div class="cv-filters">
      <div class="cv-search-wrap">
        <v-icon size="14" color="rgba(255,255,255,0.35)" class="cv-si">mdi-magnify</v-icon>
        <input v-model="q" class="cv-fi" placeholder="Filtrer par désignation…" @input="load"/>
      </div>
      <select v-model="catFilter" @change="load" class="cv-select">
        <option value="">Toutes catégories</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <button class="cv-btn-reindex" @click="reindex" :disabled="reindexing" title="Recalculer tous les embeddings">
        <v-icon size="13">mdi-refresh</v-icon>
        {{ reindexing ? 'En cours…' : 'Reindexer' }}
      </button>
    </div>

    <!-- Liste -->
    <div class="cv-table-wrap">
      <table class="cv-table">
        <thead>
          <tr>
            <th>Référence</th>
            <th>Désignation</th>
            <th>Catégorie</th>
            <th>Marque</th>
            <th>Prix HT</th>
            <th>Vecteur</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="cv-loading">Chargement…</td></tr>
          <tr v-else-if="!articles.length"><td colspan="6" class="cv-empty">Aucun article</td></tr>
          <tr v-for="a in articles" :key="a.id" class="cv-row">
            <td class="cv-ref">{{ a.reference }}</td>
            <td class="cv-desig">{{ a.designation }}</td>
            <td class="cv-cat">{{ a.categorie || '—' }}</td>
            <td class="cv-brand">{{ a.marque || '—' }}</td>
            <td class="cv-prix">{{ a.prix_unitaire ? fmtNum(a.prix_unitaire) + ' DA' : '—' }}</td>
            <td>
              <span class="cv-emb" :class="a.has_embedding ? 'cv-emb--ok' : 'cv-emb--no'">
                {{ a.has_embedding ? '✓' : '○' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal ajout -->
    <div v-if="showModal" class="cv-overlay" @click.self="showModal = false">
      <div class="cv-modal">
        <div class="cv-modal-hd">
          <v-icon size="16" color="#f59e0b">mdi-plus-circle-outline</v-icon>
          Nouvel article
          <button class="cv-modal-close" @click="showModal = false"><v-icon size="15">mdi-close</v-icon></button>
        </div>
        <div class="cv-modal-body">
          <div class="cv-fg"><label class="cv-lbl">Référence *</label><input class="cv-inp" v-model="form.reference" /></div>
          <div class="cv-fg"><label class="cv-lbl">Désignation *</label><input class="cv-inp" v-model="form.designation" /></div>
          <div class="cv-fg"><label class="cv-lbl">Catégorie</label><input class="cv-inp" v-model="form.categorie" /></div>
          <div class="cv-fg"><label class="cv-lbl">Sous-catégorie</label><input class="cv-inp" v-model="form.sous_categorie" /></div>
          <div class="cv-fg"><label class="cv-lbl">Marque</label><input class="cv-inp" v-model="form.marque" /></div>
          <div class="cv-row-2">
            <div class="cv-fg"><label class="cv-lbl">Prix HT</label><input class="cv-inp" type="number" v-model.number="form.prix_unitaire" /></div>
            <div class="cv-fg"><label class="cv-lbl">Unité</label><input class="cv-inp" v-model="form.unite" /></div>
          </div>
          <div v-if="formErr" class="cv-err">{{ formErr }}</div>
        </div>
        <div class="cv-modal-ft">
          <button class="cv-cancel" @click="showModal = false">Annuler</button>
          <button class="cv-submit" @click="addArticle" :disabled="saving">
            <v-icon v-if="saving" size="13" class="cv-spin">mdi-loading</v-icon>
            Enregistrer + vectoriser
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

const articles   = ref([])
const loading    = ref(false)
const q          = ref('')
const catFilter  = ref('')
const showModal  = ref(false)
const saving     = ref(false)
const formErr    = ref('')
const reindexing = ref(false)

const form = ref({ reference: '', designation: '', categorie: '', sous_categorie: '', marque: '', prix_unitaire: 0, unite: 'U' })

const categories = computed(() => [...new Set(articles.value.map(a => a.categorie).filter(Boolean))])

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/articles/', { params: { q: q.value || undefined, categorie: catFilter.value || undefined, limit: 200 } })
    articles.value = data
  } finally { loading.value = false }
}

async function addArticle() {
  formErr.value = ''
  if (!form.value.reference || !form.value.designation) { formErr.value = 'Référence et désignation obligatoires.'; return }
  saving.value = true
  try {
    await api.post('/api/articles/', form.value)
    showModal.value = false
    form.value = { reference: '', designation: '', categorie: '', sous_categorie: '', marque: '', prix_unitaire: 0, unite: 'U' }
    await load()
  } catch (e) {
    formErr.value = e?.response?.data?.detail || 'Erreur lors de la création.'
  } finally { saving.value = false }
}

async function reindex() {
  reindexing.value = true
  try { await api.post('/api/articles/reindex'); await new Promise(r => setTimeout(r, 3000)); await load() }
  finally { reindexing.value = false }
}

function fmtNum(n) {
  return Number(n).toLocaleString('fr-DZ', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(load)
</script>

<style scoped>
.cv-page { flex: 1; padding: 28px 24px; display: flex; flex-direction: column; gap: 16px; max-width: 1100px; margin: 0 auto; width: 100%; }
.cv-header { display: flex; align-items: center; justify-content: space-between; }
.cv-title { font-size: 20px; font-weight: 800; color: rgba(255,255,255,0.90); }
.cv-btn-add { display: flex; align-items: center; gap: 5px; padding: 6px 14px; border-radius: 8px; background: rgba(245,158,11,0.14); border: 1px solid rgba(245,158,11,0.30); color: #f59e0b; font-size: 12px; font-weight: 700; cursor: pointer; transition: background 0.15s; }
.cv-btn-add:hover { background: rgba(245,158,11,0.22); }

.cv-filters { display: flex; align-items: center; gap: 8px; }
.cv-search-wrap { position: relative; flex: 1; display: flex; align-items: center; }
.cv-si { position: absolute; left: 10px; pointer-events: none; }
.cv-fi { width: 100%; height: 32px; background: #141414; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 0 10px 0 30px; color: rgba(255,255,255,0.85); font-size: 12px; outline: none; }
.cv-select { height: 32px; background: #141414; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 0 8px; color: rgba(255,255,255,0.75); font-size: 12px; }
.cv-btn-reindex { display: flex; align-items: center; gap: 5px; padding: 0 12px; height: 32px; background: transparent; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; color: rgba(255,255,255,0.50); font-size: 11px; cursor: pointer; transition: all 0.15s; }
.cv-btn-reindex:hover:not(:disabled) { border-color: rgba(255,255,255,0.25); color: rgba(255,255,255,0.80); }
.cv-btn-reindex:disabled { opacity: 0.40; cursor: default; }

.cv-table-wrap { border: 1px solid rgba(255,255,255,0.10); border-radius: 10px; overflow: hidden; overflow-x: auto; }
.cv-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.cv-table thead th { background: #141414; padding: 9px 12px; text-align: left; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: rgba(255,255,255,0.45); border-bottom: 1px solid rgba(255,255,255,0.10); }
.cv-row td { padding: 9px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: middle; }
.cv-row:hover td { background: rgba(255,255,255,0.02); }
.cv-ref   { color: rgba(255,255,255,0.55); font-size: 11px; white-space: nowrap; }
.cv-desig { color: rgba(255,255,255,0.85); font-weight: 500; }
.cv-cat   { color: #93c5fd; font-size: 11px; }
.cv-brand { color: #fbbf24; font-size: 11px; }
.cv-prix  { color: rgba(255,255,255,0.60); text-align: right; white-space: nowrap; }
.cv-emb   { font-size: 13px; font-weight: 700; }
.cv-emb--ok { color: #34d399; }
.cv-emb--no { color: rgba(255,255,255,0.20); }
.cv-loading, .cv-empty { padding: 32px; text-align: center; color: rgba(255,255,255,0.30); font-size: 13px; }

/* Modal */
.cv-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.75); display: flex; align-items: center; justify-content: center; z-index: 100; }
.cv-modal { background: #141414; border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; width: 460px; max-width: 96vw; box-shadow: 0 24px 80px rgba(0,0,0,0.60); }
.cv-modal-hd { display: flex; align-items: center; gap: 8px; padding: 14px 18px; font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.88); border-bottom: 1px solid rgba(255,255,255,0.10); }
.cv-modal-close { margin-left: auto; background: none; border: none; color: rgba(255,255,255,0.35); cursor: pointer; }
.cv-modal-body { padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; }
.cv-modal-ft { display: flex; justify-content: flex-end; gap: 8px; padding: 12px 18px 16px; border-top: 1px solid rgba(255,255,255,0.10); }
.cv-fg { display: flex; flex-direction: column; gap: 4px; }
.cv-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.cv-lbl { font-size: 10px; font-weight: 700; color: rgba(255,255,255,0.40); text-transform: uppercase; letter-spacing: 0.05em; }
.cv-inp { background: #0d0d0d; border: 1px solid rgba(255,255,255,0.12); border-radius: 7px; padding: 7px 10px; color: rgba(255,255,255,0.85); font-size: 12px; width: 100%; outline: none; }
.cv-err { color: #f87171; font-size: 11px; }
.cv-cancel { padding: 6px 14px; border-radius: 7px; background: transparent; border: 1px solid rgba(255,255,255,0.12); color: rgba(255,255,255,0.50); font-size: 12px; font-weight: 600; cursor: pointer; }
.cv-submit { display: flex; align-items: center; gap: 6px; padding: 6px 16px; border-radius: 7px; background: #f59e0b; border: none; color: #000; font-size: 12px; font-weight: 700; cursor: pointer; transition: opacity 0.15s; }
.cv-submit:hover:not(:disabled) { opacity: 0.85; }
.cv-submit:disabled { opacity: 0.40; cursor: default; }
.cv-spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
