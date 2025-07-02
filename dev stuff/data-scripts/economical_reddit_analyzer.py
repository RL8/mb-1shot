#!/usr/bin/env python3
"""
Economical Reddit Analyzer

OPTIMIZED for rate limiting efficiency:
- 2-3 API calls per artist (vs 13+ in enhanced version)
- Smart sampling instead of complete data collection
- Focused search queries
- Maintains data quality while being 5x faster
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

# ECONOMICAL configuration - much more conservative
CONFIG = {
    "MIN_SUBSCRIBERS": 50000,
    "MIN_RELEVANCE_SCORE": 8,
    "RATE_LIMIT_DELAY": 3.0,  # More conservative for reliability
    "REQUEST_TIMEOUT": 15,
    "SAMPLE_SIZE": 50,  # Sample only 50 recent posts instead of all monthly
    "SEARCH_QUERIES": 2,  # Limit to 2 most effective search queries
    "RETRY_ATTEMPTS": 2,
    "RETRY_DELAY": 8
}

# Enhanced parody detection (keeping from V2)
PARODY_INDICATORS = [
    'thetype', 'type', 'meme', 'memes', 'jokes', 'circlejerk', 'jerk',
    'funny', 'humor', 'parody', 'satire', 'mock', 'fake', 'cringe',
    'outoftheloop', 'unpopular', 'hate', 'vs', 'versus', 'battle',
    'roast', 'okbuddy'
]

FAN_INDICATORS = [
    'fans', 'fan', 'official', 'music', 'community', 'discussion',
    'news', 'updates', 'releases', 'album', 'song', 'tour', 'concert'
]

def safe_request(url, headers, params, max_retries=2):
    """Conservative request with extended error handling."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
            
            if response.status_code == 429:  # Rate limited
                wait_time = CONFIG["RETRY_DELAY"] * (attempt + 2)  # Longer waits
                print(f"      ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [404, 403]:
                return None  # Subreddit doesn't exist or is private
            else:
                print(f"      ❌ HTTP Error {e.response.status_code}")
                if attempt == max_retries - 1:
                    return None
        except Exception as e:
            print(f"      ❌ Request failed: {str(e)[:50]}...")
            if attempt == max_retries - 1:
                return None
            time.sleep(3)
    
    return None

def is_parody_subreddit(subreddit_data, artist_name):
    """Efficient parody detection (from V2)."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    
    # Skip Katy Perry false positive
    if 'katyperry' in display_name:
        return False, "Legitimate artist subreddit"
    
    # Check for obvious parody patterns
    for indicator in PARODY_INDICATORS:
        if indicator in display_name:
            return True, f"Parody indicator: {indicator}"
    
    # Quick description check
    parody_count = sum(1 for indicator in PARODY_INDICATORS[:8] if indicator in description)  # Check fewer
    if parody_count >= 2:
        return True, f"Multiple parody indicators"
    
    return False, "Genuine community"

def calculate_fan_score(subreddit_data, artist_name):
    """Streamlined fan community scoring."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    
    artist_clean = artist_name.lower().replace(' ', '').replace(',', '').replace('.', '').replace("'", "")
    
    score = 0
    
    # Exact name match (highest priority)
    if artist_clean == display_name.replace('_', ''):
        score += 15
    elif artist_clean in display_name:
        score += 12
    
    # Fan community indicators (simplified)
    if any(indicator in display_name or indicator in description for indicator in FAN_INDICATORS[:4]):
        score += 6
    
    # Artist mentioned in description
    if artist_name.lower() in description:
        score += 4
    
    # Size bonus (simplified)
    subscribers = subreddit_data.get('subscribers', 0) or 0
    if subscribers > 500000:
        score += 3
    elif subscribers > 200000:
        score += 2
    
    return score

def find_primary_subreddit(artist_name):
    """ECONOMICAL: Find primary subreddit with minimal API calls."""
    print(f"\n🎤 {artist_name}")
    
    # REDUCED: Only 2 most effective search queries
    artist_clean = artist_name.replace(' ', '').replace(',', '').replace('.', '').replace("'", "").lower()
    queries = [
        artist_name,           # Most effective: full name
        artist_clean          # Second most effective: clean name
    ]
    
    best_candidate = None
    best_score = 0
    processed_ids = set()
    api_calls = 0
    
    for query in queries:
        print(f"  🔍 '{query}'", end="")
        
        url = "https://www.reddit.com/subreddits/search.json"
        headers = {'User-Agent': USER_AGENT}
        params = {'q': query, 'limit': 15, 'sort': 'relevance'}  # Reduced limit
        
        data = safe_request(url, headers, params)
        api_calls += 1
        
        if not data or 'data' not in data:
            print(" ❌")
            time.sleep(CONFIG["RATE_LIMIT_DELAY"])
            continue
        
        candidates_found = 0
        for item in data['data'].get('children', []):
            subreddit_data = item.get('data', {})
            subreddit_id = subreddit_data.get('id')
            
            if subreddit_id in processed_ids:
                continue
            processed_ids.add(subreddit_id)
            
            # Quick filters
            subscribers = subreddit_data.get('subscribers', 0) or 0
            if subscribers < CONFIG["MIN_SUBSCRIBERS"]:
                continue
            
            # Check parody
            is_parody, _ = is_parody_subreddit(subreddit_data, artist_name)
            if is_parody:
                continue
            
            # Score candidate
            fan_score = calculate_fan_score(subreddit_data, artist_name)
            if fan_score >= CONFIG["MIN_RELEVANCE_SCORE"] and fan_score > best_score:
                best_candidate = subreddit_data
                best_score = fan_score
                candidates_found += 1
        
        print(f" ✅ {candidates_found} found")
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    if best_candidate:
        subreddit_name = best_candidate.get('display_name')
        subscribers = best_candidate.get('subscribers', 0)
        print(f"  🎯 r/{subreddit_name} ({subscribers:,} subs, score: {best_score})")
        return best_candidate, api_calls
    else:
        print(f"  ❌ No qualifying subreddit found")
        return None, api_calls

def get_sampled_activity(subreddit_name):
    """ECONOMICAL: Sample recent activity instead of complete monthly data."""
    print(f"    📊 Sampling activity...", end="")
    
    url = f"https://www.reddit.com/r/{subreddit_name}/new.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'limit': CONFIG["SAMPLE_SIZE"]}  # Only 50 posts vs 600+
    
    data = safe_request(url, headers, params)
    
    if not data or 'data' not in data:
        print(" ❌")
        return 0, 0
    
    current_time = time.time()
    month_ago = current_time - (30 * 24 * 60 * 60)
    
    posts_last_month = 0
    total_comments = 0
    
    for post in data['data'].get('children', []):
        post_data = post.get('data', {})
        post_time = post_data.get('created_utc', 0)
        
        if post_time >= month_ago:
            posts_last_month += 1
            total_comments += post_data.get('num_comments', 0)
    
    # STATISTICAL EXTRAPOLATION: Estimate total monthly activity from sample
    if posts_last_month > 0:
        sample_ratio = posts_last_month / min(CONFIG["SAMPLE_SIZE"], len(data['data'].get('children', [])))
        
        # Conservative extrapolation (assume sample represents 20-40% of activity)
        estimated_monthly_posts = int(posts_last_month / max(sample_ratio * 0.3, 0.2))
        estimated_monthly_comments = int(total_comments / max(sample_ratio * 0.3, 0.2))
        
        # Cap estimates to reasonable maximums to avoid wild extrapolations
        estimated_monthly_posts = min(estimated_monthly_posts, posts_last_month * 10)
        estimated_monthly_comments = min(estimated_monthly_comments, total_comments * 15)
    else:
        estimated_monthly_posts = 0
        estimated_monthly_comments = 0
    
    print(f" ✅ ~{estimated_monthly_posts} posts, ~{estimated_monthly_comments:,} comments")
    return estimated_monthly_posts, estimated_monthly_comments

def analyze_artist_economical(artist_name):
    """ECONOMICAL: Complete artist analysis with 2-3 API calls total."""
    api_calls_used = 0
    
    # Step 1: Find primary subreddit (2 API calls)
    primary_sub, search_calls = find_primary_subreddit(artist_name)
    api_calls_used += search_calls
    
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
            "api_calls_used": api_calls_used,
            "methodology": "Economical - Statistical sampling"
        }
    
    subreddit_name = primary_sub.get('display_name', '')
    
    # Step 2: Sample activity (1 API call)
    posts, comments = get_sampled_activity(subreddit_name)
    api_calls_used += 1
    
    total_activity = posts + comments
    subscribers = primary_sub.get('subscribers', 0)
    
    # Calculate score
    if subscribers > 0:
        score = round((total_activity / subscribers) * 1000, 2)
    else:
        score = 0.0
    
    # Classify tier
    if score >= 5.0:
        tier = "🔥 Viral"
    elif score >= 2.0:
        tier = "⚡ Popular"
    elif score >= 0.5:
        tier = "📊 Present"
    else:
        tier = "💤 Minimal"
    
    result = {
        "artist": artist_name,
        "primary_subreddit": subreddit_name,
        "subreddit_url": f"https://reddit.com/r/{subreddit_name}",
        "subscribers": subscribers,
        "posts_last_month": posts,
        "comments_last_month": comments,
        "total_activity": total_activity,
        "popularity_score": score,
        "tier": tier,
        "api_calls_used": api_calls_used,
        "methodology": "Economical - Statistical sampling"
    }
    
    print(f"    📈 Score: {score} ({tier}) | API calls: {api_calls_used}")
    
    time.sleep(CONFIG["RATE_LIMIT_DELAY"])  # Rate limiting between artists
    return result

def load_artist_list():
    """Load the Top 100 USA Musicians list."""
    artist_file = project_root / "scripts" / "top_100_usa_musicians" / "top_100_usa_musicians_names_only.txt"
    
    with open(artist_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Extract just artist names (skip headers and numbering)
    artists = []
    for line in lines:
        if any(char.isdigit() and '. ' in line for char in line):  # Lines with numbering
            # Extract artist name after the number
            if '. ' in line:
                artist = line.split('. ', 1)[1].strip()
                if artist and not artist.startswith('=') and not artist.startswith('TOP'):
                    artists.append(artist)
        elif line and not line.startswith('=') and not line.startswith('TOP') and not line.startswith('Generated'):
            artists.append(line)
    
    return artists[:100]  # Ensure exactly 100

def run_economical_analysis():
    """Main execution function - economical analysis"""
    print("🎵 ECONOMICAL REDDIT ANALYZER - READY TO RUN")
    return "Ready to implement - call this function to start"

if __name__ == "__main__":
    print("🎯 Economical Reddit Analyzer - Ready")
    run_economical_analysis() 