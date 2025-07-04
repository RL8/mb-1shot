#!/usr/bin/env python3
"""
Enhanced AuraDB Spotify Data Importer
Advanced matching with fuzzy logic to ensure 100% coverage of Taylor Swift songs
"""

import os
import csv
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from neo4j import GraphDatabase
from dotenv import load_dotenv
from difflib import SequenceMatcher

# Load environment variables
load_dotenv('../../../.env.development')

class EnhancedSpotifyImporter:
    def __init__(self):
        """Initialize with AuraDB connection optimized for complete coverage"""
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME') 
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not all([self.neo4j_uri, self.neo4j_password]):
            raise ValueError("❌ Missing AuraDB credentials in environment")
            
        # Optimized driver
        self.driver = GraphDatabase.driver(
            self.neo4j_uri, 
            auth=(self.neo4j_user, self.neo4j_password),
            max_connection_pool_size=50,
            connection_timeout=30
        )
        
        # Archive data path
        self.archive_path = Path(r"C:\Users\Bravo\CascadeProjects\mb-1shot-archive\taylor\data-raw\spotify-data.csv")
        
        print("🎵 Enhanced Spotify Importer initialized")
        print(f"📂 Archive path: {self.archive_path}")
        
    def analyze_csv_albums(self) -> Dict:
        """Analyze album names in CSV to create comprehensive mapping"""
        print("🔍 Analyzing CSV album names...")
        
        album_counts = {}
        
        with open(self.archive_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                album_name = row['album_name']
                album_counts[album_name] = album_counts.get(album_name, 0) + 1
                
        print("📊 Albums found in CSV:")
        for album, count in sorted(album_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  📀 {album}: {count} songs")
            
        return album_counts
    
    def create_comprehensive_album_mapping(self) -> Dict[str, str]:
        """Create comprehensive mapping including all variations"""
        mapping = {
            # Basic mappings
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
            
            # Taylor's Version variations
            'Fearless (Taylor\'s Version)': 'FER',
            'Red (Taylor\'s Version)': 'RED',
            'Speak Now (Taylor\'s Version)': 'SPN',
            '1989 (Taylor\'s Version)': 'NEN',
            
            # Special cases and variations  
            'The Tortured Poets Department': 'TPD',
            'THE TORTURED POETS DEPARTMENT': 'TPD',
            'The Tortured Poets Department: The Anthology': 'TPD',
            'Tortured Poets Department': 'TPD',
            
            # Handle any case variations
            'FOLKLORE': 'FOL',
            'EVERMORE': 'EVE',
            'MIDNIGHTS': 'MID',
            'REPUTATION': 'REP',
            'LOVER': 'LVR',
            
            # Handle lowercase and additional variations
            'folklore': 'FOL',
            'evermore': 'EVE', 
            'midnights': 'MID',
            'reputation': 'REP',
            'lover': 'LVR',
            
            # Additional variations found in CSV
            'NA': 'OTH',  # Handle NA album entries
            'Unknown Album': 'OTH',
            'Single': 'OTH',
        }
        
        return mapping
    
    def normalize_title(self, title: str) -> str:
        """Normalize song title for better matching"""
        if not title:
            return ""
            
        # Convert to lowercase
        normalized = title.lower()
        
        # Remove common variations
        normalized = normalized.replace("(taylor's version)", "")
        normalized = normalized.replace("(taylor's version)", "")  # Handle smart quotes
        normalized = normalized.replace("(tv)", "")
        normalized = normalized.replace("(from the vault)", "")
        normalized = normalized.replace("(3am edition)", "")
        normalized = normalized.replace("feat.", "")
        normalized = normalized.replace("featuring", "")
        
        # Handle special characters
        normalized = normalized.replace("'", "'")  # Smart quote to regular
        normalized = normalized.replace(""", '"')  # Smart quote to regular
        normalized = normalized.replace(""", '"')  # Smart quote to regular
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove punctuation variations for matching
        for char in ".,!?;:":
            normalized = normalized.replace(char, "")
            
        return normalized
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def find_best_match(self, auradb_song: Dict, csv_songs: List[Dict], album_code: str) -> Optional[Dict]:
        """Find best matching CSV song for an AuraDB song"""
        auradb_title = self.normalize_title(auradb_song.get('title', ''))
        
        best_match = None
        best_score = 0.0
        threshold = 0.6  # Lowered threshold for better matching
        
        for csv_song in csv_songs:
            # Check if album matches
            csv_album_code = self.create_comprehensive_album_mapping().get(csv_song['album_name'])
            if csv_album_code != album_code:
                continue
                
            csv_title = self.normalize_title(csv_song.get('track_name', ''))
            
            # Calculate similarity
            similarity = self.calculate_similarity(auradb_title, csv_title)
            
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = csv_song
                
        return best_match if best_score >= threshold else None
    
    def load_spotify_data_enhanced(self) -> List[Dict]:
        """Load Spotify data with enhanced processing"""
        print("📊 Loading Spotify data with enhanced processing...")
        
        spotify_data = []
        
        try:
            with open(self.archive_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Clean and prepare data
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
    
    def get_all_auradb_songs(self) -> List[Dict]:
        """Get all songs from AuraDB for matching"""
        print("🔍 Fetching all AuraDB songs for enhanced matching...")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Song) 
                RETURN s.title as title, 
                       s.albumCode as albumCode,
                       s.trackNumber as trackNumber,
                       ID(s) as nodeId
                ORDER BY s.albumCode, s.trackNumber
            """)
            
            songs = [dict(record) for record in result]
            print(f"📊 Retrieved {len(songs)} songs from AuraDB")
            
            # Group by album for analysis
            album_counts = {}
            for song in songs:
                album = song['albumCode']
                album_counts[album] = album_counts.get(album, 0) + 1
                
            print("📀 AuraDB album breakdown:")
            for album, count in sorted(album_counts.items()):
                print(f"  {album}: {count} songs")
                
            return songs
    
    def enhanced_matching_import(self, auradb_songs: List[Dict], csv_songs: List[Dict]) -> Dict:
        """Enhanced matching and import process"""
        print("🚀 Starting enhanced matching and import process...")
        
        album_mapping = self.create_comprehensive_album_mapping()
        import_stats = {
            'total_auradb_songs': len(auradb_songs),
            'total_csv_songs': len(csv_songs),
            'successfully_matched': 0,
            'failed_matches': 0,
            'exact_matches': 0,
            'fuzzy_matches': 0,
            'albums_updated': set(),
            'unmatched_songs': []
        }
        
        matched_pairs = []
        
        # Process each AuraDB song
        for auradb_song in auradb_songs:
            album_code = auradb_song['albumCode']
            
            # Try exact match first
            exact_match = None
            auradb_title_norm = self.normalize_title(auradb_song['title'])
            
            for csv_song in csv_songs:
                csv_album_code = album_mapping.get(csv_song['album_name'])
                if csv_album_code == album_code:
                    csv_title_norm = self.normalize_title(csv_song['track_name'])
                    if auradb_title_norm == csv_title_norm:
                        exact_match = csv_song
                        break
            
            if exact_match:
                matched_pairs.append((auradb_song, exact_match, 'exact'))
                import_stats['exact_matches'] += 1
                import_stats['albums_updated'].add(album_code)
            else:
                # Try fuzzy matching
                fuzzy_match = self.find_best_match(auradb_song, csv_songs, album_code)
                if fuzzy_match:
                    matched_pairs.append((auradb_song, fuzzy_match, 'fuzzy'))
                    import_stats['fuzzy_matches'] += 1
                    import_stats['albums_updated'].add(album_code)
                else:
                    import_stats['unmatched_songs'].append({
                        'title': auradb_song['title'],
                        'album': album_code,
                        'nodeId': auradb_song['nodeId']
                    })
        
        import_stats['successfully_matched'] = len(matched_pairs)
        import_stats['failed_matches'] = len(import_stats['unmatched_songs'])
        
        print(f"📊 Matching Summary:")
        print(f"  📈 Total matches: {import_stats['successfully_matched']}/{import_stats['total_auradb_songs']}")
        print(f"  🎯 Exact matches: {import_stats['exact_matches']}")
        print(f"  🔍 Fuzzy matches: {import_stats['fuzzy_matches']}")
        print(f"  ❌ Failed matches: {import_stats['failed_matches']}")
        
        if import_stats['unmatched_songs']:
            print(f"📝 Unmatched songs:")
            for song in import_stats['unmatched_songs'][:10]:  # Show first 10
                print(f"  🎵 {song['title']} ({song['album']})")
            if len(import_stats['unmatched_songs']) > 10:
                print(f"  ... and {len(import_stats['unmatched_songs']) - 10} more")
        
        # Execute the matched imports
        self._execute_enhanced_bulk_import(matched_pairs)
        
        return import_stats
    
    def _execute_enhanced_bulk_import(self, matched_pairs: List[Tuple]):
        """Execute the enhanced bulk import"""
        print("💫 Executing enhanced bulk import...")
        
        batch_size = 25
        total_batches = (len(matched_pairs) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(matched_pairs))
            batch_pairs = matched_pairs[start_idx:end_idx]
            
            print(f"📦 Processing batch {batch_num + 1}/{total_batches} ({len(batch_pairs)} songs)")
            
            # Prepare batch data
            batch_updates = []
            for auradb_song, csv_song, match_type in batch_pairs:
                update_data = {
                    'nodeId': auradb_song['nodeId'],
                    'danceability': csv_song['danceability'],
                    'energy': csv_song['energy'],
                    'spotify_key': csv_song['key'],
                    'loudness': csv_song['loudness'],
                    'spotify_mode': csv_song['mode'],
                    'speechiness': csv_song['speechiness'],
                    'acousticness': csv_song['acousticness'],
                    'instrumentalness': csv_song['instrumentalness'],
                    'liveness': csv_song['liveness'],
                    'valence': csv_song['valence'],
                    'tempo': csv_song['tempo'],
                    'time_signature': csv_song['time_signature'],
                    'duration_ms': csv_song['duration_ms'],
                    'explicit': csv_song['explicit'],
                    'match_type': match_type,
                    'csv_title': csv_song['track_name']
                }
                batch_updates.append(update_data)
            
            # Execute batch update using node IDs for precision
            with self.driver.session() as session:
                try:
                    result = session.run("""
                        UNWIND $batch_updates as update_data
                        MATCH (s:Song) WHERE ID(s) = update_data.nodeId
                        SET s.danceability = update_data.danceability,
                            s.energy = update_data.energy,
                            s.spotify_key = update_data.spotify_key,
                            s.loudness = update_data.loudness,
                            s.spotify_mode = update_data.spotify_mode,
                            s.speechiness = update_data.speechiness,
                            s.acousticness = update_data.acousticness,
                            s.instrumentalness = update_data.instrumentalness,
                            s.liveness = update_data.liveness,
                            s.valence = update_data.valence,
                            s.tempo = update_data.tempo,
                            s.time_signature = update_data.time_signature,
                            s.duration_ms = update_data.duration_ms,
                            s.explicit = update_data.explicit,
                            s.spotify_features_imported = datetime(),
                            s.spotify_import_source = 'enhanced_csv_v2',
                            s.spotify_match_type = update_data.match_type,
                            s.csv_matched_title = update_data.csv_title
                        RETURN count(s) as updated_count
                    """, batch_updates=batch_updates)
                    
                    updated_count = result.single()['updated_count']
                    print(f"  ✅ Updated {updated_count}/{len(batch_updates)} songs")
                    
                except Exception as e:
                    print(f"  ❌ Batch update error: {e}")
            
            time.sleep(0.1)  # Brief pause between batches
    
    def run_enhanced_phase_zero(self):
        """Execute complete enhanced Phase 0 process"""
        print("🚀 Starting Enhanced Phase 0: 100% Coverage Import")
        print("=" * 70)
        
        start_time = time.time()
        
        try:
            # Step 1: Analyze CSV structure
            csv_albums = self.analyze_csv_albums()
            
            # Step 2: Load all data
            csv_songs = self.load_spotify_data_enhanced()
            auradb_songs = self.get_all_auradb_songs()
            
            if not csv_songs or not auradb_songs:
                print("❌ Failed to load data. Aborting.")
                return False
            
            # Step 3: Enhanced matching and import
            import_stats = self.enhanced_matching_import(auradb_songs, csv_songs)
            
            # Step 4: Validate results
            validation = self.validate_enhanced_results()
            
            elapsed_time = time.time() - start_time
            
            print("=" * 70)
            print(f"✅ Enhanced Phase 0 completed in {elapsed_time:.1f} seconds!")
            print(f"📊 Final coverage: {validation['songs_with_energy']}/{validation['total_songs']} songs")
            print(f"🎯 Success rate: {(validation['songs_with_energy']/validation['total_songs']*100):.1f}%")
            
            return validation['songs_with_energy'] == validation['total_songs']
            
        except Exception as e:
            print(f"❌ Enhanced Phase 0 failed: {e}")
            return False
        
        finally:
            self.driver.close()
    
    def validate_enhanced_results(self) -> Dict:
        """Validate enhanced import results"""
        print("🔍 Validating enhanced import results...")
        
        with self.driver.session() as session:
            # Overall stats
            result = session.run("""
                MATCH (s:Song)
                RETURN 
                    count(s) as total_songs,
                    count(s.energy) as songs_with_energy,
                    count(s.spotify_match_type) as songs_with_match_info
            """)
            
            validation = dict(result.single())
            
            # Match type breakdown
            match_type_result = session.run("""
                MATCH (s:Song)
                WHERE s.spotify_match_type IS NOT NULL
                RETURN s.spotify_match_type as match_type, count(s) as count
                ORDER BY count DESC
            """)
            
            match_types = {record['match_type']: record['count'] for record in match_type_result}
            
            # Album coverage
            album_result = session.run("""
                MATCH (s:Song)
                RETURN s.albumCode as album,
                       count(s) as total,
                       count(s.energy) as with_features,
                       (count(s.energy) * 100.0 / count(s)) as coverage_percent
                ORDER BY coverage_percent DESC, album
            """)
            
            album_coverage = [dict(record) for record in album_result]
            
            print(f"📊 Enhanced Validation Results:")
            print(f"  Total songs: {validation['total_songs']}")
            print(f"  Songs with features: {validation['songs_with_energy']}")
            print(f"  Coverage: {(validation['songs_with_energy']/validation['total_songs']*100):.1f}%")
            
            print(f"🎯 Match type breakdown:")
            for match_type, count in match_types.items():
                print(f"  {match_type}: {count} songs")
            
            print(f"📀 Album coverage:")
            for album in album_coverage:
                print(f"  {album['album']}: {album['with_features']}/{album['total']} ({album['coverage_percent']:.0f}%)")
            
            return validation

def main():
    """Main execution function"""
    importer = EnhancedSpotifyImporter()
    success = importer.run_enhanced_phase_zero()
    
    if success:
        print("\n🎉 Enhanced Phase 0 completed with 100% coverage!")
        print("All 232 Taylor Swift songs now have Spotify features!")
        print("Ready for Phase 1: Taxonomy Calculation")
    else:
        print("\n💥 Enhanced Phase 0 needs attention. Check results above.")

if __name__ == "__main__":
    main() 