#!/usr/bin/env python3
"""
Drake-Specific Reddit Analyzer

Manual analysis to find the correct Drake (rapper) subreddit.
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
    "REQUEST_TIMEOUT": 15
}

def safe_request(url, headers, params):
    """Make a safe request."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def check_subreddit_details(subreddit_name):
    """Get detailed information about a specific subreddit."""
    url = f"https://www.reddit.com/r/{subreddit_name}/about.json"
    headers = {'User-Agent': USER_AGENT}
    
    data = safe_request(url, headers, {})
    if not data or 'data' not in data:
        return None
    
    subreddit_data = data['data']
    
    print(f"\n📋 r/{subreddit_name}:")
    print(f"   Subscribers: {subreddit_data.get('subscribers', 0):,}")
    print(f"   Title: {subreddit_data.get('title', 'N/A')}")
    print(f"   Description: {subreddit_data.get('public_description', 'N/A')[:100]}...")
    
    return subreddit_data

def get_monthly_activity(subreddit_name):
    """Get activity from last 30 days."""
    url = f"https://www.reddit.com/r/{subreddit_name}/new.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'limit': 50}
    
    data = safe_request(url, headers, params)
    if not data or 'data' not in data:
        return 0, 0
    
    posts = data['data']['children']
    current_time = time.time()
    month_ago = current_time - (30 * 24 * 60 * 60)
    
    posts_last_month = 0
    total_comments = 0
    
    for post in posts:
        post_data = post.get('data', {})
        post_time = post_data.get('created_utc', 0)
        
        if post_time >= month_ago:
            posts_last_month += 1
            total_comments += post_data.get('num_comments', 0)
    
    return posts_last_month, total_comments

def main():
    """Manually check potential Drake rapper subreddits."""
    
    print("🎤 DRAKE RAPPER - MANUAL SUBREDDIT ANALYSIS")
    print("=" * 60)
    
    # Known potential Drake subreddits
    candidates = [
        'Drizzy',
        'Drake', 
        'ChampagnePapi',
        'OVO',
        'OctobersVeryOwn',
        'ovo_sound',
        'ovosound'
    ]
    
    results = []
    
    for subreddit in candidates:
        print(f"\n🔍 Checking r/{subreddit}...")
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
        
        subreddit_data = check_subreddit_details(subreddit)
        
        if subreddit_data:
            subscribers = subreddit_data.get('subscribers', 0)
            if subscribers >= 10000:
                
                posts, comments = get_monthly_activity(subreddit)
                total_activity = posts + comments
                
                if subscribers > 0:
                    engagement_score = (total_activity / subscribers) * 1000
                else:
                    engagement_score = 0
                
                if engagement_score >= 5.0:
                    tier = "🔥 Viral"
                elif engagement_score >= 2.0:
                    tier = "⚡ Popular"
                elif engagement_score >= 0.5:
                    tier = "📊 Present"
                else:
                    tier = "💤 Minimal"
                
                results.append({
                    "subreddit": subreddit,
                    "subscribers": subscribers,
                    "posts_last_month": posts,
                    "comments_last_month": comments,
                    "total_activity": total_activity,
                    "engagement_score": round(engagement_score, 2),
                    "tier": tier,
                    "title": subreddit_data.get('title', ''),
                    "description": subreddit_data.get('public_description', '')
                })
                
                print(f"   ✅ QUALIFIED: {subscribers:,} subs, {engagement_score:.2f} score")
            else:
                print(f"   ❌ Too small: {subscribers:,} subscribers")
        else:
            print(f"   ❌ Not found")
    
    results.sort(key=lambda x: x['engagement_score'], reverse=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"drake_manual_analysis_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "analysis_date": datetime.datetime.now().isoformat(),
            "methodology": "Manual Drake-specific verification",
            "artist": "Drake (rapper)", 
            "qualifying_subreddits": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Saved: {output_file}")
    
    if results:
        best = results[0]
        print(f"\n🏆 BEST: r/{best['subreddit']}")
        print(f"   📊 Score: {best['engagement_score']}")
        print(f"   👥 Subs: {best['subscribers']:,}")
        return best
    else:
        print("\n❌ No qualifying Drake subreddits found")
        return None

if __name__ == "__main__":
    main() 