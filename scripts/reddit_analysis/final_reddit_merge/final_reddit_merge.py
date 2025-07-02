#!/usr/bin/env python3
"""
Final Reddit Merge

Creates the definitive Top 100 USA Musicians Reddit Analysis by:
- Using original results for artists 1-44
- Using batch results for artists 45-100
- Properly deduplicating and ordering
"""

import json
import datetime
from pathlib import Path

# Load environment
project_root = Path(__file__).parent.parent.parent
OUTPUT_DIR = project_root / "dev stuff" / "data-scripts" / "reddit_results"

def load_artist_list():
    """Load the original artist order from file."""
    artists_file = project_root / "top_100_usa_musicians_names_only.txt"
    
    artists = []
    with open(artists_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and line[0].isdigit():
                # Extract just the artist name
                parts = line.split('.', 1)
                if len(parts) > 1:
                    artist_name = parts[1].strip()
                    artists.append(artist_name)
    
    return artists

def load_json_file(filename):
    """Load a JSON file and return its contents."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        print(f"❌ File not found: {filename}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Create the final definitive Reddit analysis."""
    print("🎯 FINAL REDDIT ANALYSIS - TOP 100 USA MUSICIANS")
    print("=" * 70)
    
    # Load the original artist order
    ordered_artists = load_artist_list()
    print(f"📋 Loaded original order: {len(ordered_artists)} artists")
    
    # Find the most recent files
    original_files = list(OUTPUT_DIR.glob("top100_usa_musicians_reddit_scores_*.json"))
    batch_45_70_files = list(OUTPUT_DIR.glob("batch_45-70_*.json"))
    batch_71_100_files = list(OUTPUT_DIR.glob("batch_71-100_*.json"))
    
    if not all([original_files, batch_45_70_files, batch_71_100_files]):
        print("❌ Missing required files")
        return
    
    # Get the most recent files
    original_file = max(original_files, key=lambda x: x.stat().st_mtime)
    batch_45_70_file = max(batch_45_70_files, key=lambda x: x.stat().st_mtime)
    batch_71_100_file = max(batch_71_100_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📄 Loading from:")
    print(f"   • Original: {original_file.name}")
    print(f"   • Batch 45-70: {batch_45_70_file.name}")
    print(f"   • Batch 71-100: {batch_71_100_file.name}")
    
    # Load all files
    original_data = load_json_file(original_file.name)
    batch_45_70_data = load_json_file(batch_45_70_file.name)
    batch_71_100_data = load_json_file(batch_71_100_file.name)
    
    if not all([original_data, batch_45_70_data, batch_71_100_data]):
        return
    
    # Create artist lookup dictionaries
    original_scores = original_data.get("artist_scores", [])
    batch_45_70_scores = batch_45_70_data.get("artists_sorted_by_score", [])
    batch_71_100_scores = batch_71_100_data.get("artists_sorted_by_score", [])
    
    # Create lookup by artist name
    original_lookup = {artist["artist"]: artist for artist in original_scores}
    batch_45_70_lookup = {artist["artist"]: artist for artist in batch_45_70_scores}
    batch_71_100_lookup = {artist["artist"]: artist for artist in batch_71_100_scores}
    
    print(f"\n📊 Data loaded:")
    print(f"   • Original data: {len(original_lookup)} artists")
    print(f"   • Batch 45-70: {len(batch_45_70_lookup)} artists")
    print(f"   • Batch 71-100: {len(batch_71_100_lookup)} artists")
    
    # Build final results in correct order
    final_results = []
    
    for i, artist_name in enumerate(ordered_artists, 1):
        if i <= 44:
            # Use original results for 1-44
            if artist_name in original_lookup:
                final_results.append(original_lookup[artist_name])
            else:
                # Create placeholder for missing artist
                final_results.append({
                    "artist": artist_name,
                    "primary_subreddit": None,
                    "subreddit_url": None,
                    "subscribers": 0,
                    "posts_last_month": 0,
                    "comments_last_month": 0,
                    "total_activity": 0,
                    "popularity_score": 0.0,
                    "tier": "❌ No Presence",
                    "relevance_score": 0,
                    "relevance_reasons": "No qualifying subreddit found"
                })
        elif 45 <= i <= 70:
            # Use batch 45-70 results
            if artist_name in batch_45_70_lookup:
                final_results.append(batch_45_70_lookup[artist_name])
            else:
                final_results.append({
                    "artist": artist_name,
                    "primary_subreddit": None,
                    "subreddit_url": None,
                    "subscribers": 0,
                    "posts_last_month": 0,
                    "comments_last_month": 0,
                    "total_activity": 0,
                    "popularity_score": 0.0,
                    "tier": "❌ No Presence",
                    "relevance_score": 0,
                    "relevance_reasons": "No qualifying subreddit found"
                })
        else:  # 71-100
            # Use batch 71-100 results
            if artist_name in batch_71_100_lookup:
                final_results.append(batch_71_100_lookup[artist_name])
            else:
                final_results.append({
                    "artist": artist_name,
                    "primary_subreddit": None,
                    "subreddit_url": None,
                    "subscribers": 0,
                    "posts_last_month": 0,
                    "comments_last_month": 0,
                    "total_activity": 0,
                    "popularity_score": 0.0,
                    "tier": "❌ No Presence",
                    "relevance_score": 0,
                    "relevance_reasons": "No qualifying subreddit found"
                })
    
    # Create sorted version for popularity ranking
    sorted_results = sorted([a for a in final_results if a["popularity_score"] > 0], 
                          key=lambda x: x["popularity_score"], reverse=True)
    
    # Calculate statistics
    total_artists = len(final_results)
    with_presence = sum(1 for a in final_results if a["popularity_score"] > 0)
    without_presence = total_artists - with_presence
    
    # Count tiers
    tier_counts = {}
    for artist in final_results:
        tier = artist["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    # Create final output
    final_output = {
        "analysis_date": datetime.datetime.now().isoformat(),
        "methodology": "Single Primary Subreddit - Engagement Density",
        "data_sources": {
            "artists_1_44": f"Original run from {original_file.name}",
            "artists_45_70": f"Batch run from {batch_45_70_file.name}",
            "artists_71_100": f"Batch run from {batch_71_100_file.name}"
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
        "artists_in_original_order": final_results,
        "artists_sorted_by_popularity": sorted_results
    }
    
    # Save final results
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    final_file = OUTPUT_DIR / f"FINAL_top100_reddit_analysis_{timestamp}.json"
    
    with open(final_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ FINAL ANALYSIS COMPLETE")
    print(f"📄 Saved: {final_file}")
    
    # Print comprehensive summary
    print(f"\n🎯 DEFINITIVE TOP 100 USA MUSICIANS REDDIT ANALYSIS")
    print("=" * 70)
    print(f"📊 Total Artists: {total_artists}")
    print(f"✅ With Reddit Presence: {with_presence}")
    print(f"❌ Without Presence: {without_presence}")
    print(f"📈 Coverage: {(with_presence/total_artists)*100:.1f}%")
    
    print(f"\n📈 Tier Distribution:")
    for tier, count in tier_counts.items():
        print(f"   • {tier}: {count} artists")
    
    print(f"\n🏆 TOP 20 ARTISTS BY REDDIT ENGAGEMENT:")
    print("-" * 70)
    for i, artist in enumerate(sorted_results[:20], 1):
        subreddit = artist['primary_subreddit'] or 'N/A'
        print(f"   {i:2d}. {artist['artist']:25} {artist['popularity_score']:8.2f} ({artist['tier']})")
        print(f"       └── r/{subreddit} • {artist['subscribers']:,} subscribers")
    
    print(f"\n🎵 Complete dataset ready for Music Besties integration!")
    print(f"📊 Use: artists_sorted_by_popularity for engagement ranking")
    print(f"📋 Use: artists_in_original_order for Top 100 chart reference")

if __name__ == "__main__":
    main() 