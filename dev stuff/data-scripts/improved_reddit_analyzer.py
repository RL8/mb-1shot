#!/usr/bin/env python3
"""
Improved Reddit Artist Analyzer

Enhanced version that filters out parody/meme subreddits and focuses on genuine fan communities.
Addresses the Drake "DrakeTheType" parody subreddit issue.
"""

import requests
import time
import datetime
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import re

# Load environment
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'script:mb-script:v1.0 (by /u/tapinda)')
OUTPUT_DIR = project_root / "dev stuff" / "data-scripts" / "reddit_results"
OUTPUT_DIR.mkdir(exist_ok=True)

# Enhanced configuration
CONFIG = {
    "MIN_SUBSCRIBERS": 50000,
    "MIN_RELEVANCE_SCORE": 8,
    "RATE_LIMIT_DELAY": 2.0,
    "REQUEST_TIMEOUT": 15,
    "ACTIVITY_CHECK_LIMIT": 50,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 5
}

# Parody/meme subreddit indicators
PARODY_INDICATORS = [
    'thetype', 'type', 'meme', 'memes', 'jokes', 'circlejerk', 'jerk',
    'funny', 'humor', 'parody', 'satire', 'mock', 'fake', 'cringe',
    'outoftheloop', 'unpopular', 'hate', 'vs', 'versus', 'battle'
]

# Positive fan community indicators
FAN_INDICATORS = [
    'fans', 'fan', 'official', 'music', 'community', 'discussion',
    'news', 'updates', 'releases', 'album', 'song', 'tour'
]

def safe_request(url, headers, params, max_retries=3):
    """Make a request with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = CONFIG["RETRY_DELAY"] * (attempt + 1)
                print(f"      ⏳ Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                return None
        except Exception as e:
            if attempt == max_retries - 1:
                return None
            time.sleep(2)
    return None

def is_parody_subreddit(subreddit_data, artist_name):
    """Check if a subreddit is likely a parody/meme subreddit."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    title = (subreddit_data.get('title') or '').lower()
    
    # Check for parody indicators in name
    for indicator in PARODY_INDICATORS:
        if indicator in display_name:
            return True, f"Parody indicator '{indicator}' in subreddit name"
    
    # Check for parody indicators in description
    parody_words_in_desc = sum(1 for indicator in PARODY_INDICATORS if indicator in description)
    if parody_words_in_desc >= 2:
        return True, f"Multiple parody indicators in description"
    
    # Specific patterns that indicate parody
    if 'the type' in display_name or 'thetype' in display_name:
        return True, "Contains 'the type' pattern (parody format)"
    
    if 'meme' in description and 'joke' in description:
        return True, "Description mentions both memes and jokes"
    
    return False, "No parody indicators found"

def calculate_fan_community_score(subreddit_data, artist_name):
    """Calculate how likely this is a genuine fan community."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    title = (subreddit_data.get('title') or '').lower()
    
    artist_lower = artist_name.lower()
    artist_clean = artist_lower.replace(' ', '').replace(',', '').replace('.', '').replace("'", "")
    
    score = 0
    reasons = []
    
    # Exact match gets highest score
    if artist_clean == display_name:
        score += 15
        reasons.append("Exact artist name match")
    elif artist_lower.replace(' ', '') in display_name:
        score += 12
        reasons.append("Artist name in subreddit")
    
    # Official indicators
    if 'official' in display_name or 'official' in description:
        score += 8
        reasons.append("Official community")
    
    # Fan community indicators
    fan_score = sum(3 for indicator in FAN_INDICATORS if indicator in display_name or indicator in description)
    if fan_score > 0:
        score += min(fan_score, 9)  # Cap at 9 points
        reasons.append(f"Fan community indicators (+{min(fan_score, 9)})")
    
    # Artist mentioned in description
    if artist_lower in description:
        score += 5
        reasons.append("Artist mentioned in description")
    
    # Subscriber count bonus (larger communities more likely to be genuine)
    subscribers = subreddit_data.get('subscribers', 0) or 0
    if subscribers > 500000:
        score += 3
        reasons.append("Large community (500K+)")
    elif subscribers > 200000:
        score += 2
        reasons.append("Medium-large community (200K+)")
    
    return score, " | ".join(reasons) if reasons else "No strong indicators"

def search_subreddits(query, limit=15):
    """Search subreddits with enhanced limit."""
    url = "https://www.reddit.com/subreddits/search.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'q': query, 'limit': limit}
    return safe_request(url, headers, params)

def get_monthly_activity(subreddit_name):
    """Get posts + comments from last 30 days."""
    url = f"https://www.reddit.com/r/{subreddit_name}/new.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'limit': CONFIG["ACTIVITY_CHECK_LIMIT"]}
    
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

def calculate_artist_score(posts_last_month, comments_last_month, total_subscribers):
    """Core scoring function."""
    if total_subscribers == 0:
        return 0.0
    activity_score = posts_last_month + comments_last_month
    engagement_density = (activity_score / total_subscribers) * 1000
    return round(engagement_density, 2)

def get_tier_classification(score):
    """Classify score into engagement tiers."""
    if score >= 5.0:
        return "🔥 Viral"
    elif score >= 2.0:
        return "⚡ Popular"
    elif score >= 0.5:
        return "📊 Present"
    else:
        return "💤 Minimal"

def find_genuine_fan_subreddit(artist_name):
    """Find the genuine fan subreddit for an artist."""
    print(f"🎤 {artist_name}", end=" ", flush=True)
    
    artist_clean = artist_name.replace(' ', '').replace(',', '').replace('.', '').replace("'", "").lower()
    queries = [
        artist_name,
        artist_clean,
        f"{artist_name} music",
        f"{artist_name} fans",
        f"{artist_name} official"
    ]
    
    all_candidates = []
    processed_ids = set()
    
    for query in queries:
        print(".", end="", flush=True)
        data = search_subreddits(query, 15)
        if not data or 'data' not in data:
            continue
        
        for item in data['data'].get('children', []):
            subreddit_data = item.get('data', {})
            subreddit_id = subreddit_data.get('id')
            
            if subreddit_id in processed_ids:
                continue
            processed_ids.add(subreddit_id)
            
            subscribers = subreddit_data.get('subscribers', 0) or 0
            if subscribers < CONFIG["MIN_SUBSCRIBERS"]:
                continue
            
            # Check if it's a parody subreddit
            is_parody, parody_reason = is_parody_subreddit(subreddit_data, artist_name)
            if is_parody:
                continue
            
            # Calculate fan community score
            fan_score, fan_reasons = calculate_fan_community_score(subreddit_data, artist_name)
            
            if fan_score >= CONFIG["MIN_RELEVANCE_SCORE"]:
                all_candidates.append({
                    'data': subreddit_data,
                    'fan_score': fan_score,
                    'fan_reasons': fan_reasons,
                    'subscribers': subscribers
                })
        
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    if not all_candidates:
        print(" ❌")
        return None
    
    # Sort by fan community score first, then by subscribers
    all_candidates.sort(key=lambda x: (x['fan_score'], x['subscribers']), reverse=True)
    primary = all_candidates[0]
    
    subreddit_name = primary['data'].get('display_name')
    print(f" ✅ r/{subreddit_name}")
    
    return primary

def analyze_artist(artist_name):
    """Analyze a single artist with improved methodology."""
    primary_sub = find_genuine_fan_subreddit(artist_name)
    
    if not primary_sub:
        return {
            "artist": artist_name,
            "primary_subreddit": None,
            "subreddit_url": None,
            "subscribers": 0,
            "posts_last_month": 0,
            "comments_last_month": 0,
            "total_activity": 0,
            "popularity_score": 0.0,
            "tier": "❌ No Presence",
            "fan_community_score": 0,
            "fan_reasons": "No qualifying genuine fan subreddit found"
        }
    
    subreddit_name = primary_sub['data'].get('display_name', '')
    time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    posts, comments = get_monthly_activity(subreddit_name)
    total_activity = posts + comments
    score = calculate_artist_score(posts, comments, primary_sub['subscribers'])
    tier = get_tier_classification(score)
    
    return {
        "artist": artist_name,
        "primary_subreddit": subreddit_name,
        "subreddit_url": f"https://reddit.com/r/{subreddit_name}",
        "subscribers": primary_sub['subscribers'],
        "posts_last_month": posts,
        "comments_last_month": comments,
        "total_activity": total_activity,
        "popularity_score": score,
        "tier": tier,
        "fan_community_score": primary_sub['fan_score'],
        "fan_reasons": primary_sub['fan_reasons']
    }

def main():
    """Main execution for Drake-specific reanalysis."""
    print("🎵 IMPROVED REDDIT ANALYZER - DRAKE REANALYSIS")
    print("=" * 60)
    print("🚫 Enhanced parody detection")
    print("✅ Focus on genuine fan communities")
    print("=" * 60)
    
    drake_result = analyze_artist("Drake")
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"drake_corrected_analysis_{timestamp}.json"
    
    corrected_analysis = {
        "analysis_date": datetime.datetime.now().isoformat(),
        "methodology": "Enhanced Single Primary Subreddit - Genuine Fan Communities Only",
        "improvements": [
            "Added parody subreddit detection and filtering",
            "Enhanced fan community scoring system",
            "Filtered out meme/joke subreddits like 'DrakeTheType'",
            "Prioritized genuine fan engagement over parody content"
        ],
        "artist_analysis": drake_result
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(corrected_analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Saved: {output_file}")
    
    if drake_result['popularity_score'] > 0:
        print(f"\n✅ Found: r/{drake_result['primary_subreddit']}")
        print(f"   Subscribers: {drake_result['subscribers']:,}")
        print(f"   Score: {drake_result['popularity_score']} ({drake_result['tier']})")
    else:
        print(f"\n❌ No genuine fan community found")

if __name__ == "__main__":
    main() 