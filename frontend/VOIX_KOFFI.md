# 🎙️ Voix de KOFFI

## 🎯 Configuration

KOFFI est un agent masculin et possède donc une **voix masculine française** imposée automatiquement.

## 🔧 Sélection Automatique de la Voix

### Algorithme de Sélection

Le système sélectionne automatiquement la meilleure voix masculine disponible selon cet ordre de priorité :

#### Priorité 1 : Voix Masculine Explicite 🎖️
Recherche de voix avec des noms masculins courants :
- `male` (anglais)
- `homme` (français)
- `man` (anglais)
- Prénoms masculins : `thomas`, `daniel`, `nicolas`, `paul`, `pierre`, `laurent`

#### Priorité 2 : Exclusion des Voix Féminines 🚫
Si aucune voix masculine explicite n'est trouvée, sélectionne une voix française qui n'est PAS féminine :
- Exclusion de : `female`, `femme`, `woman`
- Exclusion des prénoms féminins : `amelie`, `marie`, `claire`, `julie`, `sophie`, `lea`, `emma`

#### Priorité 3 : Première Voix Française 🇫🇷
Si aucune voix masculine n'est identifiée, utilise la première voix française disponible.

#### Priorité 4 : Voix par Défaut 🔊
En dernier recours, utilise la voix par défaut du système.

## ⚙️ Paramètres de la Voix

### Configuration Actuelle
```typescript
utterance.lang = 'fr-FR';      // Langue française
utterance.rate = 1.0;          // Vitesse normale
utterance.pitch = 0.9;         // Ton légèrement grave (masculin)
utterance.volume = 1.0;        // Volume maximum
```

### Explication des Paramètres

#### `pitch` (Ton) : 0.9
- Valeur par défaut : `1.0`
- KOFFI : `0.9` (légèrement plus grave)
- Effet : Rend la voix plus masculine et grave
- Plage possible : `0.0` à `2.0`

#### `rate` (Vitesse) : 1.0
- Vitesse normale de lecture
- Plage possible : `0.1` à `10.0`
- `1.0` = vitesse naturelle

#### `volume` (Volume) : 1.0
- Volume maximum pour une bonne audibilité
- Plage possible : `0.0` à `1.0`

## 🌐 Voix Disponibles par Système

### Windows 10/11
Voix françaises masculines courantes :
- `Microsoft Paul - French (France)`
- `Microsoft Hortense - French (France)` (féminine - évitée)

### macOS
Voix françaises masculines courantes :
- `Thomas (French (France))`
- `Daniel (French (France))`

### Linux (Ubuntu)
Voix françaises via espeak :
- `French (France)` (voix par défaut)

### Chrome/Edge
Utilise les voix du système + voix Google :
- `Google français` (voix neutre/masculine)

### Safari
Utilise les voix macOS natives :
- `Thomas`, `Daniel`

### Firefox
Utilise les voix du système

## 🔍 Debug : Voir les Voix Disponibles

Au chargement de l'application, la console affiche automatiquement toutes les voix disponibles :

```
🎙️ Voix disponibles sur ce système:
🇫🇷 1. Thomas (fr-FR) ⭐
🇫🇷 2. Daniel (fr-FR)
   3. Google US English (en-US)
   4. Google UK English (en-GB)
...
```

- 🇫🇷 = Voix française
- ⭐ = Voix par défaut du système

## 📊 Exemples de Sélection

### Exemple 1 : macOS avec Thomas
```
Voix disponibles : Thomas, Daniel, Amelie
Sélection : Thomas (priorité 1 - nom masculin)
Console : 🎙️ Voix de KOFFI (masculine): Thomas (fr-FR)
```

### Exemple 2 : Windows avec Paul
```
Voix disponibles : Microsoft Paul, Microsoft Hortense
Sélection : Microsoft Paul (priorité 1 - nom masculin)
Console : 🎙️ Voix de KOFFI (masculine): Microsoft Paul (fr-FR)
```

### Exemple 3 : Chrome avec Google français
```
Voix disponibles : Google français, Google US English
Sélection : Google français (priorité 3 - première voix française)
Console : 🎙️ Voix de KOFFI (masculine): Google français (fr-FR)
```

### Exemple 4 : Système sans voix française
```
Voix disponibles : Google US English, Microsoft David
Sélection : Google US English (priorité 4 - voix par défaut)
Console : ⚠️ Aucune voix trouvée, utilisation de la voix par défaut
```

## 🎨 Personnalisation (Développeurs)

Si tu veux modifier les paramètres de la voix, édite `frontend/hooks/useTextToSpeech.ts` :

### Rendre la Voix Plus Grave
```typescript
utterance.pitch = 0.8;  // Plus grave (0.9 par défaut)
```

### Accélérer la Lecture
```typescript
utterance.rate = 1.2;  // Plus rapide (1.0 par défaut)
```

### Ralentir la Lecture
```typescript
utterance.rate = 0.8;  // Plus lent (1.0 par défaut)
```

### Ajouter des Noms Masculins
```typescript
voice.name.toLowerCase().includes('jean') ||
voice.name.toLowerCase().includes('marc')
```

### Ajouter des Noms Féminins à Exclure
```typescript
!voice.name.toLowerCase().includes('isabelle') &&
!voice.name.toLowerCase().includes('nathalie')
```

## 🚀 Amélioration de la Qualité Vocale

### Pour Windows
1. Installer des voix supplémentaires :
   - Paramètres → Heure et langue → Langue
   - Ajouter une langue → Français (France)
   - Options → Voix → Télécharger

### Pour macOS
1. Les voix sont déjà installées
2. Pour plus de voix :
   - Préférences Système → Accessibilité → Contenu énoncé
   - Voix système → Personnaliser

### Pour Linux
1. Installer espeak-ng :
   ```bash
   sudo apt install espeak-ng
   ```

2. Installer des voix supplémentaires :
   ```bash
   sudo apt install espeak-ng-data
   ```

## 📝 Notes Importantes

### Pourquoi Imposer une Voix Masculine ?

KOFFI est un agent masculin avec une personnalité définie. La voix fait partie de son identité et doit être cohérente avec son caractère.

### Que se Passe-t-il si Aucune Voix Masculine n'est Disponible ?

Le système sélectionne la meilleure voix française disponible, même si elle est féminine. C'est mieux qu'une voix anglaise ou pas de voix du tout.

### Peut-on Changer la Voix ?

Non, la voix est imposée automatiquement pour garantir une expérience cohérente. C'est la voix de KOFFI, pas une option utilisateur.

### La Voix est-elle la Même sur Tous les Systèmes ?

Non, elle dépend des voix installées sur le système. Mais l'algorithme garantit toujours la sélection de la meilleure voix masculine française disponible.

## 🎯 Résultat

- ✅ Voix masculine automatiquement sélectionnée
- ✅ Ton légèrement grave (pitch 0.9)
- ✅ Vitesse naturelle (rate 1.0)
- ✅ Volume maximum (volume 1.0)
- ✅ Langue française (fr-FR)
- ✅ Cohérence avec l'identité de KOFFI

---

KOFFI parle avec une voix masculine claire et naturelle ! 🎙️
