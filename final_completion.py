import os
import pandas as pd
import numpy as np
from neo4j import GraphDatabase
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../../.env.development')

class FinalCompletion:
    def __init__(self):
        # Database connection using environment variables
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME') 
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not all([self.neo4j_uri, self.neo4j_password]):
            raise ValueError("Missing required environment variables for AuraDB connection")
        
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        self.archive_path = "C:\\Users\\Bravo\\CascadeProjects\\mb-1shot-archive\\taylor"
        self.csv_data = None
        self._load_csv_data()

    def _load_csv_data(self):
        """Load the Spotify CSV data"""
        csv_path = os.path.join(self.archive_path, "data-raw", "spotify-data.csv")
        try:
            self.csv_data = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(self.csv_data)} tracks from spotify-data.csv")
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            self.csv_data = None

    def find_missing_songs(self):
        """Find all songs still missing audio features"""
        query = """
        MATCH (s:Song) 
        WHERE s.energy IS NULL 
        RETURN s.title as title, s.albumCode as album
        ORDER BY s.albumCode, s.title
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            records = list(result)
            
        print(f"🔍 Found {len(records)} songs still missing audio features:")
        for record in records:
            print(f"  🎵 {record['title']} ({record['album']})")
        
        return records

    def estimate_features_for_slut(self, song_title, album_code):
        """Estimate audio features for Slut! using 1989 album averages"""
        if self.csv_data is None:
            return False
        
        # Get 1989 (Taylor's Version) songs for estimation
        album_songs = self.csv_data[self.csv_data['album_name'] == '1989 (Taylor\'s Version)']
        
        if len(album_songs) == 0:
            # Fallback to original 1989
            album_songs = self.csv_data[self.csv_data['album_name'] == '1989']
        
        if len(album_songs) == 0:
            print("  ❌ No 1989 album songs found for estimation")
            return False
        
        # Calculate average features from 1989 songs
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
        
        # Prepare the update query
        set_clauses = []
        params = {
            'title': song_title,
            'albumCode': album_code,
            'estimation_method': 'album_average_1989',
            'confidence': 0.75,
            'reason': 'Estimated from 1989 (Taylor\'s Version) album average',
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
                print(f"  ✅ Updated {song_title} ({album_code}) with estimated features")
                print(f"  📊 Used {len(album_songs)} songs from 1989 album for averaging")
                return True
            else:
                print(f"  ❌ Could not find song: {song_title} ({album_code})")
                return False

    def complete_final_songs(self):
        """Complete the final missing songs to achieve 100% coverage"""
        print("🚀 Starting final completion for 100% coverage...")
        
        # Find missing songs
        missing_songs = self.find_missing_songs()
        
        success_count = 0
        
        for record in missing_songs:
            song_title = record['title']
            album_code = record['album']
            
            print(f"\n🔮 Processing final song: {song_title} ({album_code})")
            
            # Handle each song individually
            if 'Slut' in song_title:
                success = self.estimate_features_for_slut(song_title, album_code)
                if success:
                    success_count += 1
            else:
                # For any other songs, try basic estimation
                print(f"  ⚠️ Unexpected missing song: {song_title}")
        
        print(f"\n📊 Final completion results:")
        print(f"  ✅ Successfully completed: {success_count}/{len(missing_songs)} songs")
        
        return success_count

    def validate_final_coverage(self):
        """Validate that we achieved 100% coverage"""
        query = """
        MATCH (s:Song) 
        RETURN count(s) as total_songs, 
               count(s.energy) as with_features,
               (count(s.energy)*100.0/count(s)) as coverage_percent
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            
        total = record['total_songs']
        with_features = record['with_features']
        coverage = record['coverage_percent']
        
        print(f"\n📊 Final Coverage Validation:")
        print(f"  📈 Total songs: {total}")
        print(f"  ✅ Songs with features: {with_features}")
        print(f"  🎯 Coverage: {coverage:.1f}%")
        
        if coverage >= 100.0:
            print("  🎉 SUCCESS: 100% COVERAGE ACHIEVED!")
        else:
            print("  ⚠️ Coverage still incomplete")
        
        return coverage

    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()

def main():
    completer = FinalCompletion()
    
    try:
        # Complete final songs
        success_count = completer.complete_final_songs()
        
        # Validate coverage
        coverage = completer.validate_final_coverage()
        
    finally:
        completer.close()

if __name__ == "__main__":
    main() 