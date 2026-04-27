<template>
  <div class="sv-page">

    <!-- HERO -->
    <div class="sv-hero">
      <div class="sv-hero-icon">
        <v-icon size="36" color="#f59e0b">mdi-lightning-bolt-circle</v-icon>
      </div>
      <h1 class="sv-hero-title">Matching Sémantique</h1>
      <p class="sv-hero-sub">
        Entrez la désignation d'un article — le moteur trouve les correspondances
        dans le catalogue même si les mots sont différents.
      </p>
    </div>

    <!-- BARRE DE RECHERCHE -->
    <div class="sv-search-wrap">
      <div class="sv-search-box">
        <v-icon size="18" color="rgba(255,255,255,0.35)" class="sv-search-icon">mdi-text-search</v-icon>
        <input
          v-model="query"
          class="sv-search-input"
          placeholder="Ex: câble souple cuivre 2.5mm², disjoncteur bipolaire 20A…"
          @keydown.enter="search"
          autofocus
        />
        <button v-if="query" class="sv-clear" @click="query = ''; results = []">
          <v-icon size="14">mdi-close</v-icon>
        </button>
      </div>

      <!-- Options -->
      <div class="sv-options">
        <label class="sv-opt-label">Seuil min.</label>
        <input type="range" v-model.number="seuil" min="0.20" max="0.90" step="0.05" class="sv-slider"/>
        <span class="sv-opt-val">{{ Math.round(seuil * 100) }}%</span>
        <label class="sv-opt-label" style="margin-left:16px;">Résultats</label>
        <select v-model.number="topK" class="sv-select">
          <option :value="5">5</option>
          <option :value="8">8</option>
          <option :value="10">10</option>
          <option :value="15">15</option>
        </select>
        <label class="sv-opt-label sv-opt-check">
          <input type="checkbox" v-model="hybrid" /> Boost lexical
        </label>
        <button class="sv-btn-search" @click="search" :disabled="loading || !query.trim()">
          <v-icon v-if="loading" class="sv-spin" size="14">mdi-loading</v-icon>
          <v-icon v-else size="14">mdi-magnify</v-icon>
          Rechercher
        </button>
      </div>
    </div>

    <!-- RÉSULTATS -->
    <div class="sv-results" v-if="results.length || searched">

      <div v-if="!results.length && searched" class="sv-empty">
        <v-icon size="32" color="rgba(255,255,255,0.15)">mdi-text-search-variant</v-icon>
        <span>Aucun article trouvé — essayez de baisser le seuil ou reformulez.</span>
      </div>

      <div v-else class="sv-cards">
        <div class="sv-result-header">
          <span class="sv-result-count">{{ results.length }} résultat{{ results.length > 1 ? 's' : '' }}</span>
          <span class="sv-result-query">pour « {{ lastQuery }} »</span>
        </div>

        <div v-for="(r, i) in results" :key="r.id" class="sv-card"
             :class="{ 'sv-card--top': i === 0 }">
          <!-- Score -->
          <div class="sv-score-wrap">
            <div class="sv-score-bar">
              <div class="sv-score-fill" :style="{ width: r.score_pct + '%', background: scoreColor(r.score_pct) }"></div>
            </div>
            <span class="sv-score-val" :style="{ color: scoreColor(r.score_pct) }">{{ r.score_pct }}%</span>
            <span v-if="i === 0" class="sv-best-badge">Meilleur match</span>
          </div>
          <!-- Infos -->
          <div class="sv-card-body">
            <div class="sv-card-desig">{{ r.designation }}</div>
            <div class="sv-card-meta">
              <span v-if="r.reference" class="sv-chip">{{ r.reference }}</span>
              <span v-if="r.categorie" class="sv-chip sv-chip--cat">{{ r.categorie }}</span>
              <span v-if="r.marque" class="sv-chip sv-chip--brand">{{ r.marque }}</span>
            </div>
          </div>
          <!-- Prix -->
          <div class="sv-card-prix" v-if="r.prix_unitaire">
            {{ fmtNum(r.prix_unitaire) }} DA / {{ r.unite }}
          </div>
        </div>
      </div>
    </div>

    <!-- Explication -->
    <div class="sv-explain" v-if="!searched">
      <div class="sv-explain-item">
        <v-icon size="20" color="#f59e0b">mdi-brain</v-icon>
        <div>
          <div class="sv-exp-title">Compréhension sémantique</div>
          <div class="sv-exp-sub">« câble » ↔ « fil », « disjoncteur » ↔ « coupe-circuit », « vanne » ↔ « robinet »</div>
        </div>
      </div>
      <div class="sv-explain-item">
        <v-icon size="20" color="#60a5fa">mdi-translate</v-icon>
        <div>
          <div class="sv-exp-title">Multilingue</div>
          <div class="sv-exp-sub">Fonctionne en français, arabe, anglais et 50+ langues</div>
        </div>
      </div>
      <div class="sv-explain-item">
        <v-icon size="20" color="#34d399">mdi-lightning-bolt</v-icon>
        <div>
          <div class="sv-exp-title">Hybride lexical + sémantique</div>
          <div class="sv-exp-sub">Boost automatique quand les mots se recoupent aussi littéralement</div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const query    = ref('')
const seuil    = ref(0.45)
const topK     = ref(8)
const hybrid   = ref(true)
const results  = ref([])
const loading  = ref(false)
const searched = ref(false)
const lastQuery = ref('')

async function search() {
  if (!query.value.trim()) return
  loading.value  = true
  searched.value = false
  results.value  = []
  lastQuery.value = query.value
  try {
    const { data } = await api.post('/api/articles/search', {
      designation: query.value,
      top_k:       topK.value,
      seuil:       seuil.value,
      hybrid:      hybrid.value,
    })
    results.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value  = false
    searched.value = true
  }
}

function scoreColor(pct) {
  if (pct >= 80) return '#34d399'
  if (pct >= 60) return '#f59e0b'
  return '#94a3b8'
}

function fmtNum(n) {
  return Number(n).toLocaleString('fr-DZ', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.sv-page { flex: 1; padding: 40px 24px; max-width: 860px; margin: 0 auto; width: 100%; display: flex; flex-direction: column; gap: 32px; }

/* Hero */
.sv-hero { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 10px; }
.sv-hero-icon { width: 64px; height: 64px; border-radius: 18px; background: rgba(245,158,11,0.10); border: 1px solid rgba(245,158,11,0.20); display: flex; align-items: center; justify-content: center; }
.sv-hero-title { font-size: 28px; font-weight: 800; color: rgba(255,255,255,0.95); }
.sv-hero-sub { font-size: 14px; color: rgba(255,255,255,0.45); max-width: 500px; line-height: 1.6; }

/* Search */
.sv-search-wrap { display: flex; flex-direction: column; gap: 10px; }
.sv-search-box { position: relative; display: flex; align-items: center; }
.sv-search-icon { position: absolute; left: 14px; pointer-events: none; }
.sv-search-input {
  width: 100%; height: 52px; background: #141414;
  border: 1px solid rgba(255,255,255,0.15); border-radius: 12px;
  padding: 0 44px 0 44px; color: rgba(255,255,255,0.90);
  font-size: 14px; font-family: inherit; outline: none;
  transition: border-color 0.15s;
}
.sv-search-input:focus { border-color: rgba(245,158,11,0.45); }
.sv-search-input::placeholder { color: rgba(255,255,255,0.25); }
.sv-clear { position: absolute; right: 12px; background: none; border: none; cursor: pointer; color: rgba(255,255,255,0.35); display: flex; align-items: center; }

.sv-options { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.sv-opt-label { font-size: 11px; color: rgba(255,255,255,0.40); }
.sv-slider { accent-color: #f59e0b; width: 80px; cursor: pointer; }
.sv-opt-val { font-size: 11px; font-weight: 700; color: #f59e0b; min-width: 28px; }
.sv-select { background: #141414; border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 3px 6px; color: rgba(255,255,255,0.75); font-size: 11px; }
.sv-opt-check { display: flex; align-items: center; gap: 5px; cursor: pointer; }
.sv-opt-check input { accent-color: #f59e0b; }
.sv-btn-search {
  margin-left: auto; display: flex; align-items: center; gap: 6px;
  padding: 6px 16px; border-radius: 8px; font-size: 12px; font-weight: 700;
  background: #f59e0b; border: none; color: #000; cursor: pointer; transition: opacity 0.15s;
}
.sv-btn-search:hover:not(:disabled) { opacity: 0.85; }
.sv-btn-search:disabled { opacity: 0.40; cursor: default; }
.sv-spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Résultats */
.sv-result-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.sv-result-count { font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.85); }
.sv-result-query { font-size: 12px; color: rgba(255,255,255,0.40); }

.sv-empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 48px; color: rgba(255,255,255,0.30); font-size: 13px; }

.sv-cards { display: flex; flex-direction: column; gap: 8px; }
.sv-card {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 16px; border-radius: 10px;
  background: #141414; border: 1px solid rgba(255,255,255,0.08);
  transition: border-color 0.15s;
}
.sv-card:hover { border-color: rgba(255,255,255,0.18); }
.sv-card--top { border-color: rgba(245,158,11,0.25); background: rgba(245,158,11,0.04); }

.sv-score-wrap { display: flex; flex-direction: column; align-items: center; gap: 3px; flex-shrink: 0; width: 56px; }
.sv-score-bar { width: 100%; height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; overflow: hidden; }
.sv-score-fill { height: 100%; border-radius: 2px; transition: width 0.3s; }
.sv-score-val { font-size: 13px; font-weight: 800; }
.sv-best-badge { font-size: 9px; font-weight: 700; color: #f59e0b; letter-spacing: 0.03em; white-space: nowrap; }

.sv-card-body { flex: 1; min-width: 0; }
.sv-card-desig { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.88); line-height: 1.4; }
.sv-card-meta { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 5px; }
.sv-chip { font-size: 10px; font-weight: 600; padding: 1px 7px; border-radius: 12px; background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12); color: rgba(255,255,255,0.55); }
.sv-chip--cat   { background: rgba(96,165,250,0.08); border-color: rgba(96,165,250,0.20); color: #93c5fd; }
.sv-chip--brand { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.20); color: #fbbf24; }

.sv-card-prix { font-size: 12px; font-weight: 700; color: rgba(255,255,255,0.60); white-space: nowrap; flex-shrink: 0; }

/* Explication */
.sv-explain { display: flex; flex-direction: column; gap: 12px; padding: 20px; background: #111; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; }
.sv-explain-item { display: flex; align-items: flex-start; gap: 12px; }
.sv-exp-title { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.80); }
.sv-exp-sub   { font-size: 11px; color: rgba(255,255,255,0.38); margin-top: 2px; }
</style>
