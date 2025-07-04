#!/usr/bin/env python3
"""
Unified Word Identifier & Music Taxonomy Implementation
Merges word optimization, production implementation, and comprehensive taxonomy
"""

from neo4j import GraphDatabase
import hashlib
import time
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedWordTaxonomySystem:
    """
    Unified implementation combining:
    - Word identifier optimization (concept.md)
    - Production-ready implementation (README.md) 
    - Comprehensive music taxonomy (additional_fields.md)
    """
    
    def __init__(self, uri: str = None, username: str = None, password: str = None):
        # Use .env credentials if not provided
        if uri is None:
            uri = os.getenv("AURA_DB_URI")
        if username is None:
            username = os.getenv("AURA_DB_USERNAME", "neo4j")
        if password is None:
            password = os.getenv("AURA_DB_PASSWORD")
            
        # AuraDB-optimized connection (from README)
        self.driver = GraphDatabase.driver(
            uri, 
            auth=(username, password),
            max_connection_pool_size=100,
            connection_timeout=60,
            max_retry_time=30
        )
        
        # Performance tracking
        self.stats = {
            'words_created': 0,
            'songs_converted': 0,
            'taxonomies_calculated': 0,
            'start_time': time.time()
        }
    
    # ======= PHASE 1: WORD IDENTIFIER SYSTEM =======
    
    def generate_word_id(self, word_text: str) -> str:
        """Generate consistent unique ID for word (from README)"""
        return f"word_{hashlib.md5(word_text.lower().encode()).hexdigest()[:8]}"
    
    def phase1_create_word_registry(self) -> int:
        """Phase 1: Create unified word dictionary with enhanced metadata"""
        logger.info("🔄 Phase 1: Creating unified word registry...")
        
        with self.driver.session() as session:
            result = session.execute_write(self._bulk_extract_words_enhanced)
            self.stats['words_created'] = result
            logger.info(f"✅ Created {result} unique word entries")
            return result
    
    @staticmethod
    def _bulk_extract_words_enhanced(tx):
        """Enhanced word extraction with taxonomy preparation"""
        query = """
        MATCH (s:Song)-[r:HAS_WORD]->(w:Word)
        WITH DISTINCT w.text as word_text, 
             sum(r.count) as total_frequency,
             count(DISTINCT s) as song_count,
             collect(DISTINCT s.albumCode) as albums
        
        // Create enhanced word registry
        UNWIND collect({
            text: word_text, 
            freq: total_frequency,
            song_count: song_count,
            albums: albums
        }) as word_data
        
        MERGE (wd:WordDictionary {
            id: 'word_' + substring(apoc.util.md5([word_data.text]), 0, 8),
            text: word_data.text,
            frequency: word_data.freq,
            song_usage_count: word_data.song_count,
            album_spread: size(word_data.albums),
            created_at: datetime(),
            system_version: 'unified_v1.0'
        })
        
        RETURN count(wd) as words_created
        """
        
        result = tx.run(query)
        return result.single()["words_created"]
    
    def phase1_convert_song_sequences(self) -> int:
        """Phase 1: Convert songs to word ID sequences with validation"""
        logger.info("🔄 Phase 1: Converting songs to word sequences...")
        
        with self.driver.session() as session:
            batch_size = 50  # Optimized batch size from README
            total_songs = session.run("MATCH (s:Song) RETURN count(s) as total").single()["total"]
            
            songs_converted = 0
            for offset in range(0, total_songs, batch_size):
                batch_result = session.execute_write(
                    self._convert_song_batch_enhanced, offset, batch_size
                )
                songs_converted += batch_result
                logger.info(f"📊 Processed {min(offset + batch_size, total_songs)}/{total_songs} songs")
            
            self.stats['songs_converted'] = songs_converted
            return songs_converted
    
    @staticmethod
    def _convert_song_batch_enhanced(tx, offset: int, batch_size: int):
        """Enhanced song conversion with metadata tracking"""
        query = """
        // Get songs with their lyrics in order
        MATCH (s:Song)-[:HAS_LYRIC]->(l:Lyric)
        WITH s, l ORDER BY s.title, l.lineNumber
        SKIP $offset LIMIT $batch_size
        
        // Get words for each lyric line with position tracking
        MATCH (l)-[:CONTAINS_WORD]->(w:Word)
        WITH s, l, collect(w.text) as line_words
        ORDER BY l.lineNumber
        
        // Convert to word IDs and calculate metadata
        WITH s, l, [word IN line_words | 
            'word_' + substring(apoc.util.md5([word]), 0, 8)
        ] as word_ids
        
        SET l.word_sequence = word_ids,
            l.conversion_timestamp = datetime(),
            l.word_count = size(word_ids),
            l.unique_word_count = size(apoc.coll.toSet(word_ids))
        
        // Update song-level word statistics
        WITH s, collect(l.word_count) as line_word_counts,
             collect(l.word_sequence) as all_sequences
        
        WITH s, line_word_counts,
             apoc.coll.flatten(all_sequences) as all_word_ids
        
        SET s.total_word_count = apoc.coll.sum(line_word_counts),
            s.unique_word_count = size(apoc.coll.toSet(all_word_ids)),
            s.vocabulary_complexity = toFloat(size(apoc.coll.toSet(all_word_ids))) / apoc.coll.sum(line_word_counts),
            s.word_conversion_completed = datetime()
        
        RETURN count(DISTINCT s) as songs_converted
        """
        
        result = tx.run(query, offset=offset, batch_size=batch_size)
        return result.single()["songs_converted"]
    
    # ======= PHASE 2: MUSIC TAXONOMY INTEGRATION =======
    
    def phase2_calculate_comprehensive_taxonomies(self) -> int:
        """Phase 2: Calculate all music taxonomies from additional_fields.md"""
        logger.info("🔄 Phase 2: Calculating comprehensive music taxonomies...")
        
        with self.driver.session() as session:
            # Get all songs with required Spotify features
            songs_query = """
            MATCH (s:Song) 
            WHERE s.energy IS NOT NULL AND s.valence IS NOT NULL
            RETURN s.title as title,
                   s.albumCode as albumCode,
                   ID(s) as nodeId,
                   s.energy as energy,
                   s.valence as valence,
                   s.danceability as danceability,
                   s.acousticness as acousticness,
                   s.instrumentalness as instrumentalness,
                   s.liveness as liveness,
                   s.speechiness as speechiness,
                   s.tempo as tempo,
                   s.loudness as loudness,
                   s.spotify_key as key,
                   s.spotify_mode as mode,
                   s.time_signature as time_signature,
                   s.unique_word_count as unique_word_count,
                   s.total_word_count as total_word_count,
                   s.vocabulary_complexity as vocabulary_complexity
            """
            
            songs = list(session.run(songs_query))
            logger.info(f"📊 Found {len(songs)} songs with complete data")
            
            # Calculate taxonomies for each song
            taxonomy_updates = []
            for song in songs:
                taxonomies = self._calculate_unified_taxonomies(dict(song))
                taxonomy_updates.append((song['nodeId'], taxonomies))
            
            # Batch update all taxonomies
            updated_count = session.execute_write(
                self._batch_update_taxonomies, taxonomy_updates
            )
            
            self.stats['taxonomies_calculated'] = updated_count
            logger.info(f"✅ Updated taxonomies for {updated_count} songs")
            return updated_count
    
    def _calculate_unified_taxonomies(self, song: Dict) -> Dict:
        """Calculate all taxonomies using formulas from additional_fields.md"""
        taxonomies = {}
        
        # Extract features
        energy = song.get('energy', 0.0)
        valence = song.get('valence', 0.0)
        danceability = song.get('danceability', 0.0)
        acousticness = song.get('acousticness', 0.0)
        instrumentalness = song.get('instrumentalness', 0.0)
        speechiness = song.get('speechiness', 0.0)
        tempo = song.get('tempo', 120.0)
        loudness = song.get('loudness', -10.0)
        
        # Word-based complexity (enhanced with word data)
        vocab_complexity = song.get('vocabulary_complexity', 0.5)
        unique_words = song.get('unique_word_count', 50)
        total_words = song.get('total_word_count', 150)
        
        # === PHASE 1 TAXONOMIES (High Priority) ===
        
        # 1. Energy Level (enhanced with word data)
        energy_component = energy * 0.4
        tempo_component = min(tempo / 200.0, 1.0) * 0.3
        loudness_component = min((loudness + 60) / 60.0, 1.0) * 0.2
        word_energy_component = vocab_complexity * 0.1  # Complex words = higher energy
        
        taxonomies['energy_level'] = min(energy_component + tempo_component + loudness_component + word_energy_component, 1.0)
        taxonomies['energy_label'] = self._get_energy_label(taxonomies['energy_level'])
        
        # 2. Emotional Valence (enhanced with lyrical context)
        base_valence = valence * 0.8
        lyrical_enhancement = (1.0 - vocab_complexity) * 0.2  # Simpler words = more direct emotion
        
        taxonomies['emotional_valence'] = min(base_valence + lyrical_enhancement, 1.0)
        taxonomies['emotional_label'] = self._get_emotional_label(taxonomies['emotional_valence'])
        
        # 3. Musical Complexity (combining audio + lyrical)
        audio_complexity = (1 - acousticness) * 0.4 + instrumentalness * 0.3 + (1 - danceability) * 0.3
        lyrical_complexity = vocab_complexity
        
        taxonomies['musical_complexity'] = (audio_complexity * 0.6) + (lyrical_complexity * 0.4)
        taxonomies['complexity_label'] = self._get_complexity_label(taxonomies['musical_complexity'])
        
        # 4. Intimacy Level
        intimacy_score = acousticness * 0.4 + (1 - (loudness + 60) / 60.0) * 0.3 + (1 - energy) * 0.3
        taxonomies['intimacy_level'] = max(min(intimacy_score, 1.0), 0.0)
        taxonomies['intimacy_label'] = self._get_intimacy_label(taxonomies['intimacy_level'])
        
        # 5. Focus Suitability (enhanced with word analysis)
        instrumental_component = instrumentalness * 0.4
        speech_component = (1 - speechiness) * 0.3
        energy_component = (1 - energy) * 0.2
        word_component = (1 - vocab_complexity) * 0.1  # Simpler words = better focus
        
        taxonomies['focus_suitability'] = min(instrumental_component + speech_component + energy_component + word_component, 1.0)
        taxonomies['focus_label'] = self._get_focus_label(taxonomies['focus_suitability'])
        
        # 6. Time of Day & Activity Match
        taxonomies['time_of_day'], taxonomies['time_primary'] = self._determine_time_of_day(
            energy, tempo, acousticness, valence, danceability
        )
        taxonomies['activity_match'], taxonomies['activity_category'] = self._determine_activity_match(
            tempo, energy, danceability, instrumentalness, valence, acousticness
        )
        
        # Add calculation metadata
        taxonomies['calculated_at'] = datetime.now().isoformat()
        taxonomies['taxonomy_version'] = 'unified_v1.0'
        taxonomies['calculation_confidence'] = 0.85  # High confidence with word enhancement
        
        return taxonomies
    
    @staticmethod
    def _batch_update_taxonomies(tx, taxonomy_updates: List[Tuple[int, Dict]]):
        """Batch update all calculated taxonomies"""
        
        # Prepare batch data
        batch_data = []
        for node_id, taxonomies in taxonomy_updates:
            batch_data.append({
                'nodeId': node_id,
                **taxonomies
            })
        
        query = """
        UNWIND $batch_data as song_update
        MATCH (s:Song) WHERE ID(s) = song_update.nodeId
        SET s.taxonomy_energy_level = song_update.energy_level,
            s.taxonomy_energy_label = song_update.energy_label,
            s.taxonomy_emotional_valence = song_update.emotional_valence,
            s.taxonomy_emotional_label = song_update.emotional_label,
            s.taxonomy_musical_complexity = song_update.musical_complexity,
            s.taxonomy_complexity_label = song_update.complexity_label,
            s.taxonomy_intimacy_level = song_update.intimacy_level,
            s.taxonomy_intimacy_label = song_update.intimacy_label,
            s.taxonomy_focus_suitability = song_update.focus_suitability,
            s.taxonomy_focus_label = song_update.focus_label,
            s.taxonomy_time_of_day = song_update.time_of_day,
            s.taxonomy_time_primary = song_update.time_primary,
            s.taxonomy_activity_match = song_update.activity_match,
            s.taxonomy_activity_category = song_update.activity_category,
            s.taxonomy_calculated_at = song_update.calculated_at,
            s.taxonomy_version = song_update.taxonomy_version,
            s.calculation_confidence = song_update.calculation_confidence
        RETURN count(s) as updated_count
        """
        
        result = tx.run(query, batch_data=batch_data)
        return result.single()["updated_count"]
    
    # ======= PHASE 3: PERFORMANCE OPTIMIZATION =======
    
    def phase3_create_unified_indexes(self):
        """Phase 3: Create optimized indexes for word IDs + taxonomies"""
        logger.info("🔄 Phase 3: Creating unified performance indexes...")
        
        indexes = [
            # Word system indexes (from concept.md)
            "CREATE INDEX word_id_index IF NOT EXISTS FOR (w:WordDictionary) ON (w.id)",
            "CREATE INDEX word_text_index IF NOT EXISTS FOR (w:WordDictionary) ON (w.text)",
            "CREATE INDEX lyric_sequence_index IF NOT EXISTS FOR (l:Lyric) ON (l.word_sequence)",
            
            # Taxonomy indexes (from additional_fields.md)
            "CREATE INDEX taxonomy_energy_index IF NOT EXISTS FOR (s:Song) ON (s.taxonomy_energy_level)",
            "CREATE INDEX taxonomy_valence_index IF NOT EXISTS FOR (s:Song) ON (s.taxonomy_emotional_valence)",
            "CREATE INDEX taxonomy_time_index IF NOT EXISTS FOR (s:Song) ON (s.taxonomy_time_primary)",
            "CREATE INDEX taxonomy_activity_index IF NOT EXISTS FOR (s:Song) ON (s.taxonomy_activity_category)",
            
            # Composite indexes for common queries
            "CREATE INDEX composite_energy_valence IF NOT EXISTS FOR (s:Song) ON (s.taxonomy_energy_level, s.taxonomy_emotional_valence)",
            "CREATE INDEX composite_time_activity IF NOT EXISTS FOR (s:Song) ON (s.taxonomy_time_primary, s.taxonomy_activity_category)",
            
            # Word analysis indexes
            "CREATE INDEX word_complexity_index IF NOT EXISTS FOR (s:Song) ON (s.vocabulary_complexity)",
            "CREATE INDEX unique_word_count_index IF NOT EXISTS FOR (s:Song) ON (s.unique_word_count)"
        ]
        
        with self.driver.session() as session:
            for index_query in indexes:
                try:
                    session.run(index_query)
                    index_name = index_query.split()[2]
                    logger.info(f"✅ Created index: {index_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Index may already exist: {e}")
    
    # ======= VALIDATION & ANALYTICS =======
    
    def validate_unified_system(self) -> Dict:
        """Comprehensive validation of the unified system"""
        logger.info("🔍 Validating unified word + taxonomy system...")
        
        with self.driver.session() as session:
            validation_query = """
            // Comprehensive system validation
            MATCH (wd:WordDictionary)
            WITH count(wd) as total_words
            
            MATCH (l:Lyric) WHERE l.word_sequence IS NOT NULL
            WITH total_words, count(l) as converted_lyrics,
                 avg(size(l.word_sequence)) as avg_words_per_line
            
            MATCH (s:Song) WHERE s.taxonomy_energy_level IS NOT NULL
            WITH total_words, converted_lyrics, avg_words_per_line,
                 count(s) as songs_with_taxonomies,
                 avg(s.vocabulary_complexity) as avg_vocab_complexity,
                 avg(s.calculation_confidence) as avg_confidence
            
            // Sample reconstruction test
            MATCH (l:Lyric) WHERE l.word_sequence IS NOT NULL
            WITH total_words, converted_lyrics, avg_words_per_line,
                 songs_with_taxonomies, avg_vocab_complexity, avg_confidence,
                 l LIMIT 3
            
            UNWIND l.word_sequence as word_id
            MATCH (wd:WordDictionary {id: word_id})
            WITH total_words, converted_lyrics, avg_words_per_line,
                 songs_with_taxonomies, avg_vocab_complexity, avg_confidence,
                 l, collect(wd.text) as reconstructed_words
            
            RETURN total_words, converted_lyrics, avg_words_per_line,
                   songs_with_taxonomies, avg_vocab_complexity, avg_confidence,
                   l.original_text as original,
                   apoc.text.join(reconstructed_words, ' ') as reconstructed
            """
            
            results = list(session.run(validation_query))
            
            if results:
                stats = results[0]
                validation_data = {
                    'total_words': stats['total_words'],
                    'converted_lyrics': stats['converted_lyrics'],
                    'avg_words_per_line': round(stats['avg_words_per_line'], 2),
                    'songs_with_taxonomies': stats['songs_with_taxonomies'],
                    'avg_vocab_complexity': round(stats['avg_vocab_complexity'], 3),
                    'avg_confidence': round(stats['avg_confidence'], 3),
                    'reconstruction_samples': []
                }
                
                # Check reconstruction accuracy
                for result in results:
                    if result['original'] and result['reconstructed']:
                        validation_data['reconstruction_samples'].append({
                            'original': result['original'],
                            'reconstructed': result['reconstructed'],
                            'match': result['original'] == result['reconstructed']
                        })
                
                logger.info("📊 Unified System Validation:")
                logger.info(f"   Words: {validation_data['total_words']:,}")
                logger.info(f"   Converted Lyrics: {validation_data['converted_lyrics']:,}")
                logger.info(f"   Songs with Taxonomies: {validation_data['songs_with_taxonomies']:,}")
                logger.info(f"   Avg Vocabulary Complexity: {validation_data['avg_vocab_complexity']}")
                logger.info(f"   Avg Calculation Confidence: {validation_data['avg_confidence']}")
                
                return validation_data
        
        return {}
    
    # ======= UTILITY METHODS =======
    
    def _get_energy_label(self, energy_level: float) -> str:
        """Convert energy level to label"""
        if energy_level >= 0.8: return "High Energy"
        elif energy_level >= 0.6: return "Energetic"
        elif energy_level >= 0.4: return "Moderate"
        else: return "Chill"
    
    def _get_emotional_label(self, valence: float) -> str:
        """Convert emotional valence to label"""
        if valence >= 0.8: return "Euphoric"
        elif valence >= 0.6: return "Uplifting"
        elif valence >= 0.4: return "Neutral"
        elif valence >= 0.2: return "Reflective"
        else: return "Melancholic"
    
    def _get_complexity_label(self, complexity: float) -> str:
        """Convert complexity score to label"""
        if complexity >= 0.75: return "Very Complex"
        elif complexity >= 0.5: return "Complex"
        elif complexity >= 0.25: return "Moderate"
        else: return "Simple"
    
    def _get_intimacy_label(self, intimacy: float) -> str:
        """Convert intimacy level to label"""
        if intimacy >= 0.8: return "Very Intimate"
        elif intimacy >= 0.6: return "Intimate"
        elif intimacy >= 0.4: return "Personal"
        elif intimacy >= 0.2: return "Social"
        else: return "Public"
    
    def _get_focus_label(self, focus: float) -> str:
        """Convert focus suitability to label"""
        if focus >= 0.75: return "Ideal Focus"
        elif focus >= 0.5: return "Suitable"
        elif focus >= 0.25: return "Background"
        else: return "Distracting"
    
    def _determine_time_of_day(self, energy: float, tempo: float, acousticness: float, 
                              valence: float, danceability: float) -> Tuple[str, str]:
        """Determine optimal time of day for song"""
        
        # Calculate time scores
        night_score = (1 - energy) * 0.3 + acousticness * 0.3 + (1 - valence) * 0.2 + (1 - danceability) * 0.2
        morning_score = energy * 0.3 + valence * 0.3 + (tempo / 200.0) * 0.2 + danceability * 0.2
        evening_score = energy * 0.2 + valence * 0.2 + danceability * 0.3 + (1 - acousticness) * 0.3
        
        # Determine primary time
        scores = {
            "Night": night_score,
            "Morning": morning_score,
            "Evening": evening_score,
            "Afternoon": (morning_score + evening_score) / 2
        }
        
        primary_time = max(scores, key=scores.get)
        
        # Determine specific context
        if night_score > 0.7:
            specific = "3AM Thoughts"
        elif morning_score > 0.7:
            specific = "Morning Motivation"
        elif evening_score > 0.7:
            specific = "Evening Party"
        else:
            specific = "Any Time"
        
        return specific, primary_time
    
    def _determine_activity_match(self, tempo: float, energy: float, danceability: float,
                                 instrumentalness: float, valence: float, acousticness: float) -> Tuple[str, str]:
        """Determine optimal activity for song"""
        
        # Calculate activity scores
        workout_score = energy * 0.4 + (tempo / 200.0) * 0.3 + danceability * 0.3
        study_score = instrumentalness * 0.4 + (1 - energy) * 0.3 + acousticness * 0.3
        social_score = danceability * 0.3 + energy * 0.3 + valence * 0.2 + (1 - acousticness) * 0.2
        relaxation_score = acousticness * 0.4 + (1 - energy) * 0.3 + (1 - tempo / 200.0) * 0.3
        
        # Determine activity category
        scores = {
            "Workout": workout_score,
            "Study": study_score,
            "Social": social_score,
            "Relaxation": relaxation_score
        }
        
        category = max(scores, key=scores.get)
        
        # Determine specific activity
        if workout_score > 0.8:
            specific = "High Intensity Workout"
        elif study_score > 0.7:
            specific = "Deep Focus"
        elif social_score > 0.7:
            specific = "Dancing"
        elif relaxation_score > 0.7:
            specific = "Wind Down"
        else:
            specific = "General Listening"
        
        return specific, category
    
    def run_complete_unified_implementation(self) -> Dict:
        """Execute the complete unified implementation"""
        logger.info("🚀 Starting Unified Word Identifier & Music Taxonomy Implementation")
        
        # Phase 1: Word Identifier System
        words_created = self.phase1_create_word_registry()
        songs_converted = self.phase1_convert_song_sequences()
        
        # Phase 2: Music Taxonomy Integration
        taxonomies_calculated = self.phase2_calculate_comprehensive_taxonomies()
        
        # Phase 3: Performance Optimization
        self.phase3_create_unified_indexes()
        
        # Validation
        validation_results = self.validate_unified_system()
        
        # Final statistics
        total_time = time.time() - self.stats['start_time']
        
        results = {
            'phase1_words_created': words_created,
            'phase1_songs_converted': songs_converted,
            'phase2_taxonomies_calculated': taxonomies_calculated,
            'total_execution_time': round(total_time, 2),
            'validation_results': validation_results,
            'system_status': 'Complete ✅'
        }
        
        logger.info("🎉 Unified Implementation Complete!")
        logger.info(f"   Execution Time: {total_time:.2f}s")
        logger.info(f"   Words Created: {words_created:,}")
        logger.info(f"   Songs Converted: {songs_converted:,}")
        logger.info(f"   Taxonomies Calculated: {taxonomies_calculated:,}")
        
        return results
    
    def close(self):
        """Close database connection"""
        self.driver.close()


# ======= USAGE EXAMPLE =======

if __name__ == "__main__":
    # Initialize system
    system = UnifiedWordTaxonomySystem(
        uri="neo4j+s://your-instance.databases.neo4j.io",
        username="neo4j",
        password="your-password"
    )
    
    try:
        # Run complete implementation
        results = system.run_complete_unified_implementation()
        print(f"\n🎯 Final Results: {results}")
        
    finally:
        system.close() 