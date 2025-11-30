# Architecture Multi-Agents KOFFI

## Vue d'ensemble

KOFFI utilise une architecture multi-agents avec un agent orchestrateur principal et des agents spécialisés.

```
┌─────────────────┐
│     KOFFI       │  ← Agent orchestrateur principal
│  (Coordinateur) │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼───┐
│NATACHA│   │PASCAL │  ← Agents spécialisés
│🍕     │   │🔍     │
└───────┘   └───────┘
```

## Agents Spécialisés

### 🍕 NATACHA - Agent de Commande Glovo
- **Technologie**: ADK + Playwright
- **Spécialité**: Commandes de nourriture sur Glovo Abidjan Nord
- **Site cible**: https://glovoapp.com/fr/ci/abidjan-nord

#### Capacités:
- Navigation automatique sur Glovo
- Gestion de l'authentification utilisateur
- Recherche de restaurants en temps réel
- Consultation des menus actualisés
- Ajout d'articles au panier
- Passage de commandes

#### Gestion de l'authentification:
1. **Connexion manuelle** (recommandée) : L'utilisateur se connecte dans le navigateur ouvert
2. **Connexion automatique** : Stockage sécurisé des identifiants avec consentement
3. **Mode invité** : Si disponible sur Glovo

### 🔍 PASCAL - Agent de Recherche Internet
- **Technologie**: ADK + Google Search API
- **Spécialité**: Recherche d'informations sur Internet

#### Capacités:
- Recherches Google ciblées
- Actualités et informations actualisées
- Prix et comparaisons
- Définitions et explications
- Statistiques et données factuelles

## 🧠 KOFFI - Agent Orchestrateur

### Rôle principal:
1. **Analyse** des demandes utilisateur
2. **Décision** de délégation aux agents spécialisés
3. **Coordination** des réponses
4. **Maintien** du contexte et de la mémoire

### Règles de délégation:

#### ➡️ Vers NATACHA:
- Mots-clés: "commander", "pizza", "restaurant", "nourriture", "livraison", "glovo"
- Exemples: "Je veux commander une pizza", "Trouve-moi un restaurant"

#### ➡️ Vers PASCAL:
- Mots-clés: "recherche", "actualités", "prix", "qu'est-ce que", "comment"
- Exemples: "Quel temps fait-il ?", "Prix de l'iPhone"

#### ➡️ Réponse directe:
- Salutations, conversations générales
- Gestion de la mémoire
- Coordination entre agents

## Installation et Configuration

### 1. Installation de Playwright pour Natacha
```bash
cd backend/koffi/sub_agent/natacha
python install_playwright.py
```

### 2. Configuration des variables d'environnement
```bash
# backend/koffi/sub_agent/natacha/.env
GLOVO_BASE_URL=https://glovoapp.com/fr/ci/abidjan-nord
BROWSER_HEADLESS=false
AUTH_STORAGE_ENABLED=true
```

### 3. Démarrage du système
```bash
cd backend
python -m koffi.agent
```

## Sécurité et Confidentialité

### Authentification Glovo:
- **Consentement explicite** requis pour le stockage des identifiants
- **Chiffrement** des données sensibles
- **Option de suppression** des données à tout moment
- **Connexion manuelle** comme option par défaut

### Gestion des données:
- Stockage local sécurisé
- Pas de partage avec des tiers
- Respect du RGPD
- Transparence totale sur l'utilisation

## Interface Utilisateur

### Indicateurs visuels:
- 🍕 **Natacha active** : Pour les commandes Glovo
- 🔍 **Pascal active** : Pour les recherches Internet
- 🧠 **Koffi coordonne** : Gestion générale

### Exemples d'interactions:

```
Utilisateur: "J'ai faim, je veux commander une pizza"
Koffi: "Parfait ! Je vais demander à Natacha 🍕 de t'aider à trouver les meilleures pizzerias d'Abidjan Nord."
→ Délégation à Natacha

Utilisateur: "Quel temps fait-il à Abidjan ?"
Koffi: "Je demande à Pascal 🔍 de chercher les conditions météo actuelles !"
→ Délégation à Pascal
```

## Avantages de cette Architecture

### ✅ Spécialisation:
- Chaque agent excelle dans son domaine
- Outils optimisés pour chaque tâche
- Maintenance facilitée

### ✅ Évolutivité:
- Ajout facile de nouveaux agents spécialisés
- Modification indépendante des agents
- Scalabilité horizontale

### ✅ Sécurité:
- Isolation des fonctionnalités sensibles
- Gestion granulaire des permissions
- Authentification sécurisée

### ✅ Expérience utilisateur:
- Transparence sur les actions
- Réponses spécialisées et précises
- Continuité conversationnelle

## Développement Futur

### Agents potentiels:
- **Agent E-commerce** : Autres plateformes de livraison
- **Agent Transport** : Réservation de taxis/transport
- **Agent Météo** : Prévisions détaillées
- **Agent Actualités** : News locales spécialisées

### Améliorations prévues:
- Interface web pour la gestion des agents
- Métriques et analytics
- API publique pour intégrations
- Support multi-langues