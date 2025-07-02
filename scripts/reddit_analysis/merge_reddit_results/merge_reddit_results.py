#!/usr/bin/env python3
"""
Merge Reddit Results

Combines the original run (artists 1-44) with batch results (45-70, 71-100)
to create the final comprehensive sorted JSON file.
"""

import json
import datetime
from pathlib import Path

# Load environment
project_root = Path(__file__).parent.parent.parent
OUTPUT_DIR = project_root / "dev stuff" / "data-scripts" / "reddit_results"

def load_json_file(filename):
    """Load a JSON file and return its contents."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        print(f"❌ File not found: {filename}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Merge all Reddit analysis results."""
    print("🔗 MERGING REDDIT ANALYSIS RESULTS")
    print("=" * 60)
    
    # Find the most recent files
    original_files = list(OUTPUT_DIR.glob("top100_usa_musicians_reddit_scores_*.json"))
    batch_45_70_files = list(OUTPUT_DIR.glob("batch_45-70_*.json"))
    batch_71_100_files = list(OUTPUT_DIR.glob("batch_71-100_*.json"))
    
    if not original_files:
        print("❌ No original results file found")
        return
    
    if not batch_45_70_files:
        print("❌ No batch 45-70 results file found")
        return
        
    if not batch_71_100_files:
        print("❌ No batch 71-100 results file found")
        return
    
    # Get the most recent files
    original_file = max(original_files, key=lambda x: x.stat().st_mtime)
    batch_45_70_file = max(batch_45_70_files, key=lambda x: x.stat().st_mtime)
    batch_71_100_file = max(batch_71_100_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📄 Original results: {original_file.name}")
    print(f"📄 Batch 45-70: {batch_45_70_file.name}")
    print(f"📄 Batch 71-100: {batch_71_100_file.name}")
    
    # Load all files
    original_data = load_json_file(original_file.name)
    batch_45_70_data = load_json_file(batch_45_70_file.name)
    batch_71_100_data = load_json_file(batch_71_100_file.name)
    
    if not all([original_data, batch_45_70_data, batch_71_100_data]):
        print("❌ Failed to load one or more files")
        return
    
    # Extract artist scores from each source (handle different key names)
    original_scores = original_data.get("artist_scores", []) or original_data.get("artists_sorted_by_score", [])
    batch_45_70_scores = batch_45_70_data.get("artists_sorted_by_score", [])
    batch_71_100_scores = batch_71_100_data.get("artists_sorted_by_score", [])
    
    print(f"\n📊 Loaded data:")
    print(f"   • Original (1-44): {len(original_scores)} artists")
    print(f"   • Batch 45-70: {len(batch_45_70_scores)} artists")
    print(f"   • Batch 71-100: {len(batch_71_100_scores)} artists")
    
    # Combine all results
    all_artists = []
    all_artists.extend(original_scores)
    all_artists.extend(batch_45_70_scores)
    all_artists.extend(batch_71_100_scores)
    
    # Sort by popularity score (descending)
    all_artists.sort(key=lambda x: x["popularity_score"], reverse=True)
    
    # Calculate statistics
    total_artists = len(all_artists)
    with_presence = sum(1 for a in all_artists if a["popularity_score"] > 0)
    without_presence = total_artists - with_presence
    
    # Count tiers
    tier_counts = {}
    for artist in all_artists:
        tier = artist["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    # Create final merged results
    merged_results = {
        "analysis_date": datetime.datetime.now().isoformat(),
        "methodology": "Single Primary Subreddit - Engagement Density",
        "data_sources": {
            "original_run": f"Artists 1-44 from {original_file.name}",
            "batch_45_70": f"Artists 45-70 from {batch_45_70_file.name}",
            "batch_71_100": f"Artists 71-100 from {batch_71_100_file.name}"
        },
        "summary": {
            "total_artists_analyzed": total_artists,
            "artists_with_reddit_presence": with_presence,
            "artists_without_presence": without_presence,
            "tier_distribution": tier_counts
        },
        "scoring_criteria": {
            "min_subscribers": 50000,
            "min_relevance_score": 8,
            "activity_period": "30 days",
            "score_formula": "(Monthly Activity ÷ Subscribers) × 1000"
        },
        "artists_sorted_by_score": all_artists
    }
    
    # Save merged results
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    merged_file = OUTPUT_DIR / f"complete_top100_reddit_scores_{timestamp}.json"
    
    with open(merged_file, 'w', encoding='utf-8') as f:
        json.dump(merged_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ MERGE COMPLETE")
    print(f"📄 Saved: {merged_file}")
    
    # Print comprehensive summary
    print(f"\n🎯 FINAL COMPREHENSIVE RESULTS")
    print("=" * 60)
    print(f"📊 Total Artists: {total_artists}")
    print(f"✅ With Reddit Presence: {with_presence}")
    print(f"❌ Without Presence: {without_presence}")
    
    print(f"\n📈 Tier Distribution:")
    for tier, count in tier_counts.items():
        print(f"   • {tier}: {count} artists")
    
    print(f"\n🏆 TOP 15 ARTISTS BY REDDIT ENGAGEMENT:")
    print("-" * 60)
    for i, artist in enumerate(all_artists[:15], 1):
        if artist['popularity_score'] > 0:
            print(f"   {i:2d}. {artist['artist']:20} {artist['popularity_score']:8.2f} ({artist['tier']})")
    
    print(f"\n🎵 Complete dataset ready for Music Besties integration!")

if __name__ == "__main__":
    main() 