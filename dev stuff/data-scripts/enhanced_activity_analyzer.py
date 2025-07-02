#!/usr/bin/env python3
"""
Enhanced Reddit Activity Analyzer

Fixes the 50-post truncation issue by implementing proper monthly data collection.
Uses multiple API calls and pagination to capture complete monthly activity.
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

CONFIG = {
    "RATE_LIMIT_DELAY": 2.0,
    "REQUEST_TIMEOUT": 15,
    "MAX_REQUESTS_PER_SUBREDDIT": 5,  # Max API calls to get complete data
    "POSTS_PER_REQUEST": 100          # Reddit's max limit
}

def safe_request(url, headers, params):
    """Make a safe request with error handling."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def get_complete_monthly_activity(subreddit_name):
    """
    Get COMPLETE monthly activity by paginating through posts until we reach 30 days ago.
    This fixes the 50-post truncation issue.
    """
    print(f"      📊 Collecting complete monthly data for r/{subreddit_name}...")
    
    current_time = time.time()
    month_ago = current_time - (30 * 24 * 60 * 60)
    
    posts_last_month = 0
    total_comments = 0
    after = None  # Pagination marker
    requests_made = 0
    
    while requests_made < CONFIG["MAX_REQUESTS_PER_SUBREDDIT"]:
        # Build URL with pagination
        url = f"https://www.reddit.com/r/{subreddit_name}/new.json"
        headers = {'User-Agent': USER_AGENT}
        params = {'limit': CONFIG["POSTS_PER_REQUEST"]}
        
        if after:
            params['after'] = after
        
        # Make request
        print(f"        📥 Request {requests_made + 1}: Fetching {CONFIG['POSTS_PER_REQUEST']} posts...")
        data = safe_request(url, headers, params)
        
        if not data or 'data' not in data:
            print(f"        ❌ No data returned, stopping")
            break
        
        posts = data['data']['children']
        
        if not posts:
            print(f"        ✅ No more posts available")
            break
        
        # Process posts
        posts_in_this_batch = 0
        oldest_post_time = current_time
        
        for post in posts:
            post_data = post.get('data', {})
            post_time = post_data.get('created_utc', 0)
            oldest_post_time = min(oldest_post_time, post_time)
            
            if post_time >= month_ago:
                posts_last_month += 1
                total_comments += post_data.get('num_comments', 0)
                posts_in_this_batch += 1
        
        print(f"        ✅ Found {posts_in_this_batch} posts from last 30 days in this batch")
        
        # Check if we've gone back far enough
        if oldest_post_time < month_ago:
            print(f"        🎯 Reached posts older than 30 days, stopping")
            break
        
        # Get pagination marker for next request
        after = data['data'].get('after')
        if not after:
            print(f"        ✅ No more pages available")
            break
        
        requests_made += 1
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    print(f"      📈 COMPLETE RESULT: {posts_last_month} posts, {total_comments} comments (using {requests_made + 1} API calls)")
    
    return posts_last_month, total_comments

def test_subreddits():
    """Test the enhanced method on high-activity subreddits to verify the fix."""
    
    print("🔬 TESTING ENHANCED ACTIVITY COLLECTION")
    print("=" * 70)
    print("🎯 Testing subreddits that likely have >50 posts/month")
    print("=" * 70)
    
    # Test high-activity subreddits that probably have >50 posts/month
    test_cases = [
        ("TaylorSwift", "Taylor Swift"),
        ("KendrickLamar", "Kendrick Lamar"), 
        ("Drizzy", "Drake"),
        ("Eminem", "Eminem"),
        ("billieeilish", "Billie Eilish")
    ]
    
    results = []
    
    for subreddit_name, artist_name in test_cases:
        print(f"\n🎤 TESTING: r/{subreddit_name} ({artist_name})")
        print("-" * 50)
        
        # Get enhanced data
        posts, comments = get_complete_monthly_activity(subreddit_name)
        total_activity = posts + comments
        
        # Get subreddit info for subscriber count
        url = f"https://www.reddit.com/r/{subreddit_name}/about.json"
        headers = {'User-Agent': USER_AGENT}
        data = safe_request(url, headers, {})
        
        subscribers = 0
        if data and 'data' in data:
            subscribers = data['data'].get('subscribers', 0)
        
        # Calculate score
        if subscribers > 0:
            engagement_score = (total_activity / subscribers) * 1000
        else:
            engagement_score = 0
        
        result = {
            "artist": artist_name,
            "subreddit": subreddit_name,
            "subscribers": subscribers,
            "posts_last_month": posts,
            "comments_last_month": comments,
            "total_activity": total_activity,
            "engagement_score": round(engagement_score, 2),
            "data_collection": "Enhanced (complete monthly data)"
        }
        
        results.append(result)
        
        print(f"📊 ENHANCED RESULTS:")
        print(f"   Posts: {posts} (vs old method's max of 50)")
        print(f"   Comments: {comments:,}")
        print(f"   Subscribers: {subscribers:,}")
        print(f"   Engagement Score: {engagement_score:.2f}")
        
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    # Save results
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"enhanced_activity_test_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": datetime.datetime.now().isoformat(),
            "methodology": "Enhanced Monthly Activity Collection",
            "improvements": [
                "Removed 50-post truncation limit",
                "Added pagination to capture complete monthly data",
                "Multiple API calls per subreddit to get full picture",
                "Stops when reaching posts older than 30 days"
            ],
            "test_results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Test results saved: {output_file}")
    
    # Show comparison
    print(f"\n🔍 COMPARISON WITH OLD METHOD:")
    print("=" * 70)
    for result in results:
        if result['posts_last_month'] > 50:
            print(f"✅ {result['artist']}: {result['posts_last_month']} posts (vs 50 cap)")
        else:
            print(f"📊 {result['artist']}: {result['posts_last_month']} posts (accurate)")
    
    print(f"\n💡 KEY INSIGHT:")
    high_activity = [r for r in results if r['posts_last_month'] > 50]
    if high_activity:
        print(f"   {len(high_activity)}/{len(results)} subreddits had >50 posts/month")
        print(f"   Previous method was UNDERESTIMATING their activity!")
    else:
        print(f"   All tested subreddits had ≤50 posts/month")
        print(f"   The 50-post limit may not affect these specific artists")
    
    return results

if __name__ == "__main__":
    test_subreddits() 