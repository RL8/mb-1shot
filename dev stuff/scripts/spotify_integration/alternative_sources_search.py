import os
import pandas as pd
import json
import numpy as np
from pathlib import Path
import openpyxl
from difflib import SequenceMatcher

class AlternativeSourcesSearcher:
    def __init__(self):
        self.missing_songs = [
            "That's When", "Don't You", "Bye Bye Baby", '"Slut!"', 
            "Say Don't Go", "Sweeter Than Fiction", "Better Man", 
            "Nothing New", "Babe", "Run", "Foolish One", "Timeless"
        ]
        
        self.archive_path = "C:\\Users\\Bravo\\CascadeProjects\\mb-1shot-archive\\taylor"
        self.data_sources = []
        self.results = []
        
    def similarity(self, a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def normalize_title(self, title):
        """Normalize song title for comparison"""
        if not title:
            return ""
        # Remove common variations
        normalized = str(title).lower()
        normalized = normalized.replace("(taylor's version)", "")
        normalized = normalized.replace("(from the vault)", "")
        normalized = normalized.replace("(feat.", "")
        normalized = normalized.replace("'", "'")  # Normalize apostrophes
        normalized = normalized.replace('"', "'")  # Normalize quotes
        normalized = normalized.strip()
        return normalized
    
    def search_csv_files(self):
        """Search all CSV files in the archive"""
        print("🔍 Searching CSV files...")
        
        csv_files = list(Path(self.archive_path).glob("**/*.csv"))
        
        for csv_file in csv_files:
            try:
                print(f"  📄 Checking: {csv_file.name}")
                df = pd.read_csv(csv_file)
                
                # Look for track name columns
                track_columns = [col for col in df.columns if 
                               'track' in col.lower() or 'song' in col.lower() or 'title' in col.lower()]
                
                if track_columns:
                    for track_col in track_columns:
                        for missing_song in self.missing_songs:
                            normalized_missing = self.normalize_title(missing_song)
                            
                            for idx, row in df.iterrows():
                                track_name = str(row.get(track_col, ""))
                                normalized_track = self.normalize_title(track_name)
                                
                                similarity_score = self.similarity(normalized_missing, normalized_track)
                                
                                if similarity_score > 0.7:  # 70% similarity threshold
                                    result = {
                                        'missing_song': missing_song,
                                        'found_track': track_name,
                                        'similarity': similarity_score,
                                        'source_file': csv_file.name,
                                        'source_type': 'CSV',
                                        'row_data': dict(row)
                                    }
                                    self.results.append(result)
                                    print(f"    ✅ Found match: {missing_song} ≈ {track_name} ({similarity_score:.1%})")
                                    
            except Exception as e:
                print(f"    ❌ Error reading {csv_file.name}: {e}")
    
    def search_excel_files(self):
        """Search all Excel files in the archive"""
        print("\n🔍 Searching Excel files...")
        
        xlsx_files = list(Path(self.archive_path).glob("**/*.xlsx"))
        
        for xlsx_file in xlsx_files:
            try:
                print(f"  📄 Checking: {xlsx_file.name}")
                
                # Read all sheets
                xl_file = pd.ExcelFile(xlsx_file)
                
                for sheet_name in xl_file.sheet_names:
                    df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
                    
                    # Look for track name columns
                    track_columns = [col for col in df.columns if 
                                   'track' in col.lower() or 'song' in col.lower() or 'title' in col.lower()]
                    
                    if track_columns:
                        print(f"    📊 Checking sheet: {sheet_name}")
                        
                        for track_col in track_columns:
                            for missing_song in self.missing_songs:
                                normalized_missing = self.normalize_title(missing_song)
                                
                                for idx, row in df.iterrows():
                                    track_name = str(row.get(track_col, ""))
                                    normalized_track = self.normalize_title(track_name)
                                    
                                    similarity_score = self.similarity(normalized_missing, normalized_track)
                                    
                                    if similarity_score > 0.7:  # 70% similarity threshold
                                        result = {
                                            'missing_song': missing_song,
                                            'found_track': track_name,
                                            'similarity': similarity_score,
                                            'source_file': f"{xlsx_file.name}:{sheet_name}",
                                            'source_type': 'Excel',
                                            'row_data': dict(row)
                                        }
                                        self.results.append(result)
                                        print(f"      ✅ Found match: {missing_song} ≈ {track_name} ({similarity_score:.1%})")
                                        
            except Exception as e:
                print(f"    ❌ Error reading {xlsx_file.name}: {e}")
    
    def search_json_files(self):
        """Search all JSON files in the archive"""
        print("\n🔍 Searching JSON files...")
        
        json_files = list(Path(self.archive_path).glob("**/*.json"))
        
        for json_file in json_files:
            try:
                print(f"  📄 Checking: {json_file.name}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Recursive search through JSON structure
                self._search_json_recursive(data, json_file.name, [])
                
            except Exception as e:
                print(f"    ❌ Error reading {json_file.name}: {e}")
    
    def _search_json_recursive(self, data, filename, path):
        """Recursively search through JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = path + [key]
                
                # Check if this might be a track name
                if any(keyword in key.lower() for keyword in ['track', 'song', 'title', 'name']):
                    if isinstance(value, str):
                        self._check_json_track(value, filename, current_path)
                
                # Recurse into nested structures
                self._search_json_recursive(value, filename, current_path)
                
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                current_path = path + [f"[{idx}]"]
                self._search_json_recursive(item, filename, current_path)
    
    def _check_json_track(self, track_name, filename, path):
        """Check if a JSON track name matches any missing songs"""
        for missing_song in self.missing_songs:
            normalized_missing = self.normalize_title(missing_song)
            normalized_track = self.normalize_title(track_name)
            
            similarity_score = self.similarity(normalized_missing, normalized_track)
            
            if similarity_score > 0.7:  # 70% similarity threshold
                result = {
                    'missing_song': missing_song,
                    'found_track': track_name,
                    'similarity': similarity_score,
                    'source_file': filename,
                    'source_type': 'JSON',
                    'json_path': ' -> '.join(path)
                }
                self.results.append(result)
                print(f"    ✅ Found match: {missing_song} ≈ {track_name} ({similarity_score:.1%})")
    
    def search_detailed_spotify_csv(self):
        """Detailed search of the main Spotify CSV with fuzzy matching"""
        print("\n🔍 Detailed Spotify CSV search with fuzzy matching...")
        
        csv_path = os.path.join(self.archive_path, "data-raw", "spotify-data.csv")
        
        if not os.path.exists(csv_path):
            print("  ❌ Spotify CSV not found")
            return
        
        df = pd.read_csv(csv_path)
        print(f"  📊 Loaded {len(df)} tracks from spotify-data.csv")
        
        # Enhanced search with multiple variations
        for missing_song in self.missing_songs:
            print(f"\n  🎵 Searching for: {missing_song}")
            
            # Try different variations
            variations = [
                missing_song,
                missing_song.replace('"', ''),  # Remove quotes
                missing_song.replace("'", "'"),  # Different apostrophe
                missing_song + " (Taylor's Version)",
                missing_song + " (From The Vault)",
                missing_song + " (Taylor's Version) (From The Vault)"
            ]
            
            best_match = None
            best_similarity = 0
            
            for variation in variations:
                normalized_variation = self.normalize_title(variation)
                
                for idx, row in df.iterrows():
                    track_name = str(row.get('track_name', ''))
                    normalized_track = self.normalize_title(track_name)
                    
                    similarity_score = self.similarity(normalized_variation, normalized_track)
                    
                    if similarity_score > best_similarity:
                        best_similarity = similarity_score
                        best_match = {
                            'missing_song': missing_song,
                            'found_track': track_name,
                            'similarity': similarity_score,
                            'source_file': 'spotify-data.csv',
                            'source_type': 'CSV_detailed',
                            'row_data': dict(row),
                            'variation_used': variation
                        }
            
            if best_match and best_similarity > 0.5:  # Lower threshold for detailed search
                self.results.append(best_match)
                print(f"    ✅ Best match: {missing_song} ≈ {best_match['found_track']} ({best_similarity:.1%})")
                
                # Show audio features if available
                row_data = best_match['row_data']
                if 'energy' in row_data and pd.notna(row_data['energy']):
                    print(f"      🎼 Audio features available: energy={row_data['energy']}, valence={row_data.get('valence', 'N/A')}")
            else:
                print(f"    ❌ No good matches found (best: {best_similarity:.1%})")
    
    def generate_report(self):
        """Generate a comprehensive report of findings"""
        print("\n" + "="*80)
        print("📊 ALTERNATIVE SOURCES SEARCH REPORT")
        print("="*80)
        
        if not self.results:
            print("❌ No matches found in alternative sources")
            return
        
        # Group results by missing song
        by_song = {}
        for result in self.results:
            song = result['missing_song']
            if song not in by_song:
                by_song[song] = []
            by_song[song].append(result)
        
        for song, matches in by_song.items():
            print(f"\n🎵 {song}:")
            
            # Sort matches by similarity score
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            for match in matches:
                print(f"  ✅ {match['found_track']} ({match['similarity']:.1%} similarity)")
                print(f"     📁 Source: {match['source_file']} ({match['source_type']})")
                
                # Show audio features if available
                if 'row_data' in match:
                    row = match['row_data']
                    features = []
                    for feature in ['energy', 'valence', 'danceability', 'acousticness', 'instrumentalness']:
                        if feature in row and pd.notna(row[feature]):
                            features.append(f"{feature}={row[feature]}")
                    
                    if features:
                        print(f"     🎼 Features: {', '.join(features)}")
                print()
        
        # Summary
        print(f"📈 SUMMARY:")
        print(f"  🔍 Missing songs searched: {len(self.missing_songs)}")
        print(f"  ✅ Songs with potential matches: {len(by_song)}")
        print(f"  📊 Total matches found: {len(self.results)}")
        
        # Songs still missing
        found_songs = set(by_song.keys())
        still_missing = set(self.missing_songs) - found_songs
        
        if still_missing:
            print(f"\n❌ Songs still without matches:")
            for song in still_missing:
                print(f"  🎵 {song}")
    
    def run_comprehensive_search(self):
        """Run all search methods"""
        print("🚀 Starting comprehensive alternative sources search...")
        print(f"📁 Archive path: {self.archive_path}")
        print(f"🎵 Searching for {len(self.missing_songs)} missing songs")
        
        # Search all data sources
        self.search_detailed_spotify_csv()  # Most important first
        self.search_excel_files()
        self.search_json_files()
        self.search_csv_files()  # This will catch any other CSVs
        
        # Generate comprehensive report
        self.generate_report()

def main():
    searcher = AlternativeSourcesSearcher()
    searcher.run_comprehensive_search()

if __name__ == "__main__":
    main() 