import os
import time
import math
from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional

# Load environment variables
load_dotenv('../../../.env.development')

class Phase1TaxonomyCalculator:
    def __init__(self):
        # Database connection
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME') 
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not all([self.neo4j_uri, self.neo4j_password]):
            raise ValueError("Missing required environment variables for AuraDB connection")
        
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        # Taxonomy calculation metadata
        self.taxonomy_version = "v1.0"
        self.calculation_timestamp = int(time.time())
        
        print("🎯 Phase 1 Taxonomy Calculator initialized")
        print(f"📊 Taxonomy Version: {self.taxonomy_version}")

    # ========== NORMALIZATION UTILITIES ==========
    
    def normalize_loudness(self, loudness: float) -> float:
        """Convert dB (-60 to 0) to 0-1 scale"""
        return max(0, min(1, (loudness + 60) / 60))
    
    def normalize_tempo(self, tempo: float) -> float:
        """Normalize BPM, cap at 200"""
        return min(tempo / 200, 1)
    
    def energy_moderate(self, energy: float) -> float:
        """Peaks at 0.5 energy level (moderate energy preferred)"""
        return 1 - abs(energy - 0.5) * 2
    
    def valence_extremity(self, valence: float) -> float:
        """Distance from neutral (0.5)"""
        return abs(valence - 0.5) * 2
    
    def normalize_popularity(self, popularity: Optional[int]) -> float:
        """Convert 0-100 to 0-1 scale"""
        return (popularity or 0) / 100
    
    # ========== CORE TAXONOMY CALCULATIONS ==========
    
    def calculate_energy_level(self, energy: float, tempo: float, loudness: float) -> Tuple[float, str]:
        """1. Energy Level calculation"""
        normalized_tempo = self.normalize_tempo(tempo)
        normalized_loudness = self.normalize_loudness(loudness)
        
        score = (energy * 0.4) + (normalized_tempo * 0.3) + (normalized_loudness * 0.3)
        
        # Determine label
        if score < 0.25:
            label = "Chill"
        elif score < 0.5:
            label = "Moderate"
        elif score < 0.75:
            label = "Energetic"
        else:
            label = "High Energy"
        
        return round(score, 3), label
    
    def calculate_emotional_valence(self, valence: float, lyrical_sentiment: Optional[float] = None) -> Tuple[float, str]:
        """2. Emotional Valence calculation"""
        if lyrical_sentiment is not None:
            score = (valence * 0.6) + (lyrical_sentiment * 0.4)
        else:
            score = valence  # Fallback to Spotify valence only
        
        # Determine label
        if score < 0.2:
            label = "Melancholic"
        elif score < 0.4:
            label = "Reflective"
        elif score < 0.6:
            label = "Neutral"
        elif score < 0.8:
            label = "Uplifting"
        else:
            label = "Euphoric"
        
        return round(score, 3), label
    
    def calculate_musical_complexity(self, time_signature: int, key_changes: int = 0, tempo_variance: float = 0.1) -> Tuple[float, str]:
        """3. Musical Complexity calculation"""
        time_sig_factor = 0.3 if time_signature != 4 else 0
        key_change_factor = min(key_changes * 0.4, 0.4)  # Cap contribution
        tempo_variance_factor = min(tempo_variance * 0.3, 0.3)  # Cap contribution
        
        score = time_sig_factor + key_change_factor + tempo_variance_factor
        
        # Determine label
        if score < 0.25:
            label = "Simple"
        elif score < 0.5:
            label = "Moderate"
        elif score < 0.75:
            label = "Complex"
        else:
            label = "Very Complex"
        
        return round(score, 3), label
    
    def calculate_intimacy_level(self, acousticness: float, liveness: float, loudness: float) -> Tuple[float, str]:
        """4. Intimacy Level calculation"""
        normalized_loudness = self.normalize_loudness(loudness)
        quietness_factor = 1 - normalized_loudness
        studio_factor = 1 - liveness
        
        score = (acousticness * 0.5) + (studio_factor * 0.3) + (quietness_factor * 0.2)
        
        # Determine label
        if score < 0.2:
            label = "Public"
        elif score < 0.4:
            label = "Social"
        elif score < 0.6:
            label = "Personal"
        elif score < 0.8:
            label = "Intimate"
        else:
            label = "Very Intimate"
        
        return round(score, 3), label
    
    def calculate_focus_suitability(self, instrumentalness: float, speechiness: float, energy: float) -> Tuple[float, str]:
        """6. Focus Suitability calculation"""
        moderate_energy = self.energy_moderate(energy)
        low_speech = 1 - speechiness
        
        score = (instrumentalness * 0.4) + (low_speech * 0.3) + (moderate_energy * 0.3)
        
        # Determine label
        if score < 0.3:
            label = "Distracting"
        elif score < 0.5:
            label = "Background"
        elif score < 0.7:
            label = "Suitable"
        else:
            label = "Ideal Focus"
        
        return round(score, 3), label
    
    def calculate_social_context(self, energy: float, valence: float, popularity: int, danceability: float) -> Tuple[float, str]:
        """8. Social Context calculation"""
        normalized_popularity = self.normalize_popularity(popularity)
        
        score = (energy * 0.3) + (valence * 0.3) + (normalized_popularity * 0.2) + (danceability * 0.2)
        
        # Determine label
        if score < 0.3:
            label = "Solitary"
        elif score < 0.5:
            label = "Small Group"
        elif score < 0.7:
            label = "Party"
        else:
            label = "Large Gathering"
        
        return round(score, 3), label
    
    def calculate_emotional_intensity(self, valence: float, energy: float, loudness: float, lyrical_intensity: float = 0.5) -> Tuple[float, str]:
        """9. Emotional Intensity calculation"""
        extremity = self.valence_extremity(valence)
        normalized_loudness = self.normalize_loudness(loudness)
        
        score = (extremity * 0.4) + (energy * 0.3) + (normalized_loudness * 0.2) + (lyrical_intensity * 0.1)
        
        # Determine label
        if score < 0.3:
            label = "Subtle"
        elif score < 0.5:
            label = "Moderate"
        elif score < 0.7:
            label = "Intense"
        else:
            label = "Very Intense"
        
        return round(score, 3), label
    
    def determine_time_of_day(self, energy: float, tempo: float, acousticness: float, valence: float, danceability: float) -> Tuple[str, str]:
        """10. Time of Day categorical determination"""
        # Late Night/3AM vibes
        if energy < 0.3 and acousticness > 0.6 and valence < 0.4:
            return "3AM Thoughts", "Night"
        
        # Early Morning Energy
        if energy > 0.7 and valence > 0.6 and tempo > 120:
            return "Morning Motivation", "Morning"
        
        # Evening Party
        if energy > 0.5 and danceability > 0.7:
            return "Evening Party", "Evening"
        
        # Afternoon Chill
        if 0.3 <= energy <= 0.6 and valence > 0.4:
            return "Afternoon Chill", "Afternoon"
        
        # Late Night Wind Down
        if energy < 0.4 and acousticness > 0.5:
            return "Wind Down", "Night"
        
        return "Any Time", "Any Time"
    
    def determine_activity_match(self, tempo: float, energy: float, danceability: float, instrumentalness: float, valence: float, acousticness: float) -> Tuple[str, str]:
        """11. Activity Match categorical determination"""
        # High Intensity Workout
        if tempo > 140 and energy > 0.8:
            return "High Intensity Workout", "Workout"
        
        # Moderate Workout
        if 110 <= tempo <= 140 and energy > 0.6:
            return "Moderate Workout", "Workout"
        
        # Deep Focus/Study
        if energy < 0.4 and instrumentalness > 0.5:
            return "Deep Focus", "Study"
        
        # Light Study/Background
        if energy < 0.6 and instrumentalness > 0.3:
            return "Light Study", "Study"
        
        # Relaxing/Spa
        if energy < 0.3 and acousticness > 0.7:
            return "Relaxing", "Relaxation"
        
        # Dancing/Party
        if danceability > 0.7 and energy > 0.6:
            return "Dancing", "Social"
        
        # Driving
        if 100 <= tempo <= 140 and energy > 0.5:
            return "Driving", "General"
        
        return "General Listening", "General"
    
    # ========== BATCH PROCESSING ==========
    
    def fetch_songs_with_audio_features(self) -> List[Dict]:
        """Fetch all songs with complete audio features for processing"""
        query = """
        MATCH (s:Song)
        WHERE s.energy IS NOT NULL 
        AND s.valence IS NOT NULL
        AND s.danceability IS NOT NULL
        AND s.tempo IS NOT NULL
        AND s.loudness IS NOT NULL
        RETURN s.id as song_id,
               s.title as title,
               s.albumCode as album_code,
               s.energy as energy,
               s.valence as valence,
               s.danceability as danceability,
               s.acousticness as acousticness,
               s.instrumentalness as instrumentalness,
               s.liveness as liveness,
               s.speechiness as speechiness,
               s.tempo as tempo,
               s.loudness as loudness,
               s.key as key,
               s.mode as mode,
               s.time_signature as time_signature
        ORDER BY s.albumCode, s.title
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            songs = [dict(record) for record in result]
        
        print(f"📊 Retrieved {len(songs)} songs with complete audio features")
        return songs
    
    def calculate_taxonomies_for_song(self, song: Dict) -> Dict:
        """Calculate all 12 taxonomies for a single song"""
        taxonomies = {}
        
        # Extract audio features
        energy = song['energy']
        valence = song['valence']
        danceability = song['danceability']
        acousticness = song['acousticness']
        instrumentalness = song['instrumentalness']
        liveness = song['liveness']
        speechiness = song['speechiness']
        tempo = song['tempo']
        loudness = song['loudness']
        time_signature = song.get('time_signature', 4)
        
        # Calculate core taxonomies
        taxonomies['energy_level'], taxonomies['energy_label'] = self.calculate_energy_level(energy, tempo, loudness)
        taxonomies['emotional_valence'], taxonomies['emotional_label'] = self.calculate_emotional_valence(valence)
        taxonomies['musical_complexity'], taxonomies['complexity_label'] = self.calculate_musical_complexity(time_signature)
        taxonomies['intimacy_level'], taxonomies['intimacy_label'] = self.calculate_intimacy_level(acousticness, liveness, loudness)
        taxonomies['danceability_enhanced'] = danceability  # Simplified for Phase 1
        taxonomies['dance_label'] = "Danceable" if danceability > 0.5 else "Not Danceable"
        taxonomies['focus_suitability'], taxonomies['focus_label'] = self.calculate_focus_suitability(instrumentalness, speechiness, energy)
        taxonomies['nostalgia_factor'] = 0.4  # Simplified default for Phase 1
        taxonomies['nostalgia_label'] = "Recent"
        taxonomies['social_context'], taxonomies['social_label'] = self.calculate_social_context(energy, valence, 50, danceability)
        taxonomies['emotional_intensity'], taxonomies['intensity_label'] = self.calculate_emotional_intensity(valence, energy, loudness)
        taxonomies['time_of_day'], taxonomies['time_primary'] = self.determine_time_of_day(energy, tempo, acousticness, valence, danceability)
        taxonomies['activity_match'], taxonomies['activity_category'] = self.determine_activity_match(tempo, energy, danceability, instrumentalness, valence, acousticness)
        taxonomies['genre_fluidity'] = 0.2  # Simplified default
        taxonomies['fluidity_label'] = "Pure Genre"
        
        return taxonomies
    
    def update_song_taxonomies_batch(self, song_taxonomies: List[Tuple[str, Dict]]) -> int:
        """Batch update songs with calculated taxonomies using AuraDB optimization"""
        
        batch_query = """
        UNWIND $song_data as song_update
        MATCH (s:Song {id: song_update.song_id})
        SET s.taxonomy_energy_level = song_update.energy_level,
            s.taxonomy_energy_label = song_update.energy_label,
            s.taxonomy_emotional_valence = song_update.emotional_valence,
            s.taxonomy_emotional_label = song_update.emotional_label,
            s.taxonomy_musical_complexity = song_update.musical_complexity,
            s.taxonomy_complexity_label = song_update.complexity_label,
            s.taxonomy_intimacy_level = song_update.intimacy_level,
            s.taxonomy_intimacy_label = song_update.intimacy_label,
            s.taxonomy_danceability = song_update.danceability_enhanced,
            s.taxonomy_dance_label = song_update.dance_label,
            s.taxonomy_focus_suitability = song_update.focus_suitability,
            s.taxonomy_focus_label = song_update.focus_label,
            s.taxonomy_nostalgia_factor = song_update.nostalgia_factor,
            s.taxonomy_nostalgia_label = song_update.nostalgia_label,
            s.taxonomy_social_context = song_update.social_context,
            s.taxonomy_social_label = song_update.social_label,
            s.taxonomy_emotional_intensity = song_update.emotional_intensity,
            s.taxonomy_intensity_label = song_update.intensity_label,
            s.taxonomy_time_of_day = song_update.time_of_day,
            s.taxonomy_time_primary = song_update.time_primary,
            s.taxonomy_activity_match = song_update.activity_match,
            s.taxonomy_activity_category = song_update.activity_category,
            s.taxonomy_genre_fluidity = song_update.genre_fluidity,
            s.taxonomy_fluidity_label = song_update.fluidity_label,
            s.taxonomy_calculated_at = song_update.calculated_at,
            s.taxonomy_version = song_update.version,
            s.calculation_confidence = song_update.confidence
        RETURN count(s) as updated_count
        """
        
        # Prepare batch data
        batch_data = []
        for song_id, taxonomies in song_taxonomies:
            song_data = {
                'song_id': song_id,
                'calculated_at': self.calculation_timestamp,
                'version': self.taxonomy_version,
                'confidence': 0.85,  # Default confidence for Phase 1
                **taxonomies
            }
            batch_data.append(song_data)
        
        # Execute batch update
        with self.driver.session() as session:
            result = session.run(batch_query, {'song_data': batch_data})
            updated_count = result.single()['updated_count']
        
        return updated_count
    
    def process_all_songs(self, batch_size: int = 25) -> Dict:
        """Process all songs in batches for optimal performance"""
        print("🚀 Starting Phase 1: Music Taxonomy Calculation")
        print("=" * 70)
        
        start_time = time.time()
        
        # Fetch songs
        songs = self.fetch_songs_with_audio_features()
        total_songs = len(songs)
        
        if total_songs == 0:
            print("❌ No songs with audio features found!")
            return {'success': False, 'total_songs': 0}
        
        # Process in batches
        processed_count = 0
        batch_count = 0
        
        for i in range(0, total_songs, batch_size):
            batch_count += 1
            batch_songs = songs[i:i + batch_size]
            current_batch_size = len(batch_songs)
            
            print(f"\n📦 Processing batch {batch_count} ({current_batch_size} songs)")
            
            # Calculate taxonomies for this batch
            song_taxonomies = []
            for song in batch_songs:
                taxonomies = self.calculate_taxonomies_for_song(song)
                song_taxonomies.append((song['song_id'], taxonomies))
            
            # Batch update to database
            updated_count = self.update_song_taxonomies_batch(song_taxonomies)
            processed_count += updated_count
            
            print(f"  ✅ Updated {updated_count}/{current_batch_size} songs")
            
            # Progress update
            progress = (processed_count / total_songs) * 100
            print(f"  📊 Overall progress: {processed_count}/{total_songs} ({progress:.1f}%)")
        
        # Final validation
        execution_time = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("📊 Phase 1 Taxonomy Calculation Complete!")
        print(f"  ✅ Successfully processed: {processed_count}/{total_songs} songs")
        print(f"  ⏱️ Execution time: {execution_time:.2f} seconds")
        print(f"  📈 Processing rate: {processed_count/execution_time:.1f} songs/second")
        
        return {
            'success': True,
            'total_songs': total_songs,
            'processed_songs': processed_count,
            'execution_time': execution_time,
            'taxonomy_version': self.taxonomy_version
        }
    
    def validate_taxonomy_results(self) -> Dict:
        """Validate the taxonomy calculation results"""
        validation_query = """
        MATCH (s:Song)
        WHERE s.taxonomy_energy_level IS NOT NULL
        RETURN count(s) as songs_with_taxonomies,
               avg(s.taxonomy_energy_level) as avg_energy,
               avg(s.taxonomy_emotional_valence) as avg_valence,
               avg(s.taxonomy_danceability) as avg_danceability,
               collect(DISTINCT s.taxonomy_energy_label) as energy_labels,
               collect(DISTINCT s.taxonomy_time_primary) as time_categories,
               collect(DISTINCT s.taxonomy_activity_category) as activity_categories
        """
        
        with self.driver.session() as session:
            result = session.run(validation_query)
            validation_data = result.single()
        
        print("\n🔍 Taxonomy Validation Results:")
        print(f"  📊 Songs with taxonomies: {validation_data['songs_with_taxonomies']}")
        print(f"  ⚡ Average energy level: {validation_data['avg_energy']:.3f}")
        print(f"  😊 Average emotional valence: {validation_data['avg_valence']:.3f}")
        print(f"  💃 Average danceability: {validation_data['avg_danceability']:.3f}")
        print(f"  🏷️ Energy labels: {sorted(validation_data['energy_labels'])}")
        print(f"  🕐 Time categories: {sorted(validation_data['time_categories'])}")
        print(f"  🎯 Activity categories: {sorted(validation_data['activity_categories'])}")
        
        return dict(validation_data)
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()

def main():
    calculator = Phase1TaxonomyCalculator()
    
    try:
        # Process all songs with taxonomy calculations
        results = calculator.process_all_songs(batch_size=25)  # Optimized batch size
        
        if results['success']:
            # Validate results
            validation = calculator.validate_taxonomy_results()
            
            print(f"\n🎉 Phase 1 Complete!")
            print(f"📈 All {results['processed_songs']} songs now have complete music taxonomies")
            print(f"🚀 Ready for Phase 2: Enhanced Analysis & Optimization")
        else:
            print("❌ Phase 1 failed - check error messages above")
    
    finally:
        calculator.close()

if __name__ == "__main__":
    main() 