#!/usr/bin/env python3
"""
Reddit No Presence Finder - Find communities for artists with "❌ No Presence"

RELAXED CRITERIA:
- Minimum 10K subscribers (vs 50K)
- Lower relevance threshold (5 vs 8)
- More comprehensive search patterns
- Includes smaller fan communities
"""

import requests
import time
import datetime
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'script:mb-script:v1.0 (by /u/tapinda)')
OUTPUT_DIR = project_root / "dev stuff" / "data-scripts" / "reddit_results"
OUTPUT_DIR.mkdir(exist_ok=True)

# RELAXED CONFIG
CONFIG = {
    "MIN_SUBSCRIBERS": 10000,        # Lowered from 50K
    "MIN_RELEVANCE_SCORE": 5,        # Lowered from 8  
    "RATE_LIMIT_DELAY": 2.0,
    "REQUEST_TIMEOUT": 15,
    "SEARCH_LIMIT": 25
}

def safe_request(url, headers, params):
    """Make safe API request with retries."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f" ❌ Error: {e}")
        return None

def calculate_relevance(subreddit_data, artist_name):
    """Calculate relevance with relaxed criteria."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    
    artist_lower = artist_name.lower()
    artist_clean = artist_lower.replace(' ', '').replace('.', '').replace(',', '').replace("'", '')
    
    score = 0
    reasons = []
    
    # Exact matches
    if artist_clean == display_name:
        score += 12
        reasons.append("Exact match")
    elif artist_lower.replace(' ', '_') == display_name:
        score += 10
        reasons.append("Exact match (underscores)")
    
    # Partial matches
    elif artist_clean in display_name:
        score += 8
        reasons.append("Artist name in subreddit")
    
    # Fan patterns
    fan_patterns = [f"{artist_clean}fans", f"{artist_clean}fan", f"{artist_clean}music"]
    if any(pattern == display_name for pattern in fan_patterns):
        score += 9
        reasons.append("Fan pattern match")
    
    # Community indicators
    if any(word in display_name for word in ['fans', 'fan', 'music', 'official']):
        score += 4
        reasons.append("Fan community indicator")
    
    # Description mentions
    if artist_lower in description:
        score += 3
        reasons.append("Artist mentioned in description")
    
    return score, " | ".join(reasons)

def search_artist_comprehensive(artist_name):
    """Comprehensive search for hard-to-find artists."""
    print(f"\n🔍 SEARCHING: {artist_name}")
    print("-" * 40)
    
    artist_clean = artist_name.replace(' ', '').replace('.', '').replace(',', '').replace("'", '').lower()
    
    # Comprehensive search queries
    queries = [
        artist_name,
        artist_clean,
        artist_name.replace(' ', '_').lower(),
        f"{artist_name} fans",
        f"{artist_name} fan", 
        f"{artist_name} music",
        f"{artist_clean}fans",
        f"{artist_clean}fan",
        f"{artist_clean}music",
        f"r/{artist_clean}",
        f"{artist_name} official",
        f"{artist_name} community"
    ]
    
    candidates = []
    processed_ids = set()
    
    for i, query in enumerate(queries, 1):
        print(f"  [{i:2d}/12] '{query}'", end="")
        
        url = "https://www.reddit.com/subreddits/search.json"
        headers = {'User-Agent': USER_AGENT}
        params = {'q': query, 'limit': CONFIG["SEARCH_LIMIT"]}
        
        data = safe_request(url, headers, params)
        
        if not data or 'data' not in data:
            print("")
            time.sleep(CONFIG["RATE_LIMIT_DELAY"])
            continue
        
        found_new = 0
        for item in data['data'].get('children', []):
            subreddit_data = item.get('data', {})
            subreddit_id = subreddit_data.get('id')
            
            if subreddit_id in processed_ids:
                continue
            processed_ids.add(subreddit_id)
            
            subscribers = subreddit_data.get('subscribers', 0) or 0
            if subscribers < CONFIG["MIN_SUBSCRIBERS"]:
                continue
            
            relevance_score, relevance_reasons = calculate_relevance(subreddit_data, artist_name)
            
            if relevance_score >= CONFIG["MIN_RELEVANCE_SCORE"]:
                candidates.append({
                    "artist": artist_name,
                    "subreddit": subreddit_data.get('display_name', ''),
                    "url": f"https://reddit.com/r/{subreddit_data.get('display_name', '')}",
                    "subscribers": subscribers,
                    "relevance_score": relevance_score,
                    "relevance_reasons": relevance_reasons,
                    "description": (subreddit_data.get('public_description') or '')[:150],
                    "found_by_query": query
                })
                found_new += 1
        
        print(f" ✅ {found_new} new")
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    candidates.sort(key=lambda x: (x['relevance_score'], x['subscribers']), reverse=True)
    
    print(f"  📊 TOTAL: {len(candidates)} communities found")
    if candidates:
        best = candidates[0]
        print(f"  🏆 BEST: r/{best['subreddit']} ({best['subscribers']:,} subs, score: {best['relevance_score']})")
    
    return candidates

def load_no_presence_artists():
    """Load artists with no current Reddit presence."""
    data_file = project_root / "public" / "data" / "reddit_analysis.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    no_presence_artists = [
        artist['artist'] for artist in data.get('artists_in_original_order', [])
        if artist.get('tier') == "❌ No Presence"
    ]
    
    return no_presence_artists

def save_results(results):
    """Save discovery results."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"no_presence_discovery_{timestamp}.json"
    filepath = OUTPUT_DIR / filename
    
    output_data = {
        "discovery_date": datetime.datetime.now().isoformat(),
        "methodology": "Comprehensive search with relaxed criteria",
        "criteria": {
            "min_subscribers": CONFIG["MIN_SUBSCRIBERS"],
            "min_relevance_score": CONFIG["MIN_RELEVANCE_SCORE"]
        },
        "artists_searched": len(set(r['artist'] for r in results)),
        "total_discoveries": len(results),
        "discoveries": results
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Results saved to: {filepath}")
    return filepath

def main():
    """Find Reddit communities for artists with no presence."""
    print("🎯 REDDIT NO PRESENCE FINDER")
    print("=" * 50)
    print("🔍 Finding communities for artists with no current presence")
    print(f"📊 RELAXED CRITERIA: {CONFIG['MIN_SUBSCRIBERS']:,} min subs, {CONFIG['MIN_RELEVANCE_SCORE']} min score")
    print("=" * 50)
    
    no_presence_artists = load_no_presence_artists()
    print(f"\n📋 {len(no_presence_artists)} artists with no current presence")
    
    if not no_presence_artists:
        print("🎉 All artists already have Reddit presence!")
        return
    
    all_discoveries = []
    start_time = time.time()
    
    try:
        for i, artist in enumerate(no_presence_artists, 1):
            print(f"\n[{i:2d}/{len(no_presence_artists)}] {'=' * 40}")
            discoveries = search_artist_comprehensive(artist)
            all_discoveries.extend(discoveries)
        
        save_results(all_discoveries)
        
        # Summary
        end_time = time.time()
        successful_artists = len(set(d['artist'] for d in all_discoveries))
        
        print(f"\n🎉 SEARCH COMPLETE!")
        print(f"⏱️  Time: {(end_time - start_time)/60:.1f} minutes")
        print(f"🎯 Searched: {len(no_presence_artists)} artists")
        print(f"✅ Found communities: {successful_artists} artists")
        print(f"📊 Total communities: {len(all_discoveries)}")
        print(f"📈 Success rate: {(successful_artists/len(no_presence_artists)*100):.1f}%")
        
        if all_discoveries:
            print(f"\n🏆 TOP DISCOVERIES:")
            top = sorted(all_discoveries, key=lambda x: x['relevance_score'], reverse=True)[:8]
            for i, d in enumerate(top, 1):
                print(f"  {i}. {d['artist']}: r/{d['subreddit']} ({d['subscribers']:,} subs)")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Search interrupted")
    except Exception as e:
        print(f"\n❌ Search failed: {e}")

if __name__ == "__main__":
    main() 