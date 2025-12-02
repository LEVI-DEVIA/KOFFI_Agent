# Fonctionnalités Audio de KOFFI

## 🎤 Reconnaissance Vocale (Speech-to-Text)

Koffi peut écouter et comprendre tes questions vocales :

1. Clique sur le bouton microphone 🎤
2. Parle clairement en français
3. Clique à nouveau pour arrêter l'enregistrement
4. Koffi transcrit automatiquement ta question

## 🔊 Synthèse Vocale (Text-to-Speech)

Koffi peut répondre en audio quand tu poses une question vocale :

### Comportement Automatique
- **Question vocale** → Réponse en audio 🔊
- **Question texte** → Réponse en texte 📝

### Contrôles Audio
- **Indicateur vert** : "🔊 Koffi parle..." s'affiche pendant la lecture
- **Bouton Arrêter** : Stoppe la lecture audio à tout moment
- **Auto-stop** : La lecture s'arrête automatiquement si tu poses une nouvelle question

## 🌐 Compatibilité Navigateur

### Reconnaissance Vocale (STT)
- ✅ Chrome / Edge (Web Speech API)
- ✅ Safari (avec permissions)
- ⚠️ Firefox (support limité)

### Synthèse Vocale (TTS)
- ✅ Tous les navigateurs modernes
- ✅ Voix française automatiquement sélectionnée
- ✅ Fonctionne hors ligne

## 🎯 Cas d'Usage

### Conversation Vocale Complète
```
1. 🎤 "Bonjour Koffi, comment vas-tu ?"
2. 🔊 Koffi répond en audio
3. 🎤 "Quelles sont les dernières news sur l'IA ?"
4. 🔊 Koffi répond en audio avec recherche web
```

### Conversation Mixte
```
1. ⌨️ "Bonjour" (texte)
2. 📝 Koffi répond en texte
3. 🎤 "Recherche des infos sur Tesla" (vocal)
4. 🔊 Koffi répond en audio
```

## ⚙️ Configuration

### Paramètres TTS (dans useTextToSpeech.ts)
```typescript
utterance.rate = 1.0;   // Vitesse (0.1 à 10)
utterance.pitch = 1.0;  // Ton (0 à 2)
utterance.volume = 1.0; // Volume (0 à 1)
utterance.lang = 'fr-FR'; // Langue
```

### Personnalisation
Tu peux modifier ces paramètres dans `frontend/hooks/useTextToSpeech.ts` pour :
- Accélérer/ralentir la voix
- Changer le ton
- Ajuster le volume
- Changer la langue

## 🐛 Dépannage

### La reconnaissance vocale ne fonctionne pas
- Vérifie les permissions du microphone dans ton navigateur
- Utilise Chrome ou Edge pour de meilleurs résultats
- Assure-toi d'avoir une connexion internet (requis pour la transcription)

### La synthèse vocale ne fonctionne pas
- Vérifie que le son n'est pas coupé
- Essaie de recharger la page
- Vérifie la console pour les erreurs

### La voix n'est pas en français
- Le système sélectionne automatiquement une voix française
- Si aucune voix française n'est disponible, la voix par défaut du système est utilisée
- Tu peux installer des voix supplémentaires dans les paramètres de ton système

## 🚀 Améliorations Futures

- [ ] Choix de la voix (masculine/féminine)
- [ ] Réglages de vitesse/ton dans l'UI
- [ ] Support de plusieurs langues
- [ ] Lecture pendant le streaming (mot par mot)
- [ ] Historique audio des conversations
