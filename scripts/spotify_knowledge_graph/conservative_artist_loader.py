#!/usr/bin/env python3
"""
Conservative Artist Loader - Process 1-3 artists with aggressive rate limiting
Safe approach to avoid Spotify API rate limits
"""

import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add the spotify_knowledge_builder directory to path
sys.path.append(str(Path(__file__).parent / "spotify_knowledge_builder"))
from spotify_knowledge_builder import SpotifyKnowledgeGraphBuilder

class ConservativeArtistLoader:
    """Ultra-conservative loader to avoid rate limits"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.status_file = self.project_root / "scripts" / "top_100_usa_musicians" / "artist_auradb_status_detailed.csv"
        
    def get_high_priority_missing(self) -> List[Dict]:
        """Get only HIGH priority missing artists"""
        artists = []
        
        try:
            with open(self.status_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if (row['Priority'] == 'HIGH' and 
                        row['In AuraDB'] == 'NO'):
                        artists.append({
                            'rank': int(row['Rank']),
                            'name': row['Artist Name'].strip('"'),
                            'reddit_score': float(row['Reddit Score']) if row['Reddit Score'] else 0.0,
                        })
        except Exception as e:
            print(f"❌ Failed to load artist status: {e}")
            return []
        
        # Sort by rank (higher priority first)
        artists.sort(key=lambda x: x['rank'])
        return artists
    
    def process_single_artist_safely(self, artist: Dict):
        """Process one artist with maximum safety"""
        print(f"\n🎵 SAFELY Processing: {artist['name']} (Rank #{artist['rank']})")
        print("=" * 60)
        
        try:
            builder = SpotifyKnowledgeGraphBuilder()
            
            print("⏳ Starting processing with extended rate limiting...")
            success = builder.process_artist_with_eras(artist['name'])
            
            if success:
                print(f"✅ SUCCESS: {artist['name']} processed successfully")
            else:
                print(f"❌ FAILED: {artist['name']} could not be processed")
            
            builder.close()
            return success
            
        except Exception as e:
            print(f"❌ ERROR processing {artist['name']}: {e}")
            return False
    
    def process_top_3_priority(self):
        """Process only the top 3 HIGH priority artists"""
        print("🎯 Conservative Processing: Top 3 HIGH Priority Artists")
        print("=" * 60)
        
        high_priority = self.get_high_priority_missing()
        
        if not high_priority:
            print("✅ No HIGH priority artists to process")
            return
        
        # Limit to top 3
        artists_to_process = high_priority[:3]
        
        print(f"📊 Found {len(high_priority)} HIGH priority artists")
        print(f"🎯 Processing only top 3 to avoid rate limits:")
        for artist in artists_to_process:
            print(f"   - {artist['name']} (Rank #{artist['rank']}, Reddit: {artist['reddit_score']})")
        
        print(f"\n⏰ Estimated time: {len(artists_to_process) * 5} minutes")
        print("⚠️  Using CONSERVATIVE rate limiting to prevent API limits")
        
        results = []
        for i, artist in enumerate(artists_to_process, 1):
            print(f"\n{'='*60}")
            print(f"🎯 Processing {i}/{len(artists_to_process)}")
            
            success = self.process_single_artist_safely(artist)
            results.append({'artist': artist['name'], 'success': success})
            
            # VERY conservative rate limiting between artists
            if i < len(artists_to_process):
                print("⏳ EXTENDED PAUSE (2 minutes) before next artist...")
                print("   This prevents Spotify API rate limits")
                time.sleep(120)  # 2 minutes between artists
        
        # Summary
        print(f"\n{'='*60}")
        print("🎯 CONSERVATIVE PROCESSING COMPLETE")
        print("=" * 60)
        
        successful = sum(1 for r in results if r['success'])
        print(f"✅ Successful: {successful}/{len(results)} artists")
        print(f"📊 Results:")
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['artist']}")

def main():
    """Main execution"""
    print("🎵 Conservative Spotify Artist Loader")
    print("🛡️  Designed to avoid rate limits")
    print("=" * 60)
    
    loader = ConservativeArtistLoader()
    
    print("\nThis will process only 3 HIGH priority artists with:")
    print("• 2-minute pauses between artists")
    print("• Extended rate limiting within processing")
    print("• Maximum safety to avoid API limits")
    
    response = input("\nProceed? (y/n): ").strip().lower()
    
    if response == 'y':
        loader.process_top_3_priority()
    else:
        print("❌ Processing cancelled")

if __name__ == "__main__":
    main() 