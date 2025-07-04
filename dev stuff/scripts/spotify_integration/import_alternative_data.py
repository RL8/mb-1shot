import os
import pandas as pd
import numpy as np
from neo4j import GraphDatabase
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../../.env.development')

class AlternativeDataImporter:
    def __init__(self):
        # Database connection using environment variables
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME') 
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not all([self.neo4j_uri, self.neo4j_password]):
            raise ValueError("❌ Missing AuraDB credentials in environment")
            
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password),
            max_connection_pool_size=50,
            connection_timeout=30
        )
        
        self.archive_path = "C:\\Users\\Bravo\\CascadeProjects\\mb-1shot-archive\\taylor"
        
        # Mapping of missing songs to their alternative matches
        self.alternative_matches = {
            # Perfect matches (100% similarity)
            "Sweeter Than Fiction": {
                "source": "Sweeter Than Fiction",
                "confidence": 1.0,
                "reason": "Perfect match found in CSV"
            },
            "Better Man": {
                "source": "Better Man", 
                "confidence": 1.0,
                "reason": "Perfect match found in CSV"
            },
            "Babe": {
                "source": "Babe",
                "confidence": 1.0,
                "reason": "Perfect match found in CSV"
            },
            
            # High confidence matches (vault tracks with close variants)
            "That's When": {
                "source": "That's When (Taylor's Version) [From The Vault]",
                "confidence": 0.9,
                "reason": "Same song, vault version with features available"
            },
            "Bye Bye Baby": {
                "source": "Bye Bye Baby (Taylor's Version) [From The Vault]",
                "confidence": 0.9,
                "reason": "Same song, vault version with features available"
            },
            "Foolish One": {
                "source": "Foolish One (Taylor's Version) [From The Vault]",
                "confidence": 0.9,
                "reason": "Same song, vault version with features available"
            },
            
            # Additional vault tracks found in comprehensive search
            "Don't You": {
                "source": "Don't You (Taylor's Version) [From The Vault]",
                "confidence": 0.9,
                "reason": "Same song, vault version with features available"
            },
            "Say Don't Go": {
                "source": "Say Don't Go (Taylor's Version) [From The Vault]",
                "confidence": 0.9,
                "reason": "Same song, vault version with features available"
            },
            "Nothing New": {
                "source": "Nothing New (Taylor's Version) [From The Vault]",
                "confidence": 0.9,
                "reason": "Same song, vault version with features available"
            },
            "Run": {
                "source": "Run (Taylor's Version) [From The Vault]",
                "confidence": 0.9,
                "reason": "Same song, vault version with features available"
            },
            "Timeless": {
                "source": "Timeless (Taylor's Version) [From The Vault]",
                "confidence": 0.9,
                "reason": "Same song, vault version with features available"
            }
        }
        
        # Load CSV data
        self.csv_data = None
        self._load_csv_data()
        
        # Special handling for songs without direct matches
        self.estimated_features = {
            '"Slut!"': {
                "method": "similar_songs_average",
                "confidence": 0.8,
                "reason": "Estimated from similar 1989 era vault tracks",
                "base_songs": ["Is It Over Now?", "Now That We Don't Talk"]
            }
        }
    
    def _load_csv_data(self):
        """Load the Spotify CSV data"""
        csv_path = os.path.join(self.archive_path, "data-raw", "spotify-data.csv")
        if os.path.exists(csv_path):
            self.csv_data = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(self.csv_data)} tracks from spotify-data.csv")
        else:
            print("❌ Could not find spotify-data.csv")
    
    def get_alternative_features(self, source_track_name):
        """Get audio features for the source track"""
        if self.csv_data is None:
            return None
        
        # Find the track in CSV
        matches = self.csv_data[self.csv_data['track_name'] == source_track_name]
        
        if len(matches) == 0:
            print(f"  ❌ No data found for source track: {source_track_name}")
            return None
        
        if len(matches) > 1:
            print(f"  ⚠️ Multiple matches for {source_track_name}, using first")
        
        row = matches.iloc[0]
        
        # Extract audio features
        features = {}
        audio_feature_columns = [
            'danceability', 'energy', 'key', 'loudness', 'mode', 
            'speechiness', 'acousticness', 'instrumentalness', 
            'liveness', 'valence', 'tempo', 'time_signature'
        ]
        
        for col in audio_feature_columns:
            if col in row and pd.notna(row[col]):
                features[col] = row[col]
        
        return features
    
    def estimate_features_from_similar_songs(self, song_title, estimation_config):
        """Estimate audio features based on similar songs"""
        if self.csv_data is None:
            return None
        
        base_songs = estimation_config.get("base_songs", [])
        if not base_songs:
            # Fallback: use album average for 1989 vault tracks
            album_songs = self.csv_data[self.csv_data['album_name'] == '1989 (Taylor\'s Version)']
            if len(album_songs) > 0:
                features = {}
                audio_feature_columns = [
                    'danceability', 'energy', 'key', 'loudness', 'mode', 
                    'speechiness', 'acousticness', 'instrumentalness', 
                    'liveness', 'valence', 'tempo', 'time_signature'
                ]
                
                for col in audio_feature_columns:
                    if col in album_songs.columns:
                        avg_value = album_songs[col].mean()
                        if not pd.isna(avg_value):
                            features[col] = avg_value
                
                print(f"  📊 Estimated features from 1989 album average")
                return features
        
        # Try to find base songs and average their features
        features = {}
        found_songs = []
        
        for base_song in base_songs:
            matches = self.csv_data[self.csv_data['track_name'].str.contains(base_song, case=False, na=False)]
            if len(matches) > 0:
                found_songs.append(matches.iloc[0])
        
        if found_songs:
            # Calculate average features from similar songs
            audio_feature_columns = [
                'danceability', 'energy', 'key', 'loudness', 'mode', 
                'speechiness', 'acousticness', 'instrumentalness', 
                'liveness', 'valence', 'tempo', 'time_signature'
            ]
            
            for col in audio_feature_columns:
                values = []
                for song_row in found_songs:
                    if col in song_row and pd.notna(song_row[col]):
                        values.append(song_row[col])
                
                if values:
                    features[col] = sum(values) / len(values)
            
            print(f"  📊 Estimated features from {len(found_songs)} similar songs")
            return features
        
        return None
    
    def update_song_with_alternative_data(self, song_title, album_code, source_track, confidence, reason):
        """Update a song with alternative audio features data"""
        
        # Get features from alternative source
        features = self.get_alternative_features(source_track)
        if not features:
            return False
        
        # Prepare the update query
        set_clauses = []
        params = {
            'title': song_title,
            'albumCode': album_code,
            'source_track': source_track,
            'confidence': confidence,
            'reason': reason,
            'import_timestamp': int(time.time()),
            'import_source': 'alternative_csv_data'
        }
        
        # Add audio features to the query
        for feature, value in features.items():
            set_clauses.append(f"s.{feature} = ${feature}")
            params[feature] = value
        
        # Add metadata about the alternative source
        set_clauses.extend([
            "s.import_timestamp = $import_timestamp",
            "s.import_source = $import_source",
            "s.alternative_source_track = $source_track",
            "s.alternative_confidence = $confidence",
            "s.alternative_reason = $reason"
        ])
        
        query = f"""
        MATCH (s:Song {{title: $title, albumCode: $albumCode}})
        SET {', '.join(set_clauses)}
        RETURN s.title as title, s.albumCode as album
        """
        
        with self.driver.session() as session:
            result = session.run(query, params)
            records = list(result)
            
            if records:
                print(f"  ✅ Updated {song_title} ({album_code}) with alternative data")
                return True
            else:
                print(f"  ❌ Song not found: {song_title} ({album_code})")
                return False
    
    def update_song_with_estimated_data(self, song_title, album_code, estimation_config):
        """Update a song with estimated audio features"""
        
        # Get estimated features
        features = self.estimate_features_from_similar_songs(song_title, estimation_config)
        if not features:
            return False
        
        # Prepare the update query
        set_clauses = []
        params = {
            'title': song_title,
            'albumCode': album_code,
            'estimation_method': estimation_config['method'],
            'confidence': estimation_config['confidence'],
            'reason': estimation_config['reason'],
            'import_timestamp': int(time.time()),
            'import_source': 'estimated_features'
        }
        
        # Add audio features to the query
        for feature, value in features.items():
            set_clauses.append(f"s.{feature} = ${feature}")
            params[feature] = value
        
        # Add metadata about the estimation
        set_clauses.extend([
            "s.import_timestamp = $import_timestamp",
            "s.import_source = $import_source",
            "s.estimation_method = $estimation_method",
            "s.estimation_confidence = $confidence",
            "s.estimation_reason = $reason"
        ])
        
        query = f"""
        MATCH (s:Song {{title: $title, albumCode: $albumCode}})
        SET {', '.join(set_clauses)}
        RETURN s.title as title, s.albumCode as album
        """
        
        with self.driver.session() as session:
            result = session.run(query, params)
            records = list(result)
            
            if records:
                print(f"  ✅ Updated {song_title} ({album_code}) with estimated data")
                return True
            else:
                print(f"  ❌ Song not found: {song_title} ({album_code})")
                return False
    
    def import_all_alternatives(self):
        """Import all alternative data for missing songs"""
        total_to_process = len(self.alternative_matches) + len(self.estimated_features)
        print("🚀 Starting comprehensive alternative data import...")
        print(f"📊 Will attempt to import {total_to_process} songs")
        print(f"  📁 {len(self.alternative_matches)} direct matches")
        print(f"  🔮 {len(self.estimated_features)} estimated features")
        
        success_count = 0
        
        # Process direct alternative matches
        for song_title, match_info in self.alternative_matches.items():
            print(f"\n🎵 Processing: {song_title}")
            print(f"  📁 Source: {match_info['source']}")
            print(f"  🎯 Confidence: {match_info['confidence']:.1%}")
            print(f"  💡 Reason: {match_info['reason']}")
            
            # First, find the song in AuraDB to get its album code
            album_code = self._find_song_album_code(song_title)
            
            if album_code:
                success = self.update_song_with_alternative_data(
                    song_title, 
                    album_code,
                    match_info['source'],
                    match_info['confidence'],
                    match_info['reason']
                )
                if success:
                    success_count += 1
            else:
                print(f"  ❌ Could not find {song_title} in AuraDB")
        
        # Process estimated features
        for song_title, estimation_config in self.estimated_features.items():
            print(f"\n🔮 Processing (Estimation): {song_title}")
            print(f"  📊 Method: {estimation_config['method']}")
            print(f"  🎯 Confidence: {estimation_config['confidence']:.1%}")
            print(f"  💡 Reason: {estimation_config['reason']}")
            
            # Find the song in AuraDB to get its album code
            album_code = self._find_song_album_code(song_title)
            
            if album_code:
                success = self.update_song_with_estimated_data(
                    song_title,
                    album_code,
                    estimation_config
                )
                if success:
                    success_count += 1
            else:
                print(f"  ❌ Could not find {song_title} in AuraDB")
        
        print(f"\n📊 Import completed!")
        print(f"  ✅ Successfully imported: {success_count}/{total_to_process} songs")
        
        return success_count
    
    def _find_song_album_code(self, song_title):
        """Find the album code for a song title"""
        query = """
        MATCH (s:Song {title: $title})
        RETURN s.albumCode as albumCode
        """
        
        with self.driver.session() as session:
            result = session.run(query, {'title': song_title})
            records = list(result)
            
            if records:
                return records[0]['albumCode']
            else:
                return None
    
    def validate_import(self):
        """Validate the alternative data import"""
        print("\n🔍 Validating comprehensive data import...")
        
        # Check alternative CSV data
        query_alt = """
        MATCH (s:Song) 
        WHERE s.import_source = 'alternative_csv_data'
        RETURN s.title as title, s.albumCode as album, 
               s.energy as energy, s.valence as valence,
               s.alternative_source_track as source,
               s.alternative_confidence as confidence
        ORDER BY s.albumCode, s.title
        """
        
        # Check estimated features
        query_est = """
        MATCH (s:Song) 
        WHERE s.import_source = 'estimated_features'
        RETURN s.title as title, s.albumCode as album, 
               s.energy as energy, s.valence as valence,
               s.estimation_method as method,
               s.estimation_confidence as confidence
        ORDER BY s.albumCode, s.title
        """
        
        with self.driver.session() as session:
            # Check alternative data
            result_alt = session.run(query_alt)
            records_alt = list(result_alt)
            
            # Check estimated data
            result_est = session.run(query_est)
            records_est = list(result_est)
            
            total_imported = len(records_alt) + len(records_est)
            
            if records_alt:
                print(f"✅ Found {len(records_alt)} songs with alternative data:")
                for record in records_alt:
                    print(f"  🎵 {record['title']} ({record['album']}) - E:{record['energy']:.3f} V:{record['valence']:.3f}")
                    print(f"     📁 Source: {record['source']} (confidence: {record['confidence']:.1%})")
            
            if records_est:
                print(f"✅ Found {len(records_est)} songs with estimated features:")
                for record in records_est:
                    print(f"  🔮 {record['title']} ({record['album']}) - E:{record['energy']:.3f} V:{record['valence']:.3f}")
                    print(f"     📊 Method: {record['method']} (confidence: {record['confidence']:.1%})")
            
            if total_imported == 0:
                print("❌ No songs found with alternative or estimated data")
    
    def get_final_coverage_stats(self):
        """Get final coverage statistics"""
        print("\n📊 Final Coverage Statistics:")
        
        query = """
        MATCH (s:Song) 
        RETURN count(s) as total_songs, 
               count(s.energy) as with_features,
               (count(s.energy) * 100.0 / count(s)) as coverage_percent
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            
            total = record['total_songs']
            with_features = record['with_features']
            coverage = record['coverage_percent']
            
            print(f"  📊 Total songs: {total}")
            print(f"  ✅ Songs with features: {with_features}")
            print(f"  📈 Coverage: {coverage:.1f}%")
            
            return total, with_features, coverage
    
    def close(self):
        """Close database connection"""
        self.driver.close()

def main():
    importer = AlternativeDataImporter()
    
    try:
        # Import alternative data
        success_count = importer.import_all_alternatives()
        
        # Validate the import
        importer.validate_import()
        
        # Get final statistics
        total, with_features, coverage = importer.get_final_coverage_stats()
        
        print(f"\n🎯 Alternative data import completed!")
        print(f"📊 Imported {success_count} songs with alternative data")
        print(f"📈 Final coverage: {coverage:.1f}%")
        
    finally:
        importer.close()

if __name__ == "__main__":
    main() 