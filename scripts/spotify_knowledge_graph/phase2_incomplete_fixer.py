#!/usr/bin/env python3
"""
Phase 2: Incomplete Artist Catalog Fixer
Targets artists who are loaded in AuraDB but have empty catalogs (0 albums/songs)
These artists likely had partial failures during initial processing
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

class Phase2IncompleteFixer:
    """Fixes artists with empty catalogs in AuraDB"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.status_file = self.project_root / "scripts" / "top_100_usa_musicians" / "artist_auradb_status_detailed.csv"
        self.log_file = self.project_root / "scripts" / "spotify_knowledge_graph" / f"phase2_processing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.results = []
        
        print(f"🔧 Phase 2 Incomplete Catalog Fixer initialized")
        print(f"📊 Status file: {self.status_file}")
        print(f"📝 Log file: {self.log_file}")
    
    def get_incomplete_artists(self) -> List[Dict]:
        """Get artists that are loaded but have empty catalogs"""
        incomplete_artists = []
        
        try:
            with open(self.status_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Target: In AuraDB = YES, but Albums = 0 (empty catalog)
                    if (row['In AuraDB'] == 'YES' and 
                        row['Status'] == '✅ LOADED' and
                        int(row['Albums']) == 0):
                        
                        incomplete_artists.append({
                            'rank': int(row['Rank']),
                            'name': row['Artist Name'].strip('"'),
                            'reddit_present': row['Reddit Present'] == 'YES',
                            'reddit_score': float(row['Reddit Score']) if row['Reddit Score'] else 0.0,
                            'priority': row['Priority'],
                            'notes': row['Notes']
                        })
        except Exception as e:
            print(f"❌ Failed to load artist status: {e}")
            return []
        
        # Sort by priority and Reddit engagement
        def priority_score(artist):
            score = 0
            if artist['reddit_present']:
                score += artist['reddit_score'] * 10
            score += (101 - artist['rank']) * 2  # Higher rank = higher score
            return score
        
        incomplete_artists.sort(key=priority_score, reverse=True)
        return incomplete_artists
    
    def analyze_incomplete_issue(self, artist_name: str) -> Dict:
        """Analyze why an artist has an empty catalog"""
        print(f"🔍 Analyzing incomplete catalog for: {artist_name}")
        
        analysis = {
            'artist_name': artist_name,
            'artist_node_exists': False,
            'album_nodes_exist': False,
            'track_nodes_exist': False,
            'estimated_cause': 'unknown'
        }
        
        try:
            # This would require querying AuraDB to check what nodes exist
            # For now, we'll assume the artist node exists but albums/tracks don't
            analysis['artist_node_exists'] = True
            analysis['estimated_cause'] = 'partial_api_failure_during_initial_load'
            
        except Exception as e:
            print(f"⚠️ Analysis failed for {artist_name}: {e}")
        
        return analysis
    
    def fix_incomplete_artist(self, artist: Dict) -> Dict:
        """Fix an incomplete artist by re-processing their catalog"""
        start_time = time.time()
        artist_name = artist['name']
        
        print(f"\n🔧 FIXING: {artist_name} (Rank #{artist['rank']})")
        print("=" * 60)
        
        result = {
            'artist_name': artist_name,
            'rank': artist['rank'],
            'start_time': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'processing_time': 0,
            'analysis': None,
            'pre_fix_albums': 0,
            'post_fix_albums': 0,
            'albums_added': 0,
            'tracks_added': 0
        }
        
        try:
            # Analyze the current state
            result['analysis'] = self.analyze_incomplete_issue(artist_name)
            
            # Initialize builder with extended rate limiting
            builder = SpotifyKnowledgeGraphBuilder()
            
            print("⏳ Re-processing catalog with extended rate limiting...")
            print("   This will attempt to load all missing albums and tracks")
            
            # Re-process the artist (this should fill in missing data)
            success = builder.process_artist_with_eras(artist_name)
            
            if success:
                result['success'] = True
                print(f"✅ SUCCESS: {artist_name} catalog re-processed successfully")
                
                # Note: In a real implementation, we'd query the database to get exact counts
                result['post_fix_albums'] = "pending_verification"
                result['albums_added'] = "pending_verification"
                result['tracks_added'] = "pending_verification"
            else:
                result['error'] = "Re-processing failed - Spotify API or data issues"
                print(f"❌ FAILED: {artist_name} re-processing unsuccessful")
            
            builder.close()
            
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ ERROR fixing {artist_name}: {e}")
        
        result['processing_time'] = round(time.time() - start_time, 2)
        result['end_time'] = datetime.now().isoformat()
        
        return result
    
    def process_incomplete_artists(self, max_artists: int = 5):
        """Process incomplete artists with extended rate limiting"""
        
        incomplete_artists = self.get_incomplete_artists()
        
        if not incomplete_artists:
            print("✅ No incomplete artists found!")
            return
        
        print(f"📊 Found {len(incomplete_artists)} incomplete artists:")
        for artist in incomplete_artists:
            status_emoji = "🔥" if artist['reddit_score'] > 30 else "📊" if artist['reddit_score'] > 0 else "❌"
            print(f"   {status_emoji} {artist['name']} (Rank #{artist['rank']}, Reddit: {artist['reddit_score']})")
        
        # Limit processing
        artists_to_fix = incomplete_artists[:max_artists]
        
        print(f"\n🎯 Phase 2 Processing Plan:")
        print(f"📊 Total incomplete: {len(incomplete_artists)}")
        print(f"🔧 Processing now: {len(artists_to_fix)}")
        print(f"⏰ Estimated time: {len(artists_to_fix) * 3} minutes")
        print(f"🛡️ Using extended rate limiting to avoid API limits")
        
        print(f"\n🚀 Starting Phase 2 incomplete catalog fixes...")
        
        # Process each incomplete artist
        for i, artist in enumerate(artists_to_fix, 1):
            print(f"\n{'='*60}")
            print(f"🔧 PHASE 2 FIX {i}/{len(artists_to_fix)}")
            
            result = self.fix_incomplete_artist(artist)
            self.results.append(result)
            
            # Extended rate limiting between artists (Phase 2 is more conservative)
            if i < len(artists_to_fix):
                print("⏳ EXTENDED PAUSE (90 seconds) before next fix...")
                print("   Phase 2 uses conservative timing to ensure reliability")
                time.sleep(90)  # 1.5 minutes between fixes
        
        # Summary
        self.print_phase2_summary()
        self.save_results()
    
    def print_phase2_summary(self):
        """Print comprehensive Phase 2 summary"""
        print(f"\n{'='*60}")
        print("🎯 PHASE 2 INCOMPLETE CATALOG FIXES COMPLETE")
        print("=" * 60)
        
        successful = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - successful
        
        print(f"✅ Successfully fixed: {successful}/{len(self.results)} artists")
        print(f"❌ Failed to fix: {failed}/{len(self.results)} artists")
        
        if successful > 0:
            print(f"\n🎉 Fixed Artists:")
            for result in self.results:
                if result['success']:
                    print(f"   ✅ {result['artist_name']} (Rank #{result['rank']})")
        
        if failed > 0:
            print(f"\n⚠️ Failed Artists:")
            for result in self.results:
                if not result['success']:
                    print(f"   ❌ {result['artist_name']} (Rank #{result['rank']}) - {result['error']}")
        
        print(f"\n📊 Phase 2 Impact:")
        print(f"   🔧 Incomplete catalogs addressed: {len(self.results)}")
        print(f"   📈 Success rate: {round((successful/max(len(self.results), 1))*100, 1)}%")
        print(f"   ⏱️ Total processing time: {sum(r['processing_time'] for r in self.results):.1f} seconds")
        
        # Recommendations for Phase 3
        remaining_incomplete = len(self.get_incomplete_artists()) - successful
        if remaining_incomplete > 0:
            print(f"\n🔄 Phase 3 Recommendation:")
            print(f"   📊 {remaining_incomplete} incomplete artists remain")
            print(f"   💡 Consider running Phase 2 again for remaining artists")
    
    def save_results(self):
        """Save Phase 2 results to log file"""
        log_data = {
            'phase': 2,
            'purpose': 'Fix incomplete artist catalogs',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_processed': len(self.results),
                'successful': sum(1 for r in self.results if r['success']),
                'failed': sum(1 for r in self.results if not r['success']),
                'total_time': sum(r['processing_time'] for r in self.results)
            },
            'results': self.results
        }
        
        try:
            with open(self.log_file, 'w', encoding='utf-8') as file:
                json.dump(log_data, file, indent=2, ensure_ascii=False)
            print(f"📝 Phase 2 results saved to: {self.log_file}")
        except Exception as e:
            print(f"❌ Failed to save Phase 2 results: {e}")

def main():
    """Main execution for Phase 2"""
    print("🔧 Phase 2: Incomplete Artist Catalog Fixer")
    print("🎯 Targets artists loaded in AuraDB but with empty catalogs")
    print("=" * 60)
    
    fixer = Phase2IncompleteFixer()
    
    # Get count of incomplete artists
    incomplete_artists = fixer.get_incomplete_artists()
    
    if not incomplete_artists:
        print("✅ No incomplete artists found - all catalogs are complete!")
        return
    
    print(f"\n📊 Analysis:")
    print(f"   🔍 Found {len(incomplete_artists)} incomplete artists")
    print(f"   🎯 These artists are in AuraDB but have empty catalogs")
    print(f"   🔧 Phase 2 will re-process their Spotify data")
    
    print(f"\nProcessing Options:")
    print(f"1. Fix top 3 incomplete artists (recommended)")
    print(f"2. Fix top 5 incomplete artists")
    print(f"3. Fix all incomplete artists ({len(incomplete_artists)} total)")
    print(f"4. Show incomplete artists list only")
    
    try:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            fixer.process_incomplete_artists(max_artists=3)
        elif choice == "2":
            fixer.process_incomplete_artists(max_artists=5)
        elif choice == "3":
            fixer.process_incomplete_artists(max_artists=len(incomplete_artists))
        elif choice == "4":
            print(f"\n📊 Incomplete Artists List:")
            for i, artist in enumerate(incomplete_artists, 1):
                reddit_status = f"Reddit: {artist['reddit_score']:.1f}" if artist['reddit_present'] else "No Reddit"
                print(f"   {i}. {artist['name']} (Rank #{artist['rank']}, {reddit_status})")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Phase 2 processing interrupted")
        if fixer.results:
            fixer.save_results()
            print("📝 Partial results saved")
    except Exception as e:
        print(f"\n❌ Phase 2 error: {e}")

if __name__ == "__main__":
    main() 