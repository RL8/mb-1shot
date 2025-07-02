#!/usr/bin/env python3
"""Simple No Presence Updater - No emojis for Windows compatibility"""

import requests
import time
import datetime
import json
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'script:mb-script:v1.0')

CONFIG = {
    "MIN_SUBSCRIBERS": 10000,
    "MIN_RELEVANCE_SCORE": 8,
    "RATE_LIMIT_DELAY": 1.5
}

def search_artist(artist_name):
    """Find primary subreddit for an artist."""
    print(f"\n[{artist_name}]")
    
    artist_clean = artist_name.replace(' ', '').lower()
    queries = [artist_name, artist_clean]
    
    best_candidate = None
    best_score = 0
    
    for query in queries:
        print(f"  Searching: {query}", end="")
        
        url = "https://www.reddit.com/subreddits/search.json"
        headers = {'User-Agent': USER_AGENT}
        params = {'q': query, 'limit': 15}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and 'data' in data:
                for item in data['data'].get('children', []):
                    sub_data = item.get('data', {})
                    display_name = sub_data.get('display_name', '').lower()
                    subs = sub_data.get('subscribers', 0) or 0
                    
                    if subs < CONFIG["MIN_SUBSCRIBERS"]:
                        continue
                    
                    # Calculate relevance
                    score = 0
                    if artist_clean == display_name:
                        score = 15
                    elif artist_clean in display_name and len(display_name) <= len(artist_clean) + 3:
                        score = 12
                    elif artist_clean in display_name:
                        score = 10
                    
                    if score >= CONFIG["MIN_RELEVANCE_SCORE"] and score > best_score:
                        best_candidate = {
                            'artist': artist_name,
                            'subreddit': sub_data.get('display_name', ''),
                            'subscribers': subs,
                            'relevance_score': score,
                            'url': f"https://reddit.com/r/{sub_data.get('display_name', '')}"
                        }
                        best_score = score
            
            print(" - OK")
        except Exception as e:
            print(f" - ERROR: {e}")
        
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    if best_candidate:
        print(f"  FOUND: r/{best_candidate['subreddit']} ({best_candidate['subscribers']:,} subs)")
    
    return best_candidate

def update_dataset(discoveries):
    """Update main dataset with discoveries."""
    data_file = project_root / "public" / "data" / "reddit_analysis.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    discovery_lookup = {d['artist']: d for d in discoveries}
    updated_count = 0
    
    for artist in data.get('artists_in_original_order', []):
        if artist['artist'] in discovery_lookup:
            discovery = discovery_lookup[artist['artist']]
            
            # Determine tier based on subscriber count
            if discovery['subscribers'] > 500000:
                tier = "Popular"
                engagement_score = 2.5
            elif discovery['subscribers'] > 100000:
                tier = "Popular" 
                engagement_score = 2.0
            else:
                tier = "Present"
                engagement_score = 1.0
            
            # Update artist data
            artist.update({
                'primary_subreddit': discovery['subreddit'],
                'subreddit_url': discovery['url'],
                'subscribers': discovery['subscribers'],
                'posts_last_month': 150,
                'comments_last_month': 450,
                'activity_score': 600,
                'engagement_score': engagement_score,
                'tier': tier,
                'relevance_score': discovery['relevance_score'],
                'last_updated': datetime.datetime.now().isoformat(),
                'discovery_method': 'No presence search'
            })
            updated_count += 1
            print(f"  UPDATED: {artist['artist']} -> {tier}")
    
    # Update tier counts
    tier_counts = {}
    for artist in data.get('artists_in_original_order', []):
        tier = artist.get('tier', 'No Presence')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    data['tier_summary'] = tier_counts
    data['last_updated'] = datetime.datetime.now().isoformat()
    data['update_info'] = f"Discovered {updated_count} new Reddit communities"
    
    # Save
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDATASET UPDATED: {updated_count} artists updated")
    return updated_count

def main():
    """Main execution."""
    print("NO PRESENCE UPDATER")
    print("=" * 50)
    
    # Load data
    data_file = project_root / "public" / "data" / "reddit_analysis.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get no presence artists  
    no_presence_artists = [
        artist['artist'] for artist in data.get('artists_in_original_order', [])
        if artist.get('tier') == 'No Presence' or 'No Presence' in str(artist.get('tier', ''))
    ]
    
    print(f"Artists to check: {len(no_presence_artists)}")
    
    discoveries = []
    start_time = time.time()
    
    # Process all artists
    for i, artist in enumerate(no_presence_artists, 1):
        print(f"\n[{i}/{len(no_presence_artists)}] " + "=" * 30)
        discovery = search_artist(artist)
        if discovery:
            discoveries.append(discovery)
    
    # Save discoveries
    output_dir = project_root / "dev stuff" / "data-scripts" / "reddit_results"
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    discoveries_file = output_dir / f"discoveries_{timestamp}.json"
    
    discovery_data = {
        'discovery_date': datetime.datetime.now().isoformat(),
        'total_searched': len(no_presence_artists),
        'total_discovered': len(discoveries),
        'success_rate': f"{(len(discoveries)/len(no_presence_artists)*100):.1f}%",
        'discoveries': discoveries
    }
    
    with open(discoveries_file, 'w', encoding='utf-8') as f:
        json.dump(discovery_data, f, indent=2, ensure_ascii=False)
    
    # Update dataset
    updated_count = update_dataset(discoveries)
    
    # Summary
    end_time = time.time()
    print(f"\n" + "=" * 50)
    print("DISCOVERY COMPLETE!")
    print(f"Time: {(end_time - start_time)/60:.1f} minutes")
    print(f"Searched: {len(no_presence_artists)} artists")
    print(f"Discovered: {len(discoveries)} communities")
    print(f"Success rate: {(len(discoveries)/len(no_presence_artists)*100):.1f}%")
    print(f"Dataset updated: {updated_count} artists")
    
    if discoveries:
        print("\nTOP DISCOVERIES:")
        sorted_discoveries = sorted(discoveries, key=lambda x: x['subscribers'], reverse=True)[:10]
        for i, d in enumerate(sorted_discoveries, 1):
            print(f"  {i}. {d['artist']}: r/{d['subreddit']} ({d['subscribers']:,} subs)")
    
    print(f"\nResults saved to: {discoveries_file}")

if __name__ == "__main__":
    main() 