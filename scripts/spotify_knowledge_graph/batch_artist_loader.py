#!/usr/bin/env python3
"""
Batch Artist Loader for Spotify Knowledge Graph
Processes remaining artists from top 100 USA musicians list with priority-based loading
"""

import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Add the spotify_knowledge_builder directory to path
sys.path.append(str(Path(__file__).parent / "spotify_knowledge_builder"))
from spotify_knowledge_builder import SpotifyKnowledgeGraphBuilder

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

class BatchArtistLoader:
    """Batch loader for remaining artists with comprehensive error handling"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.status_file = self.project_root / "scripts" / "top_100_usa_musicians" / "artist_auradb_status_detailed.csv"
        self.processing_log = self.project_root / "scripts" / "spotify_knowledge_graph" / f"batch_processing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.builder = None
        self.processed_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.processing_results = []
        
        print(f"🔧 Batch Artist Loader initialized")
        print(f"📊 Status file: {self.status_file}")
        print(f"📝 Processing log: {self.processing_log}")
    
    def initialize_builder(self) -> bool:
        """Initialize the Spotify Knowledge Graph Builder"""
        try:
            self.builder = SpotifyKnowledgeGraphBuilder()
            print("✅ SpotifyKnowledgeGraphBuilder initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize builder: {e}")
            return False
    
    def load_artist_status(self) -> List[Dict]:
        """Load current artist status from CSV file"""
        artists = []
        
        try:
            with open(self.status_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    artists.append({
                        'rank': int(row['Rank']),
                        'name': row['Artist Name'].strip('"'),
                        'in_auradb': row['In AuraDB'] == 'YES',
                        'status': row['Status'],
                        'reddit_present': row['Reddit Present'] == 'YES',
                        'reddit_score': float(row['Reddit Score']) if row['Reddit Score'] else 0.0,
                        'priority': row['Priority'],
                        'albums': int(row['Albums']) if row['Albums'] else 0,
                        'notes': row['Notes']
                    })
        except Exception as e:
            print(f"❌ Failed to load artist status: {e}")
            return []
        
        print(f"📊 Loaded {len(artists)} artists from status file")
        return artists
    
    def get_missing_artists(self, artists: List[Dict]) -> List[Dict]:
        """Get artists that need to be loaded (missing or incomplete)"""
        missing = []
        incomplete = []
        
        for artist in artists:
            if not artist['in_auradb']:
                missing.append(artist)
            elif artist['status'] == '❌ MISSING' or artist['albums'] == 0:
                incomplete.append(artist)
        
        print(f"📊 Found {len(missing)} missing artists and {len(incomplete)} incomplete artists")
        return missing, incomplete
    
    def prioritize_artists(self, artists: List[Dict]) -> List[Dict]:
        """Sort artists by priority and other factors"""
        def priority_score(artist):
            score = 0
            
            # Priority level scoring
            priority_scores = {
                'HIGH': 1000,
                'MEDIUM': 500,
                'COMPLETE': 100,  # These are the incomplete ones we need to fix
                'INCOMPLETE': 100,
                'LOW': 100
            }
            score += priority_scores.get(artist['priority'], 0)
            
            # Reddit engagement boost
            if artist['reddit_present']:
                score += artist['reddit_score'] * 10
            
            # Rank boost (lower rank number = higher priority)
            score += (101 - artist['rank']) * 5
            
            # Boost for top 20 artists
            if artist['rank'] <= 20:
                score += 500
            
            return score
        
        sorted_artists = sorted(artists, key=priority_score, reverse=True)
        
        print(f"📊 Prioritized artists:")
        for i, artist in enumerate(sorted_artists[:10]):
            print(f"  {i+1}. {artist['name']} (Rank #{artist['rank']}, Priority: {artist['priority']}, Reddit: {artist['reddit_score']})")
        
        return sorted_artists
    
    def process_single_artist(self, artist: Dict) -> Dict:
        """Process a single artist with comprehensive error handling"""
        start_time = time.time()
        artist_name = artist['name']
        
        print(f"\n🎵 Processing: {artist_name} (Rank #{artist['rank']})")
        
        result = {
            'artist_name': artist_name,
            'rank': artist['rank'],
            'start_time': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'processing_time': 0,
            'albums_loaded': 0,
            'tracks_loaded': 0,
            'eras_created': 0
        }
        
        try:
            # Process the artist using the knowledge builder
            processing_result = self.builder.process_artist_with_eras(artist_name)
            
            if processing_result.get('success', False):
                result['success'] = True
                result['albums_loaded'] = processing_result.get('albums_loaded', 0)
                result['tracks_loaded'] = processing_result.get('tracks_loaded', 0)
                result['eras_created'] = processing_result.get('eras_created', 0)
                
                print(f"✅ {artist_name}: {result['albums_loaded']} albums, {result['tracks_loaded']} tracks, {result['eras_created']} eras")
                self.success_count += 1
            else:
                result['error'] = processing_result.get('error', 'Unknown processing error')
                print(f"❌ {artist_name}: {result['error']}")
                self.failure_count += 1
                
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ {artist_name}: Exception - {e}")
            self.failure_count += 1
        
        result['processing_time'] = round(time.time() - start_time, 2)
        result['end_time'] = datetime.now().isoformat()
        
        self.processed_count += 1
        return result
    
    def save_processing_log(self):
        """Save processing results to log file"""
        log_data = {
            'batch_info': {
                'start_time': datetime.now().isoformat(),
                'total_processed': self.processed_count,
                'successful': self.success_count,
                'failed': self.failure_count,
                'success_rate': round((self.success_count / max(self.processed_count, 1)) * 100, 2)
            },
            'results': self.processing_results
        }
        
        try:
            with open(self.processing_log, 'w', encoding='utf-8') as file:
                json.dump(log_data, file, indent=2, ensure_ascii=False)
            print(f"📝 Processing log saved to: {self.processing_log}")
        except Exception as e:
            print(f"❌ Failed to save processing log: {e}")
    
    def process_batch(self, batch_size: int = 20, start_rank: Optional[int] = None, end_rank: Optional[int] = None) -> bool:
        """Process a batch of artists"""
        
        # Initialize builder
        if not self.initialize_builder():
            return False
        
        # Load artist status
        all_artists = self.load_artist_status()
        if not all_artists:
            return False
        
        # Filter by rank range if specified
        if start_rank or end_rank:
            filtered_artists = []
            for artist in all_artists:
                rank = artist['rank']
                if start_rank and rank < start_rank:
                    continue
                if end_rank and rank > end_rank:
                    continue
                filtered_artists.append(artist)
            all_artists = filtered_artists
            print(f"📊 Filtered to ranks {start_rank or 1}-{end_rank or 100}: {len(all_artists)} artists")
        
        # Get missing and incomplete artists
        missing_artists, incomplete_artists = self.get_missing_artists(all_artists)
        
        # Combine and prioritize
        artists_to_process = missing_artists + incomplete_artists
        artists_to_process = self.prioritize_artists(artists_to_process)
        
        # Limit to batch size
        if batch_size and len(artists_to_process) > batch_size:
            artists_to_process = artists_to_process[:batch_size]
            print(f"📊 Limited to batch size: {batch_size} artists")
        
        print(f"\n🚀 Starting batch processing of {len(artists_to_process)} artists")
        print(f"⏰ Estimated time: {len(artists_to_process) * 2} minutes")
        
        # Process each artist
        for i, artist in enumerate(artists_to_process, 1):
            print(f"\n{'='*60}")
            print(f"Processing {i}/{len(artists_to_process)}")
            
            result = self.process_single_artist(artist)
            self.processing_results.append(result)
            
            # Aggressive rate limiting to prevent API limits
            if i < len(artists_to_process):
                print(f"⏳ Rate limiting pause (30 seconds)...")
                time.sleep(30)
            
            # Save progress every 5 artists
            if i % 5 == 0:
                self.save_processing_log()
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"🎯 BATCH PROCESSING COMPLETE")
        print(f"📊 Total processed: {self.processed_count}")
        print(f"✅ Successful: {self.success_count}")
        print(f"❌ Failed: {self.failure_count}")
        print(f"📈 Success rate: {round((self.success_count / max(self.processed_count, 1)) * 100, 2)}%")
        
        # Save final log
        self.save_processing_log()
        
        # Close builder
        if self.builder:
            self.builder.close()
        
        return True
    
    def process_high_priority_only(self) -> bool:
        """Process only HIGH priority artists"""
        print("🎯 Processing HIGH priority artists only")
        
        # Load and filter artists
        all_artists = self.load_artist_status()
        high_priority = [a for a in all_artists if a['priority'] == 'HIGH' and not a['in_auradb']]
        
        if not high_priority:
            print("✅ No HIGH priority artists to process")
            return True
        
        print(f"📊 Found {len(high_priority)} HIGH priority artists to process:")
        for artist in high_priority:
            print(f"  - {artist['name']} (Rank #{artist['rank']}, Reddit: {artist['reddit_score']})")
        
        # Initialize builder
        if not self.initialize_builder():
            return False
        
        # Process each high priority artist
        for i, artist in enumerate(high_priority, 1):
            print(f"\n🎯 HIGH PRIORITY {i}/{len(high_priority)}")
            result = self.process_single_artist(artist)
            self.processing_results.append(result)
            
            if i < len(high_priority):
                time.sleep(5)  # Rate limiting
        
        # Save results
        self.save_processing_log()
        
        if self.builder:
            self.builder.close()
        
        return True

def main():
    """Main execution function"""
    loader = BatchArtistLoader()
    
    print("🎵 Spotify Knowledge Graph - Batch Artist Loader")
    print("=" * 60)
    
    # Menu for different processing options
    print("\nProcessing Options:")
    print("1. Process HIGH priority artists only (recommended first)")
    print("2. Process top 20 artists (ranks 1-20)")
    print("3. Process top 50 artists (ranks 1-50)")
    print("4. Process all remaining artists (ranks 1-100)")
    print("5. Custom rank range")
    print("6. Small test batch (5 artists)")
    
    try:
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            success = loader.process_high_priority_only()
        elif choice == "2":
            success = loader.process_batch(batch_size=None, start_rank=1, end_rank=20)
        elif choice == "3":
            success = loader.process_batch(batch_size=None, start_rank=1, end_rank=50)
        elif choice == "4":
            success = loader.process_batch(batch_size=None, start_rank=1, end_rank=100)
        elif choice == "5":
            start = int(input("Start rank: "))
            end = int(input("End rank: "))
            success = loader.process_batch(batch_size=None, start_rank=start, end_rank=end)
        elif choice == "6":
            success = loader.process_batch(batch_size=5)
        else:
            print("❌ Invalid choice")
            return
        
        if success:
            print("\n🎉 Batch processing completed successfully!")
        else:
            print("\n❌ Batch processing failed")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Processing interrupted by user")
        if loader.processing_results:
            loader.save_processing_log()
            print("📝 Partial results saved to log file")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 