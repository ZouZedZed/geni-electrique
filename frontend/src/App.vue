<template>
  <div class="ge-app">
    <!-- TOPBAR -->
    <div class="ge-topbar">
      <div class="ge-topbar-brand">
        <v-icon size="22" color="#f59e0b">mdi-lightning-bolt</v-icon>
        <span class="ge-topbar-title">Géni Électrique</span>
      </div>
      <nav class="ge-nav">
        <router-link to="/" class="ge-nav-link" :class="{ active: $route.path === '/' }">
          <v-icon size="15">mdi-magnify</v-icon> Matching
        </router-link>
        <router-link to="/catalogue" class="ge-nav-link" :class="{ active: $route.path === '/catalogue' }">
          <v-icon size="15">mdi-database-outline</v-icon> Catalogue
        </router-link>
      </nav>
    </div>

    <!-- CONTENU -->
    <router-view />
  </div>
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', 'Segoe UI', sans-serif; background: #0d0d0d; color: rgba(255,255,255,0.88); }

.ge-app { min-height: 100vh; display: flex; flex-direction: column; }

.ge-topbar {
  display: flex; align-items: center; height: 56px; padding: 0 24px;
  background: #141414; border-bottom: 1px solid rgba(255,255,255,0.10);
  flex-shrink: 0; gap: 32px;
}
.ge-topbar-brand { display: flex; align-items: center; gap: 8px; }
.ge-topbar-title { font-size: 16px; font-weight: 800; color: rgba(255,255,255,0.90); letter-spacing: 0.02em; }

.ge-nav { display: flex; align-items: center; gap: 4px; }
.ge-nav-link {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 12px; border-radius: 7px;
  font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.45);
  text-decoration: none; transition: all 0.15s;
}
.ge-nav-link:hover { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.80); }
.ge-nav-link.active { background: rgba(245,158,11,0.12); color: #f59e0b; }
</style>
