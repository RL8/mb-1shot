#!/usr/bin/env python3
"""
Reddit Artist Subreddit Finder - Public API Version

This version uses Reddit's public API (no authentication required) to discover
artist subreddits. This works with any Reddit app type.

Usage:
    python reddit_public_api_finder.py
"""

import requests
import time
import datetime
import json
import csv
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

# Use Reddit User Agent from env
USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'web:music-besties:v1.0 (by /u/user)')

# Configuration
CONFIG = {
    "SEARCH_LIMIT": 15,
    "RATE_LIMIT_DELAY": 1.5,
    "MIN_SUBSCRIBERS": 50,
    "REQUEST_TIMEOUT": 10
}

# Output directory
OUTPUT_DIR = project_root / "dev stuff" / "data-scripts" / "reddit_results"
OUTPUT_DIR.mkdir(exist_ok=True)

def search_subreddits_public(query, limit=15):
    """Search subreddits using public Reddit API."""
    url = "https://www.reddit.com/subreddits/search.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'q': query, 'limit': limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def analyze_subreddit_relevance(subreddit_data, artist_name):
    """Calculate relevance score for artist-subreddit match."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = subreddit_data.get('public_description', '').lower()
    title = subreddit_data.get('title', '').lower()
    
    artist_lower = artist_name.lower()
    artist_clean = artist_lower.replace(' ', '')
    
    score = 0
    reasons = []
    
    # Exact name matches
    if artist_clean == display_name:
        score += 10
        reasons.append("Exact name match")
    elif artist_lower in display_name:
        score += 8
        reasons.append("Artist name in subreddit name")
    
    # Fan community indicators
    fan_indicators = ['fans', 'fan', 'official', 'music']
    if any(indicator in display_name for indicator in fan_indicators):
        score += 3
        reasons.append("Fan community indicator")
    
    # Description analysis
    if artist_lower in description:
        score += 2
        reasons.append("Artist mentioned in description")
    
    # Title analysis
    if artist_lower in title:
        score += 2
        reasons.append("Artist in title")
    
    # Special fan patterns
    fan_patterns = [f"{artist_clean}fans", f"{artist_clean}fan", f"{artist_clean}music"]
    if any(pattern == display_name for pattern in fan_patterns):
        score += 8
        reasons.append("Fan pattern match")
    
    return score, reasons

def find_artist_subreddits_public(artist_name):
    """Find subreddits for an artist using public API."""
    print(f"\n🎵 Searching for: {artist_name}")
    
    # Generate search queries
    queries = [
        artist_name,
        f"{artist_name} fans",
        f"{artist_name} music",
        f"{artist_name} fan",
        artist_name.replace(' ', '').lower(),
        f"{artist_name.replace(' ', '').lower()}fans"
    ]
    
    found_subreddits = []
    processed_ids = set()
    
    for query in queries:
        print(f"  🔍 Query: '{query}'")
        
        data = search_subreddits_public(query, CONFIG["SEARCH_LIMIT"])
        if not data or 'data' not in data:
            continue
        
        results_count = len(data['data'].get('children', []))
        print(f"    Found {results_count} results")
        
        for item in data['data'].get('children', []):
            subreddit_data = item.get('data', {})
            subreddit_id = subreddit_data.get('id')
            
            if subreddit_id in processed_ids:
                continue
            processed_ids.add(subreddit_id)
            
            # Skip if too few subscribers
            subscribers = subreddit_data.get('subscribers', 0)
            if subscribers is None:
                subscribers = 0
            if subscribers < CONFIG["MIN_SUBSCRIBERS"]:
                continue
            
            # Calculate relevance
            relevance_score, reasons = analyze_subreddit_relevance(subreddit_data, artist_name)
            
            # Only include if relevance is high enough
            if relevance_score >= 3:
                subreddit_info = {
                    "artist": artist_name,
                    "subreddit": subreddit_data.get('display_name', ''),
                    "url": f"https://reddit.com/r/{subreddit_data.get('display_name', '')}",
                    "subscribers": subscribers if subscribers is not None else 0,
                    "relevance_score": relevance_score,
                    "relevance_reasons": ", ".join(reasons),
                    "description": (subreddit_data.get('public_description') or '')[:200],
                    "title": subreddit_data.get('title', ''),
                    "created_utc": subreddit_data.get('created_utc', 0),
                    "subreddit_type": subreddit_data.get('subreddit_type', 'public'),
                    "over18": subreddit_data.get('over18', False),
                    "query_found_by": query
                }
                found_subreddits.append(subreddit_info)
        
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    # Sort by relevance score, then subscribers
    found_subreddits.sort(key=lambda x: (x['relevance_score'], x['subscribers']), reverse=True)
    print(f"  ✅ Found {len(found_subreddits)} qualifying subreddits")
    
    return found_subreddits

def save_results(results, filename):
    """Save results to JSON and CSV files."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON
    json_file = OUTPUT_DIR / f"{filename}_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"📄 Saved JSON: {json_file}")
    
    # Save CSV
    if results:
        csv_file = OUTPUT_DIR / f"{filename}_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"📊 Saved CSV: {csv_file}")

if __name__ == "__main__":
    print("🎵 MUSIC BESTIES - Reddit Subreddit Discovery (Public API)")
    print(f"📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("🔍 Using Reddit's public API (no authentication required)")
    print(f"📁 Results will be saved to: {OUTPUT_DIR}")
    
    # Focused artist list for testing
    artists = [
        "Taylor Swift", "Billie Eilish", "Dua Lipa", 
        "Kendrick Lamar", "Drake", "Tyler The Creator",
        "Arctic Monkeys", "Tame Impala", "The 1975",
        "Daft Punk", "Flume", "ODESZA",
        "Phoebe Bridgers", "Mac Miller", "Frank Ocean",
        "The Weeknd", "SZA", "Anderson .Paak"
    ]
    
    print(f"\n🎯 Discovering subreddits for {len(artists)} artists...")
    
    all_results = []
    start_time = time.time()
    
    try:
        for i, artist in enumerate(artists, 1):
            print(f"\n[{i}/{len(artists)}] Processing: {artist}")
            artist_results = find_artist_subreddits_public(artist)
            all_results.extend(artist_results)
        
        # Save results
        save_results(all_results, "reddit_public_discovery")
        
        # Print summary
        end_time = time.time()
        print(f"\n🎉 DISCOVERY COMPLETE!")
        print(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
        print(f"📊 Total subreddits found: {len(all_results)}")
        
        if all_results:
            print(f"\n📈 TOP DISCOVERIES:")
            top_results = sorted(all_results, key=lambda x: x['relevance_score'], reverse=True)[:10]
            for result in top_results:
                print(f"  🎵 {result['artist']}: r/{result['subreddit']} ({result['subscribers']:,} subs, score: {result['relevance_score']})")
        
        print(f"\n✅ Reddit subreddit discovery completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Discovery interrupted by user")
    except Exception as e:
        print(f"\n❌ Discovery failed: {e}")
        import traceback
        traceback.print_exc() 