# 🎯 **Music Taxonomy Derivation Reference Guide**

## **📊 Fixed Taxonomy Framework (12 Categories)**

| **Taxonomy** | **Input Data Required** | **Derivation Formula/Process** | **Output** | **Example** |
|--------------|------------------------|-------------------------------|------------|-------------|
| **1. Energy Level** | `energy`, `tempo`, `loudness` | `(energy × 0.4) + (tempo/200 × 0.3) + (loudness+60)/60 × 0.3)` | 0-1 scale | 0.8 = "High Energy" |
| **2. Emotional Valence** | `valence`, `lyrical_sentiment` | `(valence × 0.6) + (lyrical_sentiment × 0.4)` | 0-1 scale | 0.2 = "Melancholic" |
| **3. Musical Complexity** | `time_signature`, `key_changes`, `tempo_variance` | `complexity = (time_sig≠4 ? 0.3 : 0) + key_changes×0.4 + tempo_variance×0.3` | 0-1 scale | 0.7 = "Complex" |
| **4. Intimacy Level** | `acousticness`, `liveness`, `loudness` | `intimacy = (acousticness × 0.5) + ((1-liveness) × 0.3) + ((1-loudness_norm) × 0.2)` | 0-1 scale | 0.9 = "Intimate" |
| **5. Danceability** | `danceability`, `tempo`, `beat_strength` | Direct from Spotify API + validation | 0-1 scale | 0.8 = "Dance" |
| **6. Focus Suitability** | `instrumentalness`, `speechiness`, `energy` | `focus = (instrumentalness × 0.4) + ((1-speechiness) × 0.3) + (energy_moderate × 0.3)` | 0-1 scale | 0.7 = "Focus" |
| **7. Nostalgia Factor** | `release_year`, `user_age`, `genre`, `lyrical_themes` | `nostalgia = age_gap_weight + genre_era_match + theme_memory_triggers` | 0-1 scale | 0.6 = "Nostalgic" |
| **8. Social Context** | `energy`, `valence`, `popularity`, `danceability` | `social = (energy×0.3) + (valence×0.3) + (popularity×0.2) + (danceability×0.2)` | 0-1 scale | 0.8 = "Party" |
| **9. Emotional Intensity** | `valence_extremity`, `energy`, `loudness`, `lyrical_intensity` | `intensity = abs(valence-0.5)×2 + energy×0.3 + loudness_norm×0.2 + lyrical_intensity×0.3` | 0-1 scale | 0.9 = "Intense" |
| **10. Time of Day** | `energy`, `tempo`, `acousticness`, `valence` | `if (energy<0.3 && acousticness>0.6): "Night"` <br> `elif (energy>0.7 && valence>0.6): "Morning"` <br> `else: "Any Time"` | Category | "Late Night" |
| **11. Activity Match** | `tempo`, `energy`, `motivational_lyrics`, `rhythm_stability` | Multi-conditional mapping based on tempo ranges and energy levels | Category | "Workout" |
| **12. Genre Fluidity** | `genre_primary`, `genre_secondary`, `cross_genre_elements` | `fluidity = (num_genres - 1) + cross_genre_score + innovation_index` | 0-1 scale | 0.6 = "Genre-Fluid" |

---

## **🔧 Implementation Details**

### **Normalization Functions:**
```javascript
// Core normalization utilities
function normalizeLoudness(loudness) {
    return (loudness + 60) / 60;  // Convert dB (-60 to 0) to 0-1 scale
}

function normalizeTempo(tempo) {
    return Math.min(tempo / 200, 1);  // Normalize BPM, cap at 200
}

function energyModerate(energy) {
    return 1 - Math.abs(energy - 0.5) * 2;  // Peaks at 0.5 energy level
}

function valenceExtremity(valence) {
    return Math.abs(valence - 0.5) * 2;  // Distance from neutral (0.5)
}
```

### **Core Taxonomy Calculations:**

#### **1. Energy Level**
```javascript
function calculateEnergyLevel(energy, tempo, loudness) {
    const normalizedTempo = normalizeTempo(tempo);
    const normalizedLoudness = normalizeLoudness(loudness);
    
    return (energy * 0.4) + (normalizedTempo * 0.3) + (normalizedLoudness * 0.3);
}
```

#### **2. Emotional Valence**
```javascript
function calculateEmotionalValence(valence, lyricalSentiment = null) {
    if (lyricalSentiment !== null) {
        return (valence * 0.6) + (lyricalSentiment * 0.4);
    }
    return valence;  // Fallback to Spotify valence only
}
```

#### **4. Intimacy Level**
```javascript
function calculateIntimacy(acousticness, liveness, loudness) {
    const normalizedLoudness = normalizeLoudness(loudness);
    const quietnessFactor = 1 - normalizedLoudness;
    const studioFactor = 1 - liveness;
    
    return (acousticness * 0.5) + (studioFactor * 0.3) + (quietnessFactor * 0.2);
}
```

#### **6. Focus Suitability**
```javascript
function calculateFocusSuitability(instrumentalness, speechiness, energy) {
    const moderateEnergy = energyModerate(energy);
    const lowSpeech = 1 - speechiness;
    
    return (instrumentalness * 0.4) + (lowSpeech * 0.3) + (moderateEnergy * 0.3);
}
```

#### **8. Social Context**
```javascript
function calculateSocialContext(energy, valence, popularity, danceability) {
    const normalizedPopularity = popularity / 100;  // Assuming 0-100 scale
    
    return (energy * 0.3) + (valence * 0.3) + (normalizedPopularity * 0.2) + (danceability * 0.2);
}
```

#### **9. Emotional Intensity**
```javascript
function calculateEmotionalIntensity(valence, energy, loudness, lyricalIntensity = 0.5) {
    const extremity = valenceExtremity(valence);
    const normalizedLoudness = normalizeLoudness(loudness);
    
    return (extremity * 0.4) + (energy * 0.3) + (normalizedLoudness * 0.2) + (lyricalIntensity * 0.1);
}
```

### **Conditional Logic Mappings:**

#### **10. Time of Day Categories**
```javascript
function determineTimeOfDay(energy, tempo, acousticness, valence) {
    // Late Night/3AM vibes
    if (energy < 0.3 && acousticness > 0.6 && valence < 0.4) {
        return "3AM Thoughts";
    }
    
    // Early Morning Energy
    if (energy > 0.7 && valence > 0.6 && tempo > 120) {
        return "Morning Motivation";
    }
    
    // Evening Party
    if (energy > 0.5 && danceability > 0.7) {
        return "Evening Party";
    }
    
    // Afternoon Chill
    if (energy >= 0.3 && energy <= 0.6 && valence > 0.4) {
        return "Afternoon Chill";
    }
    
    // Late Night Wind Down
    if (energy < 0.4 && acousticness > 0.5) {
        return "Wind Down";
    }
    
    return "Any Time";
}
```

#### **11. Activity Match Categories**
```javascript
function determineActivityMatch(tempo, energy, danceability, instrumentalness) {
    // High Intensity Workout
    if (tempo > 140 && energy > 0.8) {
        return "High Intensity Workout";
    }
    
    // Deep Focus/Study
    if (energy < 0.4 && instrumentalness > 0.5) {
        return "Deep Focus";
    }
    
    // Cooking/Kitchen
    if (energy >= 0.4 && energy <= 0.7 && valence > 0.5) {
        return "Cooking";
    }
    
    // Driving
    if (tempo >= 100 && tempo <= 140 && energy > 0.5) {
        return "Driving";
    }
    
    // Relaxing/Spa
    if (energy < 0.3 && acousticness > 0.7) {
        return "Relaxing";
    }
    
    // Dancing/Party
    if (danceability > 0.7 && energy > 0.6) {
        return "Dancing";
    }
    
    return "General Listening";
}
```

---

## **📈 Data Requirements & Sources**

### **✅ Available from Spotify API**
- `energy`, `valence`, `danceability`, `acousticness`
- `instrumentalness`, `liveness`, `speechiness`
- `tempo`, `loudness`, `key`, `mode`, `time_signature`
- `popularity`

### **🟡 Partially Available/Derivable**
- `lyrical_sentiment` - NLP analysis of lyrics
- `lyrical_intensity` - Keyword analysis + sentiment strength
- `rhythm_stability` - Tempo variance analysis
- `motivational_lyrics` - Keyword matching

### **🔄 Requires Additional Processing**
- `key_changes` - Musical analysis of progression
- `tempo_variance` - Statistical analysis of tempo changes
- `cross_genre_elements` - Genre classification confidence scores
- `genre_era_match` - Historical genre mapping

---

## **🎯 Implementation Priority**

### **Phase 1 - High Priority (Direct API)**
1. **Energy Level** - Simple calculation
2. **Emotional Valence** - Direct from API
3. **Danceability** - Direct from API
4. **Time of Day** - Conditional logic on API data

### **Phase 2 - Medium Priority (Moderate Processing)**
5. **Intimacy Level** - Weighted calculation
6. **Focus Suitability** - Weighted calculation  
7. **Social Context** - Multi-factor calculation
8. **Activity Match** - Enhanced conditional logic

### **Phase 3 - Low Priority (Complex Processing)**
9. **Musical Complexity** - Requires music theory analysis
10. **Nostalgia Factor** - Requires user data + historical mapping
11. **Emotional Intensity** - Requires lyrical analysis
12. **Genre Fluidity** - Requires advanced classification

---

## **📊 Output Categories & Thresholds**

### **Scaled Outputs (0-1)**
```javascript
const getScaleLabel = (value) => {
    if (value < 0.2) return "Very Low";
    if (value < 0.4) return "Low";
    if (value < 0.6) return "Medium";
    if (value < 0.8) return "High";
    return "Very High";
};
```

### **Category Mappings**
```javascript
const ENERGY_LABELS = {
    0.0-0.3: "Chill",
    0.3-0.6: "Moderate", 
    0.6-0.8: "Energetic",
    0.8-1.0: "High Energy"
};

const VALENCE_LABELS = {
    0.0-0.2: "Melancholic",
    0.2-0.4: "Reflective",
    0.4-0.6: "Neutral",
    0.6-0.8: "Uplifting",
    0.8-1.0: "Euphoric"
};
```

---

## **🔍 Example Implementation**

```javascript
// Complete song analysis
function analyzeSong(spotifyFeatures, additionalData = {}) {
    const analysis = {
        energyLevel: calculateEnergyLevel(
            spotifyFeatures.energy, 
            spotifyFeatures.tempo, 
            spotifyFeatures.loudness
        ),
        emotionalValence: calculateEmotionalValence(
            spotifyFeatures.valence,
            additionalData.lyricalSentiment
        ),
        intimacy: calculateIntimacy(
            spotifyFeatures.acousticness,
            spotifyFeatures.liveness,
            spotifyFeatures.loudness
        ),
        focus: calculateFocusSuitability(
            spotifyFeatures.instrumentalness,
            spotifyFeatures.speechiness,
            spotifyFeatures.energy
        ),
        timeOfDay: determineTimeOfDay(
            spotifyFeatures.energy,
            spotifyFeatures.tempo,
            spotifyFeatures.acousticness,
            spotifyFeatures.valence
        ),
        activity: determineActivityMatch(
            spotifyFeatures.tempo,
            spotifyFeatures.energy,
            spotifyFeatures.danceability,
            spotifyFeatures.instrumentalness
        )
    };
    
    return analysis;
}
```

---

## **🚀 Integration with Personalization System**

This taxonomy system can be combined with user preference data to create personalized insights:

```javascript
// Example: Generate personalized assessment
function generatePersonalizedAssessment(userSelections, taxonomyAnalysis) {
    const preferences = analyzeUserPreferences(userSelections);
    const insights = mapToPersonalityFrameworks(preferences);
    
    return {
        musicalDNA: preferences,
        personalityInsights: insights,
        recommendedSettings: generateContextualSettings(taxonomyAnalysis),
        explanation: generateUserFriendlyExplanation(insights)
    };
}
```

---

**Created:** 2025-01-27  
**Version:** 1.0  
**Last Updated:** 2025-01-27 