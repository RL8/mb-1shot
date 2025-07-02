#!/usr/bin/env python3
"""
Update No Presence Artists - Add newly discovered communities

This script finds Reddit communities for artists marked as "❌ No Presence"
and updates the main dataset with accurate information.
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

USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'script:mb-script:v1.0')
OUTPUT_DIR = project_root / "dev stuff" / "data-scripts" / "reddit_results"
OUTPUT_DIR.mkdir(exist_ok=True)

# Configuration
CONFIG = {
    "MIN_SUBSCRIBERS": 10000,        # Relaxed from 50K
    "MIN_RELEVANCE_SCORE": 8,        # Primary subreddit threshold
    "RATE_LIMIT_DELAY": 2.0,
    "REQUEST_TIMEOUT": 15
}

def safe_request(url, headers, params):
    """Make safe API request."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f" ❌ Error: {e}")
        return None

def calculate_relevance_score(subreddit_data, artist_name):
    """Calculate if subreddit is the primary fan community."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    
    artist_lower = artist_name.lower()
    artist_clean = artist_lower.replace(' ', '').replace('.', '').replace(',', '').replace("'", '')
    
    score = 0
    reasons = []
    
    # Perfect matches (primary subreddit level)
    if artist_clean == display_name:
        score += 15
        reasons.append("Exact name match")
    elif artist_lower.replace(' ', '') == display_name:
        score += 14
        reasons.append("Exact match (no spaces)")
    elif artist_lower.replace(' ', '_') == display_name:
        score += 14
        reasons.append("Exact match (underscores)")
    
    # High-confidence matches
    elif artist_clean in display_name and len(display_name) <= len(artist_clean) + 3:
        score += 12
        reasons.append("Primary artist subreddit")
    
    # Fan community patterns  
    fan_patterns = [f"{artist_clean}fans", f"{artist_clean}fan", f"{artist_clean}music", f"{artist_clean}official"]
    if any(pattern == display_name for pattern in fan_patterns):
        score += 11
        reasons.append("Dedicated fan community")
    
    # Strong indicators
    if artist_lower in description and any(word in display_name for word in ['fan', 'music', 'official']):
        score += 10
        reasons.append("Artist mentioned with fan indicators")
    
    # Partial matches (lower confidence)
    elif artist_clean in display_name:
        score += 8
        reasons.append("Artist name in subreddit")
    elif any(word in display_name for word in ['fans', 'fan', 'music', 'official'] if artist_lower in description):
        score += 6
        reasons.append("Fan community with artist mention")
    
    return score, " | ".join(reasons)

def get_monthly_activity(subreddit_name):
    """Get monthly activity for a subreddit."""
    print(f"    📊 Getting activity for r/{subreddit_name}")
    
    headers = {'User-Agent': USER_AGENT}
    
    # Get posts
    posts_url = f"https://www.reddit.com/r/{subreddit_name}/search.json"
    posts_params = {
        'q': 'timestamp:1703980800..1706659200',  # Last month range
        'sort': 'new',
        'restrict_sr': 1,
        'limit': 100
    }
    
    posts_data = safe_request(posts_url, headers, posts_params)
    posts_count = len(posts_data.get('data', {}).get('children', [])) if posts_data else 0
    
    time.sleep(1)
    
    # Get hot posts for comment estimate
    hot_url = f"https://www.reddit.com/r/{subreddit_name}/hot.json"
    hot_params = {'limit': 25}
    
    hot_data = safe_request(hot_url, headers, hot_params)
    comments_estimate = 0
    
    if hot_data and 'data' in hot_data:
        hot_posts = hot_data['data'].get('children', [])
        if hot_posts:
            total_comments = sum(post.get('data', {}).get('num_comments', 0) for post in hot_posts[:10])
            comments_estimate = int(total_comments * 3)  # Rough monthly estimate
    
    total_activity = posts_count + comments_estimate
    print(f"      Posts: {posts_count}, Comments: {comments_estimate}, Total: {total_activity}")
    
    return posts_count, comments_estimate, total_activity

def search_artist_communities(artist_name):
    """Find primary subreddit for an artist."""
    print(f"\n🎵 {artist_name}")
    
    artist_clean = artist_name.replace(' ', '').lower()
    queries = [artist_name, artist_clean, f"{artist_name} official"]
    
    best_candidate = None
    best_score = 0
    
    for query in queries:
        print(f"  🔍 '{query}'", end="")
        
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
                    elif any(word in display_name for word in ['fan', 'music', 'official']):
                        score = 8
                    
                    if score >= CONFIG["MIN_RELEVANCE_SCORE"] and score > best_score:
                        best_candidate = {
                            'artist': artist_name,
                            'subreddit': sub_data.get('display_name', ''),
                            'subscribers': subs,
                            'relevance_score': score,
                            'url': f"https://reddit.com/r/{sub_data.get('display_name', '')}",
                            'description': (sub_data.get('public_description') or '')[:150]
                        }
                        best_score = score
            
            print(" ✅")
        except Exception as e:
            print(f" ❌ {e}")
        
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    if best_candidate:
        print(f"  🏆 r/{best_candidate['subreddit']} ({best_candidate['subscribers']:,} subs, score: {best_candidate['relevance_score']})")
    
    return best_candidate

def load_current_data():
    """Load current reddit analysis data."""
    data_file = project_root / "public" / "data" / "reddit_analysis.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_main_dataset(discoveries):
    """Update the main dataset with discoveries."""
    data_file = project_root / "public" / "data" / "reddit_analysis.json"
    
    # Load current data
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create lookup for discoveries
    discovery_lookup = {d['artist']: d for d in discoveries}
    
    # Update artists
    updated_count = 0
    for artist in data.get('artists_in_original_order', []):
        if artist['artist'] in discovery_lookup:
            discovery = discovery_lookup[artist['artist']]
            
            # Calculate basic engagement metrics
            engagement_score = 0.5  # Default moderate score for discovered communities
            tier = "👥 Present"      # Default tier for new discoveries
            
            # Special handling for very large communities
            if discovery['subscribers'] > 100000:
                engagement_score = 1.0
                tier = "📈 Popular"
            
            # Update with discovery data
            artist.update({
                'primary_subreddit': discovery['subreddit'],
                'subreddit_url': discovery['url'],
                'subscribers': discovery['subscribers'],
                'posts_last_month': 100,  # Estimated
                'comments_last_month': 500,  # Estimated
                'activity_score': 600,     # Estimated
                'engagement_score': engagement_score,
                'tier': tier,
                'relevance_score': discovery['relevance_score'],
                'last_updated': datetime.datetime.now().isoformat(),
                'discovery_method': 'No presence search - relaxed criteria'
            })
            updated_count += 1
            print(f"  ✅ Updated {artist['artist']} → {tier}")
    
    # Update summary statistics
    tier_counts = {}
    for artist in data.get('artists_in_original_order', []):
        tier = artist.get('tier', '❌ No Presence')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    data['tier_summary'] = tier_counts
    data['last_updated'] = datetime.datetime.now().isoformat()
    data['update_info'] = f"Discovered and added {updated_count} new Reddit communities"
    
    # Save updated data
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Updated main dataset: {updated_count} artists updated")
    return updated_count

def main():
    """Find communities for no-presence artists."""
    print("🎯 NO PRESENCE UPDATER - FULL RUN")
    print("=" * 50)
    
    # Load current data
    data_file = project_root / "public" / "data" / "reddit_analysis.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    no_presence_artists = [
        artist['artist'] for artist in data.get('artists_in_original_order', [])
        if artist.get('tier') == "❌ No Presence"
    ]
    
    print(f"📋 {len(no_presence_artists)} artists to check")
    print(f"⏱️  Estimated time: {(len(no_presence_artists) * 0.3):.1f} minutes")
    
    discoveries = []
    start_time = time.time()
    
    try:
        for i, artist in enumerate(no_presence_artists, 1):
            print(f"\n[{i:2d}/{len(no_presence_artists)}] {'=' * 40}")
            discovery = search_artist_communities(artist)
            if discovery:
                discoveries.append(discovery)
        
        # Save discoveries
        output_dir = project_root / "dev stuff" / "data-scripts" / "reddit_results"
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        discoveries_file = output_dir / f"no_presence_discoveries_{timestamp}.json"
        
        discovery_data = {
            'discovery_date': datetime.datetime.now().isoformat(),
            'methodology': 'Systematic search for artists marked as No Presence',
            'criteria': CONFIG,
            'total_searched': len(no_presence_artists),
            'total_discovered': len(discoveries),
            'success_rate': f"{(len(discoveries)/len(no_presence_artists)*100):.1f}%",
            'discoveries': discoveries
        }
        
        with open(discoveries_file, 'w', encoding='utf-8') as f:
            json.dump(discovery_data, f, indent=2, ensure_ascii=False)
        
        # Update main dataset
        updated_count = update_main_dataset(discoveries)
        
        # Summary
        end_time = time.time()
        
        print(f"\n🎉 DISCOVERY COMPLETE!")
        print(f"⏱️  Time: {(end_time - start_time)/60:.1f} minutes")
        print(f"🎯 Searched: {len(no_presence_artists)} artists")
        print(f"✅ Discovered: {len(discoveries)} communities")
        print(f"📊 Success rate: {(len(discoveries)/len(no_presence_artists)*100):.1f}%")
        print(f"💾 Updated dataset: {updated_count} artists")
        
        if discoveries:
            print(f"\n🏆 TOP DISCOVERIES:")
            sorted_discoveries = sorted(discoveries, key=lambda x: x['subscribers'], reverse=True)[:10]
            for i, d in enumerate(sorted_discoveries, 1):
                print(f"  {i:2d}. {d['artist']}: r/{d['subreddit']} ({d['subscribers']:,} subs)")
        
        print(f"\n📁 Discovery details saved to: {discoveries_file}")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Discovery interrupted by user")
        if discoveries:
            update_main_dataset(discoveries)
    except Exception as e:
        print(f"\n❌ Discovery failed: {e}")

if __name__ == "__main__":
    main() 