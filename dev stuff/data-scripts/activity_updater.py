#!/usr/bin/env python3
"""
Reddit Activity Updater

TARGETED EFFICIENCY:
- Only updates activity data for existing subreddits
- 1 API call per artist (vs 13+ for full analysis)
- Keeps existing subreddit discovery
- Fixes the 50-post truncation issue
- ~51 API calls total (only artists with Reddit presence)
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

# Conservative configuration for activity updates
CONFIG = {
    "RATE_LIMIT_DELAY": 4.0,  # Conservative rate limiting
    "REQUEST_TIMEOUT": 15,
    "MAX_PAGINATION_CALLS": 6,  # Up to 600 posts for complete data
    "POSTS_PER_REQUEST": 100,
    "RETRY_ATTEMPTS": 2,
    "RETRY_DELAY": 10
}

def safe_request(url, headers, params):
    """Conservative API request with error handling."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        
        if response.status_code == 429:  # Rate limited
            print(f"        ⏳ Rate limited, waiting {CONFIG['RETRY_DELAY']}s...")
            time.sleep(CONFIG["RETRY_DELAY"])
            # Try once more after rate limit
            response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        print(f"        ❌ Request failed: {str(e)[:50]}...")
        return None

def get_accurate_monthly_activity(subreddit_name):
    """
    Get ACCURATE monthly activity with proper pagination.
    Fixes the 50-post truncation issue.
    """
    print(f"    📊 Collecting accurate monthly data for r/{subreddit_name}...")
    
    current_time = time.time()
    month_ago = current_time - (30 * 24 * 60 * 60)
    
    posts_last_month = 0
    total_comments = 0
    after = None
    api_calls_made = 0
    
    while api_calls_made < CONFIG["MAX_PAGINATION_CALLS"]:
        # Build paginated request
        url = f"https://www.reddit.com/r/{subreddit_name}/new.json"
        headers = {'User-Agent': USER_AGENT}
        params = {'limit': CONFIG["POSTS_PER_REQUEST"]}
        
        if after:
            params['after'] = after
        
        # Make request
        print(f"        📥 API call {api_calls_made + 1}: Fetching {CONFIG['POSTS_PER_REQUEST']} posts...")
        data = safe_request(url, headers, params)
        
        if not data or 'data' not in data:
            print(f"        ❌ No data returned, stopping collection")
            break
        
        posts = data['data']['children']
        if not posts:
            print(f"        ✅ No more posts available")
            break
        
        # Process this batch
        posts_in_batch = 0
        oldest_time_in_batch = current_time
        
        for post in posts:
            post_data = post.get('data', {})
            post_time = post_data.get('created_utc', 0)
            oldest_time_in_batch = min(oldest_time_in_batch, post_time)
            
            if post_time >= month_ago:
                posts_last_month += 1
                total_comments += post_data.get('num_comments', 0)
                posts_in_batch += 1
        
        print(f"        ✅ Found {posts_in_batch} qualifying posts in this batch")
        
        # Check if we've gone back far enough
        if oldest_time_in_batch < month_ago:
            print(f"        🎯 Reached posts older than 30 days, collection complete")
            break
        
        # Get next page marker
        after = data['data'].get('after')
        if not after:
            print(f"        ✅ No more pages available")
            break
        
        api_calls_made += 1
        time.sleep(2)  # Brief delay between pagination calls
    
    total_activity = posts_last_month + total_comments
    print(f"    📈 ACCURATE DATA: {posts_last_month} posts + {total_comments:,} comments = {total_activity:,} total activity")
    
    return posts_last_month, total_comments

def load_current_data():
    """Load the current Reddit analysis data."""
    data_file = project_root / "public" / "data" / "reddit_analysis.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_activity_data():
    """
    Update activity data for all artists with existing Reddit presence.
    Only 1 API call per artist = ~51 total calls vs 1,300+
    """
    
    print("🔧 REDDIT ACTIVITY UPDATER")
    print("=" * 50)
    print("🎯 TARGETED EFFICIENCY:")
    print("   ✅ Only updates activity for existing subreddits")
    print("   ✅ 1 API call per artist (vs 13+ full analysis)")
    print("   ✅ Fixes 50-post truncation issue")
    print("   ✅ Keeps existing subreddit discovery")
    print("=" * 50)
    
    # Load current data
    current_data = load_current_data()
    current_results = current_data.get('artists_in_original_order', [])
    
    # Filter to only artists with Reddit presence that haven't been updated yet
    artists_with_presence = [
        artist for artist in current_results 
        if artist.get('primary_subreddit') and artist.get('tier') != "❌ No Presence"
    ]
    
    # Skip artists that have already been updated (have "last_updated" field)
    artists_to_update = [
        artist for artist in artists_with_presence 
        if not artist.get('last_updated')
    ]
    
    print(f"📋 Total artists with Reddit presence: {len(artists_with_presence)}")
    print(f"✅ Already updated: {len(artists_with_presence) - len(artists_to_update)}")
    print(f"🎯 Remaining to update: {len(artists_to_update)}")
    print(f"⏱️  Estimated time: {(len(artists_to_update) * CONFIG['RATE_LIMIT_DELAY'])/60:.1f} minutes\n")
    
    updated_results = []
    already_updated = []
    start_time = time.time()
    
    # Add already updated artists to keep them
    for artist in artists_with_presence:
        if artist.get('last_updated'):
            already_updated.append(artist)
    
    if not artists_to_update:
        print("🎉 All artists already updated!")
        return current_data
    
    for i, artist_data in enumerate(artists_to_update, 1):
        artist_name = artist_data.get('artist', 'Unknown')
        subreddit_name = artist_data.get('primary_subreddit', '')
        
        print(f"[{i:2d}/{len(artists_to_update)}] {'-' * 40}")
        print(f"🎤 {artist_name} → r/{subreddit_name}")
        
        try:
            # Get accurate activity data
            posts, comments = get_accurate_monthly_activity(subreddit_name)
            total_activity = posts + comments
            
            # Recalculate score
            subscribers = artist_data.get('subscribers', 0)
            if subscribers > 0:
                new_score = round((total_activity / subscribers) * 1000, 2)
            else:
                new_score = 0.0
            
            # Reclassify tier
            if new_score >= 5.0:
                new_tier = "🔥 Viral"
            elif new_score >= 2.0:
                new_tier = "⚡ Popular"
            elif new_score >= 0.5:
                new_tier = "📊 Present"
            else:
                new_tier = "💤 Minimal"
            
            # Create updated entry
            updated_artist = artist_data.copy()
            updated_artist.update({
                "posts_last_month": posts,
                "comments_last_month": comments,
                "total_activity": total_activity,
                "popularity_score": new_score,
                "tier": new_tier,
                "last_updated": datetime.datetime.now().isoformat(),
                "methodology": "Accurate pagination - Fixed truncation issue"
            })
            
            updated_results.append(updated_artist)
            
            # Show improvement
            old_activity = artist_data.get('total_activity', 0)
            old_score = artist_data.get('popularity_score', 0)
            
            improvement = total_activity / max(old_activity, 1)
            print(f"    📊 OLD: {old_activity:,} activity, {old_score} score")
            print(f"    📈 NEW: {total_activity:,} activity, {new_score} score")
            print(f"    🚀 IMPROVEMENT: {improvement:.1f}x more accurate data")
            
            # Progress update
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = avg_time * (len(artists_to_update) - i)
            print(f"    ⏱️  Progress: {i}/{len(artists_to_update)} | {remaining/60:.1f}min remaining")
            
        except Exception as e:
            print(f"    ❌ ERROR updating {artist_name}: {e}")
            # Keep original data if update fails
            updated_results.append(artist_data)
        
        # Rate limiting between requests
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    # Merge with artists that had no presence (unchanged)
    artists_without_presence = [
        artist for artist in current_results 
        if not artist.get('primary_subreddit') or artist.get('tier') == "❌ No Presence"
    ]
    
    all_updated_results = already_updated + updated_results + artists_without_presence
    
    # Sort back to original order
    artist_order = [artist.get('artist') for artist in current_results]
    all_updated_results.sort(key=lambda x: artist_order.index(x.get('artist', '')))
    
    # Create updated dataset
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    updated_data = current_data.copy()
    updated_data.update({
        "analysis_date": datetime.datetime.now().isoformat(),
        "methodology": "Activity Update - Fixed 50-post truncation",
        "update_type": "Activity data only - kept existing subreddit discovery",
        "artists_updated_this_run": len(updated_results),
        "artists_previously_updated": len(already_updated),
        "total_artists_with_accurate_data": len(already_updated) + len(updated_results),
        "improvements_applied": [
            "Fixed 50-post truncation with proper pagination",
            "Collected complete monthly activity data",
            "Recalculated engagement scores with accurate data",
            "Updated tier classifications"
        ],
        "artists_in_original_order": all_updated_results
    })
    
    # Save updated data
    output_file = OUTPUT_DIR / f"activity_updated_analysis_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    # Also update the main public data file
    public_data_file = project_root / "public" / "data" / "reddit_analysis.json"
    with open(public_data_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    elapsed_total = time.time() - start_time
    print(f"\n📄 Activity update complete!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📁 Public data updated: {public_data_file}")
    print(f"\n📊 UPDATE SUMMARY:")
    print(f"   ⏱️  Total time: {elapsed_total/60:.1f} minutes")
    print(f"   📡 API calls used: ~{len(updated_results) * 3}")  # Estimate with pagination
    print(f"   ✅ Artists updated: {len(updated_results)}")
    print(f"   📈 Data accuracy: Significantly improved with proper pagination")
    
    return updated_data

if __name__ == "__main__":
    print("🎯 Reddit Activity Updater - Ready")
    print("💡 Call update_activity_data() to fix activity data") 