# 🗄️ **Database Schema Extensions for Song Entries**

## **📊 New Fields Required for Music Taxonomy System**

Based on our comprehensive taxonomy derivation framework, the following fields need to be added to each song's database entry:

---

## **🎵 Core Spotify API Fields (Direct Storage)**

These fields should be stored directly from Spotify's Audio Features API:

```sql
-- Core Audio Features (from Spotify API)
spotify_energy DECIMAL(4,3) NOT NULL,           -- 0.000-1.000
spotify_valence DECIMAL(4,3) NOT NULL,          -- 0.000-1.000  
spotify_danceability DECIMAL(4,3) NOT NULL,     -- 0.000-1.000
spotify_acousticness DECIMAL(4,3) NOT NULL,     -- 0.000-1.000
spotify_instrumentalness DECIMAL(4,3) NOT NULL, -- 0.000-1.000
spotify_liveness DECIMAL(4,3) NOT NULL,         -- 0.000-1.000
spotify_speechiness DECIMAL(4,3) NOT NULL,      -- 0.000-1.000
spotify_tempo DECIMAL(6,3) NOT NULL,            -- BPM (e.g., 120.123)
spotify_loudness DECIMAL(6,3) NOT NULL,         -- dB (-60.000 to 0.000)
spotify_key INTEGER,                            -- 0-11 (C, C#, D, etc.)
spotify_mode INTEGER,                           -- 0=minor, 1=major
spotify_time_signature INTEGER,                 -- 3-7 beats per bar
spotify_popularity INTEGER DEFAULT 0,           -- 0-100

-- Metadata
spotify_audio_features_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
```

---

## **🧮 Derived Taxonomy Fields (Calculated & Stored)**

These fields are calculated using our derivation formulas and stored for performance:

```sql
-- === PHASE 1: HIGH PRIORITY TAXONOMIES ===

-- 1. Energy Level (calculated from energy + tempo + loudness)
taxonomy_energy_level DECIMAL(4,3),             -- 0.000-1.000
taxonomy_energy_label VARCHAR(20),              -- "Chill", "Moderate", "Energetic", "High Energy"

-- 2. Emotional Valence (enhanced with lyrical analysis)
taxonomy_emotional_valence DECIMAL(4,3),        -- 0.000-1.000 (enhanced from spotify_valence)
taxonomy_emotional_label VARCHAR(20),           -- "Melancholic", "Reflective", "Neutral", "Uplifting", "Euphoric"

-- 3. Danceability (direct from API with validation)
taxonomy_danceability DECIMAL(4,3),             -- 0.000-1.000
taxonomy_dance_label VARCHAR(20),               -- "Not Danceable", "Slightly", "Moderate", "Very Danceable"

-- 4. Time of Day Context (categorical)
taxonomy_time_of_day VARCHAR(30),               -- "3AM Thoughts", "Morning Motivation", "Afternoon Chill", etc.
taxonomy_time_primary VARCHAR(15),              -- "Morning", "Afternoon", "Evening", "Night", "Any Time"

-- === PHASE 2: MEDIUM PRIORITY TAXONOMIES ===

-- 5. Intimacy Level (calculated from acousticness + liveness + loudness)
taxonomy_intimacy_level DECIMAL(4,3),           -- 0.000-1.000
taxonomy_intimacy_label VARCHAR(20),            -- "Public", "Social", "Personal", "Intimate", "Very Intimate"

-- 6. Focus Suitability (calculated from instrumentalness + speechiness + energy)
taxonomy_focus_suitability DECIMAL(4,3),        -- 0.000-1.000
taxonomy_focus_label VARCHAR(20),               -- "Distracting", "Background", "Suitable", "Ideal Focus"

-- 7. Social Context (calculated from energy + valence + popularity + danceability)
taxonomy_social_context DECIMAL(4,3),           -- 0.000-1.000
taxonomy_social_label VARCHAR(20),              -- "Solitary", "Small Group", "Party", "Large Gathering"

-- 8. Activity Match (categorical)
taxonomy_activity_match VARCHAR(30),            -- "High Intensity Workout", "Deep Focus", "Cooking", etc.
taxonomy_activity_category VARCHAR(15),         -- "Workout", "Study", "Social", "Relaxation", "General"

-- === PHASE 3: LOW PRIORITY TAXONOMIES ===

-- 9. Musical Complexity (requires advanced analysis)
taxonomy_musical_complexity DECIMAL(4,3),       -- 0.000-1.000
taxonomy_complexity_label VARCHAR(20),          -- "Simple", "Moderate", "Complex", "Very Complex"

-- 10. Nostalgia Factor (requires user data integration)
taxonomy_nostalgia_factor DECIMAL(4,3),         -- 0.000-1.000
taxonomy_nostalgia_era VARCHAR(20),             -- "2000s", "2010s", "90s", etc.

-- 11. Emotional Intensity (calculated from valence extremity + energy + loudness)
taxonomy_emotional_intensity DECIMAL(4,3),      -- 0.000-1.000
taxonomy_intensity_label VARCHAR(20),           -- "Subtle", "Moderate", "Intense", "Very Intense"

-- 12. Genre Fluidity (requires genre classification analysis)
taxonomy_genre_fluidity DECIMAL(4,3),           -- 0.000-1.000
taxonomy_genre_fluidity_label VARCHAR(20),      -- "Pure Genre", "Slightly Mixed", "Fusion", "Highly Fluid"
```

---

## **📝 Additional Supporting Fields**

Fields needed for enhanced analysis and user context:

```sql
-- === LYRICAL ANALYSIS (for enhanced calculations) ===
lyrical_sentiment DECIMAL(4,3),                 -- 0.000-1.000 (from NLP analysis)
lyrical_intensity DECIMAL(4,3),                 -- 0.000-1.000 (emotional strength)
lyrical_themes JSON,                            -- ["love", "heartbreak", "empowerment"] 
lyrical_complexity_score DECIMAL(4,3),          -- vocabulary sophistication
lyrical_narrative_complexity DECIMAL(4,3),      -- story structure complexity
lyrical_analysis_updated_at TIMESTAMP,

-- === MUSICAL ANALYSIS (for advanced calculations) ===
musical_key_changes_count INTEGER DEFAULT 0,    -- number of key changes
musical_tempo_variance DECIMAL(4,3),            -- tempo stability measure
musical_rhythm_stability DECIMAL(4,3),          -- beat consistency
musical_harmonic_complexity DECIMAL(4,3),       -- chord progression complexity
musical_analysis_updated_at TIMESTAMP,

-- === CONTEXTUAL METADATA ===
release_decade VARCHAR(10),                     -- "2020s", "2010s", etc.
genre_primary VARCHAR(50),                      -- main genre classification
genre_secondary VARCHAR(50),                    -- secondary genre (if applicable)
genre_confidence_score DECIMAL(4,3),            -- classification confidence
cross_genre_elements JSON,                      -- ["pop", "rock", "electronic"]

-- === CALCULATION METADATA ===
taxonomy_calculated_at TIMESTAMP,               -- when taxonomies were last calculated
taxonomy_version VARCHAR(10) DEFAULT 'v1.0',   -- calculation version for updates
calculation_confidence DECIMAL(4,3),            -- overall confidence in calculations
```

---

## **🔍 Indexes for Performance**

Recommended database indexes for efficient queries:

```sql
-- Performance indexes for taxonomy queries
CREATE INDEX idx_song_energy_level ON songs(taxonomy_energy_level);
CREATE INDEX idx_song_emotional_valence ON songs(taxonomy_emotional_valence);
CREATE INDEX idx_song_time_of_day ON songs(taxonomy_time_of_day);
CREATE INDEX idx_song_activity_match ON songs(taxonomy_activity_match);
CREATE INDEX idx_song_focus_suitability ON songs(taxonomy_focus_suitability);
CREATE INDEX idx_song_social_context ON songs(taxonomy_social_context);

-- Composite indexes for common query patterns
CREATE INDEX idx_song_energy_valence ON songs(taxonomy_energy_level, taxonomy_emotional_valence);
CREATE INDEX idx_song_time_activity ON songs(taxonomy_time_primary, taxonomy_activity_category);
CREATE INDEX idx_song_spotify_features ON songs(spotify_energy, spotify_valence, spotify_tempo);

-- Metadata indexes
CREATE INDEX idx_song_taxonomy_calculated ON songs(taxonomy_calculated_at);
CREATE INDEX idx_song_genre_primary ON songs(genre_primary);
```

---

## **📋 Data Population Strategy**

### **Phase 1: Immediate Implementation**
```sql
-- Fields to populate immediately from existing Spotify data
UPDATE songs SET 
    taxonomy_energy_level = calculate_energy_level(spotify_energy, spotify_tempo, spotify_loudness),
    taxonomy_emotional_valence = spotify_valence,
    taxonomy_danceability = spotify_danceability,
    taxonomy_time_of_day = determine_time_of_day(spotify_energy, spotify_tempo, spotify_acousticness, spotify_valence),
    taxonomy_calculated_at = CURRENT_TIMESTAMP
WHERE spotify_energy IS NOT NULL;
```

### **Phase 2: Enhanced Calculations**
```sql
-- Fields requiring moderate processing
UPDATE songs SET 
    taxonomy_intimacy_level = calculate_intimacy(spotify_acousticness, spotify_liveness, spotify_loudness),
    taxonomy_focus_suitability = calculate_focus(spotify_instrumentalness, spotify_speechiness, spotify_energy),
    taxonomy_social_context = calculate_social_context(spotify_energy, spotify_valence, spotify_popularity, spotify_danceability),
    taxonomy_activity_match = determine_activity_match(spotify_tempo, spotify_energy, spotify_danceability, spotify_instrumentalness)
WHERE taxonomy_energy_level IS NOT NULL;
```

### **Phase 3: Advanced Analysis**
```sql
-- Fields requiring external data or complex processing
-- These will be populated as additional analysis capabilities are added
UPDATE songs SET 
    lyrical_sentiment = analyze_lyrical_sentiment(lyrics),
    musical_complexity = analyze_musical_complexity(audio_features),
    taxonomy_nostalgia_factor = calculate_nostalgia(release_year, genre_primary, user_birth_year)
WHERE lyrics IS NOT NULL AND audio_analysis_complete = true;
```

---

## **🏷️ Enum Values & Constants**

Define consistent label values:

```sql
-- Energy Level Labels
ENUM('Chill', 'Moderate', 'Energetic', 'High Energy')

-- Emotional Labels  
ENUM('Melancholic', 'Reflective', 'Neutral', 'Uplifting', 'Euphoric')

-- Time of Day Labels
ENUM('3AM Thoughts', 'Morning Motivation', 'Afternoon Chill', 'Evening Party', 'Wind Down', 'Any Time')

-- Activity Labels
ENUM('High Intensity Workout', 'Deep Focus', 'Cooking', 'Driving', 'Relaxing', 'Dancing', 'General Listening')

-- Social Context Labels
ENUM('Solitary', 'Small Group', 'Party', 'Large Gathering')

-- Focus Labels
ENUM('Distracting', 'Background', 'Suitable', 'Ideal Focus')
```

---

## **🔄 Migration Script Template**

```sql
-- Add new columns to existing songs table
ALTER TABLE songs 
-- Phase 1 fields
ADD COLUMN taxonomy_energy_level DECIMAL(4,3),
ADD COLUMN taxonomy_energy_label VARCHAR(20),
ADD COLUMN taxonomy_emotional_valence DECIMAL(4,3),
ADD COLUMN taxonomy_emotional_label VARCHAR(20),
ADD COLUMN taxonomy_danceability DECIMAL(4,3),
ADD COLUMN taxonomy_dance_label VARCHAR(20),
ADD COLUMN taxonomy_time_of_day VARCHAR(30),
ADD COLUMN taxonomy_time_primary VARCHAR(15),

-- Phase 2 fields
ADD COLUMN taxonomy_intimacy_level DECIMAL(4,3),
ADD COLUMN taxonomy_intimacy_label VARCHAR(20),
ADD COLUMN taxonomy_focus_suitability DECIMAL(4,3),
ADD COLUMN taxonomy_focus_label VARCHAR(20),
ADD COLUMN taxonomy_social_context DECIMAL(4,3),
ADD COLUMN taxonomy_social_label VARCHAR(20),
ADD COLUMN taxonomy_activity_match VARCHAR(30),
ADD COLUMN taxonomy_activity_category VARCHAR(15),

-- Metadata fields
ADD COLUMN taxonomy_calculated_at TIMESTAMP,
ADD COLUMN taxonomy_version VARCHAR(10) DEFAULT 'v1.0',
ADD COLUMN lyrical_sentiment DECIMAL(4,3),
ADD COLUMN lyrical_analysis_updated_at TIMESTAMP;

-- Create indexes
CREATE INDEX idx_song_energy_level ON songs(taxonomy_energy_level);
CREATE INDEX idx_song_time_of_day ON songs(taxonomy_time_of_day);
CREATE INDEX idx_song_activity_match ON songs(taxonomy_activity_match);
```

---

## **📊 Example Record**

Sample song record with all new fields populated:

```json
{
  "song_id": "4iV5W9uYEdYUVa79Axb7Rh",
  "title": "cardigan",
  "artist": "Taylor Swift",
  
  // Existing Spotify API fields
  "spotify_energy": 0.345,
  "spotify_valence": 0.134,
  "spotify_danceability": 0.525,
  "spotify_acousticness": 0.852,
  "spotify_tempo": 130.87,
  "spotify_loudness": -8.54,
  
  // New taxonomy fields
  "taxonomy_energy_level": 0.423,
  "taxonomy_energy_label": "Moderate",
  "taxonomy_emotional_valence": 0.156,
  "taxonomy_emotional_label": "Melancholic",
  "taxonomy_time_of_day": "3AM Thoughts",
  "taxonomy_time_primary": "Night",
  "taxonomy_intimacy_level": 0.845,
  "taxonomy_intimacy_label": "Very Intimate",
  "taxonomy_focus_suitability": 0.623,
  "taxonomy_focus_label": "Suitable",
  "taxonomy_activity_match": "Quiet Reflection",
  "taxonomy_activity_category": "Relaxation",
  
  // Analysis metadata
  "taxonomy_calculated_at": "2025-01-27T10:30:00Z",
  "taxonomy_version": "v1.0",
  "lyrical_sentiment": 0.234,
  "lyrical_themes": ["nostalgia", "lost_love", "memory"]
}
```

---

## **🚀 Implementation Checklist**

- [ ] **Phase 1**: Add core taxonomy fields (energy, valence, time, danceability)
- [ ] **Phase 1**: Create calculation functions for immediate fields
- [ ] **Phase 1**: Populate existing songs with Phase 1 calculations
- [ ] **Phase 1**: Create basic indexes for performance
- [ ] **Phase 2**: Add enhanced taxonomy fields (intimacy, focus, social, activity)
- [ ] **Phase 2**: Implement Phase 2 calculation functions
- [ ] **Phase 2**: Populate Phase 2 fields for existing songs
- [ ] **Phase 3**: Add lyrical analysis capability
- [ ] **Phase 3**: Add musical complexity analysis
- [ ] **Phase 3**: Implement remaining advanced taxonomies
- [ ] **Testing**: Validate calculation accuracy with sample data
- [ ] **Performance**: Monitor query performance and optimize indexes

---

**Created:** 2025-01-27  
**Version:** 1.0  
**Purpose:** Database schema extensions for music taxonomy system 