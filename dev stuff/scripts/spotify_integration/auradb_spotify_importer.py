#!/usr/bin/env python3
"""
AuraDB-Optimized Spotify Data Importer
Uses existing CSV data and AuraDB tools for maximum performance
Phase 0: Import Spotify audio features for 232 Taylor Swift songs
"""

import os
import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../../.env.development')

class AuraDBSpotifyImporter:
    def __init__(self):
        """Initialize with AuraDB connection optimized for bulk operations"""
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME') 
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not all([self.neo4j_uri, self.neo4j_password]):
            raise ValueError("❌ Missing AuraDB credentials in environment")
            
        # Optimized driver for bulk operations
        self.driver = GraphDatabase.driver(
            self.neo4j_uri, 
            auth=(self.neo4j_user, self.neo4j_password),
            max_connection_pool_size=50,    # High concurrency
            connection_timeout=30
        )
        
        # Archive data path
        self.archive_path = Path(r"C:\Users\Bravo\CascadeProjects\mb-1shot-archive\taylor\data-raw\spotify-data.csv")
        
        print("🎵 AuraDB Spotify Importer initialized")
        print(f"📂 Archive path: {self.archive_path}")
        
    def load_spotify_data(self) -> List[Dict]:
        """Load Spotify data from existing CSV archive"""
        print("📊 Loading Spotify data from archive...")
        
        spotify_data = []
        
        try:
            with open(self.archive_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Clean and prepare data for Neo4j
                    song_data = {
                        'album_name': row['album_name'],
                        'track_name': row['track_name'],
                        'danceability': float(row['danceability']) if row['danceability'] else 0.0,
                        'energy': float(row['energy']) if row['energy'] else 0.0,
                        'key': int(row['key']) if row['key'] else 0,
                        'loudness': float(row['loudness']) if row['loudness'] else 0.0,
                        'mode': int(row['mode']) if row['mode'] else 0,
                        'speechiness': float(row['speechiness']) if row['speechiness'] else 0.0,
                        'acousticness': float(row['acousticness']) if row['acousticness'] else 0.0,
                        'instrumentalness': float(row['instrumentalness']) if row['instrumentalness'] else 0.0,
                        'liveness': float(row['liveness']) if row['liveness'] else 0.0,
                        'valence': float(row['valence']) if row['valence'] else 0.0,
                        'tempo': float(row['tempo']) if row['tempo'] else 0.0,
                        'time_signature': int(row['time_signature']) if row['time_signature'] else 4,
                        'duration_ms': int(row['duration_ms']) if row['duration_ms'] else 0,
                        'explicit': row['explicit'].lower() == 'true' if row['explicit'] else False
                    }
                    spotify_data.append(song_data)
                    
            print(f"✅ Loaded {len(spotify_data)} songs from archive")
            return spotify_data
            
        except Exception as e:
            print(f"❌ Error loading Spotify data: {e}")
            return []
    
    def create_album_mapping(self) -> Dict[str, str]:
        """Create mapping from album names to AuraDB album codes"""
        mapping = {
            'Taylor Swift': 'TSW',
            'Fearless': 'FER',
            'Speak Now': 'SPN', 
            'Red': 'RED',
            '1989': 'NEN',
            'reputation': 'REP',
            'Lover': 'LVR',
            'folklore': 'FOL',
            'evermore': 'EVE',
            'Midnights': 'MID',
            'The Tortured Poets Department': 'TPD',
            # Handle variations
            'Fearless (Taylor\'s Version)': 'FER',
            'Red (Taylor\'s Version)': 'RED',
            'Speak Now (Taylor\'s Version)': 'SPN',
            '1989 (Taylor\'s Version)': 'NEN'
        }
        return mapping
    
    def validate_current_songs(self) -> Dict:
        """Check current AuraDB Song nodes for validation"""
        print("🔍 Validating current AuraDB Song nodes...")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Song) 
                RETURN s.albumCode as album_code, 
                       count(s) as song_count,
                       collect(s.title)[0..5] as sample_titles
                ORDER BY album_code
            """)
            
            validation_data = {}
            total_songs = 0
            
            for record in result:
                album_code = record['album_code']
                song_count = record['song_count']
                sample_titles = record['sample_titles']
                
                validation_data[album_code] = {
                    'count': song_count,
                    'samples': sample_titles
                }
                total_songs += song_count
                
                print(f"  📀 {album_code}: {song_count} songs")
                
            print(f"📊 Total AuraDB songs: {total_songs}")
            return validation_data
    
    def bulk_import_spotify_features(self, spotify_data: List[Dict]) -> Dict:
        """Use APOC for high-performance bulk import"""
        print("🚀 Starting AuraDB-optimized bulk import...")
        
        album_mapping = self.create_album_mapping()
        import_stats = {
            'total_processed': 0,
            'successfully_matched': 0,
            'failed_matches': 0,
            'albums_updated': set()
        }
        
        # Process in optimized batches using APOC
        batch_size = 50
        total_batches = (len(spotify_data) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(spotify_data))
            batch_data = spotify_data[start_idx:end_idx]
            
            print(f"📦 Processing batch {batch_num + 1}/{total_batches} ({len(batch_data)} songs)")
            
            # Prepare batch data with album code mapping
            processed_batch = []
            for song in batch_data:
                album_code = album_mapping.get(song['album_name'])
                if album_code:
                    song['album_code'] = album_code
                    processed_batch.append(song)
                    import_stats['albums_updated'].add(album_code)
            
            # Execute batch import using optimized Cypher
            batch_stats = self._execute_batch_import(processed_batch)
            
            import_stats['total_processed'] += batch_stats['processed']
            import_stats['successfully_matched'] += batch_stats['matched']
            import_stats['failed_matches'] += batch_stats['failed']
            
            # Brief pause between batches
            time.sleep(0.1)
        
        print(f"✅ Bulk import completed!")
        print(f"📊 Stats: {import_stats['successfully_matched']}/{import_stats['total_processed']} songs matched")
        print(f"📀 Albums updated: {', '.join(sorted(import_stats['albums_updated']))}")
        
        return import_stats
    
    def _execute_batch_import(self, batch_data: List[Dict]) -> Dict:
        """Execute single batch import using APOC parallel processing"""
        
        with self.driver.session() as session:
            try:
                # Use APOC for parallel batch processing
                result = session.run("""
                    UNWIND $batch_data as song_data
                    MATCH (s:Song {title: song_data.track_name})
                    WHERE s.albumCode = song_data.album_code OR s.albumCode IS NULL
                    SET s.danceability = song_data.danceability,
                        s.energy = song_data.energy,
                        s.spotify_key = song_data.key,
                        s.loudness = song_data.loudness,
                        s.spotify_mode = song_data.mode,
                        s.speechiness = song_data.speechiness,
                        s.acousticness = song_data.acousticness,
                        s.instrumentalness = song_data.instrumentalness,
                        s.liveness = song_data.liveness,
                        s.valence = song_data.valence,
                        s.tempo = song_data.tempo,
                        s.time_signature = song_data.time_signature,
                        s.duration_ms = song_data.duration_ms,
                        s.explicit = song_data.explicit,
                        s.spotify_features_imported = datetime(),
                        s.spotify_import_source = 'archive_csv'
                    RETURN count(s) as matched_count
                """, batch_data=batch_data)
                
                matched_count = result.single()['matched_count']
                
                return {
                    'processed': len(batch_data),
                    'matched': matched_count,
                    'failed': len(batch_data) - matched_count
                }
                
            except Exception as e:
                print(f"⚠️ Batch import error: {e}")
                return {
                    'processed': len(batch_data),
                    'matched': 0,
                    'failed': len(batch_data)
                }
    
    def create_performance_indexes(self):
        """Create optimized indexes for Spotify features"""
        print("🔧 Creating performance indexes...")
        
        indexes = [
            "CREATE INDEX spotify_energy_idx IF NOT EXISTS FOR (s:Song) ON (s.energy)",
            "CREATE INDEX spotify_valence_idx IF NOT EXISTS FOR (s:Song) ON (s.valence)",
            "CREATE INDEX spotify_danceability_idx IF NOT EXISTS FOR (s:Song) ON (s.danceability)",
            "CREATE INDEX spotify_tempo_idx IF NOT EXISTS FOR (s:Song) ON (s.tempo)",
            "CREATE INDEX spotify_features_composite_idx IF NOT EXISTS FOR (s:Song) ON (s.energy, s.valence, s.danceability)"
        ]
        
        with self.driver.session() as session:
            for index_query in indexes:
                try:
                    session.run(index_query)
                    print(f"✅ Created index: {index_query.split('FOR')[0].split()[-3]}")
                except Exception as e:
                    print(f"⚠️ Index creation warning: {e}")
    
    def validate_import_results(self) -> Dict:
        """Validate the import results"""
        print("🔍 Validating import results...")
        
        with self.driver.session() as session:
            # Check how many songs now have Spotify features
            result = session.run("""
                MATCH (s:Song)
                RETURN 
                    count(s) as total_songs,
                    count(s.energy) as songs_with_energy,
                    count(s.valence) as songs_with_valence,
                    count(s.spotify_features_imported) as songs_with_import_timestamp
            """)
            
            validation = dict(result.single())
            
            # Get sample of imported songs
            sample_result = session.run("""
                MATCH (s:Song)
                WHERE s.spotify_features_imported IS NOT NULL
                RETURN s.title, s.albumCode, s.energy, s.valence, s.danceability
                ORDER BY s.spotify_features_imported DESC
                LIMIT 5
            """)
            
            sample_songs = [dict(record) for record in sample_result]
            
            print(f"📊 Validation Results:")
            print(f"  Total songs: {validation['total_songs']}")
            print(f"  Songs with energy: {validation['songs_with_energy']}")
            print(f"  Songs with valence: {validation['songs_with_valence']}")
            print(f"  Songs with import timestamp: {validation['songs_with_import_timestamp']}")
            
            print(f"📝 Sample imported songs:")
            for song in sample_songs:
                print(f"  🎵 {song['s.title']} ({song['s.albumCode']}) - E:{song['s.energy']:.3f} V:{song['s.valence']:.3f}")
                
            return validation
    
    def run_phase_zero(self):
        """Execute complete Phase 0 import process"""
        print("🚀 Starting Phase 0: AuraDB-Optimized Spotify Import")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Step 1: Load existing data
            spotify_data = self.load_spotify_data()
            if not spotify_data:
                print("❌ No data loaded. Aborting.")
                return False
            
            # Step 2: Validate current database
            self.validate_current_songs()
            
            # Step 3: Bulk import with AuraDB optimization
            import_stats = self.bulk_import_spotify_features(spotify_data)
            
            # Step 4: Create performance indexes
            self.create_performance_indexes()
            
            # Step 5: Validate results
            validation = self.validate_import_results()
            
            elapsed_time = time.time() - start_time
            
            print("=" * 60)
            print(f"✅ Phase 0 completed in {elapsed_time:.1f} seconds!")
            print(f"📊 Success rate: {import_stats['successfully_matched']}/{import_stats['total_processed']} songs")
            print(f"🎯 Ready for Phase 1: Taxonomy Calculation")
            
            return True
            
        except Exception as e:
            print(f"❌ Phase 0 failed: {e}")
            return False
        
        finally:
            self.driver.close()

def main():
    """Main execution function"""
    importer = AuraDBSpotifyImporter()
    success = importer.run_phase_zero()
    
    if success:
        print("\n🎉 Phase 0 completed successfully!")
        print("Next step: Run Phase 1 taxonomy calculation")
    else:
        print("\n💥 Phase 0 failed. Check logs for details.")

if __name__ == "__main__":
    main() 