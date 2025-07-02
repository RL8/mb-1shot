#!/usr/bin/env python3
"""
Reddit Artist Batch Processor

Processes specific ranges of artists from the top 100 USA musicians list
with improved rate limiting to avoid 429 errors.

Usage:
    python reddit_batch_processor.py --start 45 --end 70
    python reddit_batch_processor.py --start 71 --end 100
"""

import requests
import time
import datetime
import json
import os
import argparse
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

# Improved configuration for batch processing
CONFIG = {
    "MIN_SUBSCRIBERS": 50000,
    "MIN_RELEVANCE_SCORE": 8,
    "RATE_LIMIT_DELAY": 3.0,  # Slower rate limiting
    "REQUEST_TIMEOUT": 15,
    "ACTIVITY_CHECK_LIMIT": 50,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 10
}

def load_artist_list():
    """Load and parse the top 100 USA musicians from file."""
    artists_file = project_root / "top_100_usa_musicians_names_only.txt"
    
    artists = []
    with open(artists_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            match = re.match(r'^\s*\d+\.\s*(.+)$', line)
            if match:
                artist_name = match.group(1).strip()
                artists.append(artist_name)
    
    return artists

def calculate_artist_score(posts_last_month, comments_last_month, total_subscribers):
    """Core scoring function"""
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

def safe_request(url, headers, params, max_retries=3):
    """Make a request with retry logic for rate limiting."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
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

def search_subreddits(query, limit=10):
    """Search subreddits with retry logic."""
    url = "https://www.reddit.com/subreddits/search.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'q': query, 'limit': limit}
    return safe_request(url, headers, params)

def get_monthly_activity(subreddit_name):
    """Get posts + comments from last 30 days with retry logic."""
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

def calculate_relevance_score(subreddit_data, artist_name):
    """Calculate relevance score."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    
    artist_lower = artist_name.lower()
    artist_clean = artist_lower.replace(' ', '').replace(',', '').replace('.', '').replace("'", "")
    
    score = 0
    reasons = []
    
    if artist_clean == display_name:
        score += 10
        reasons.append("Exact match")
    elif artist_lower in display_name:
        score += 8
        reasons.append("Name in title")
    
    if any(word in display_name for word in ['fans', 'fan', 'official']):
        score += 3
        reasons.append("Fan community")
    
    if artist_lower in description:
        score += 2
        reasons.append("Artist mentioned")
    
    return score, " | ".join(reasons) if reasons else "No clear relevance"

def find_primary_subreddit(artist_name):
    """Find the primary dedicated subreddit for an artist."""
    print(f"🎤 {artist_name}", end=" ", flush=True)
    
    artist_clean = artist_name.replace(' ', '').replace(',', '').replace('.', '').replace("'", "").lower()
    queries = [artist_name, artist_clean]
    
    candidates = []
    processed_ids = set()
    
    for query in queries:
        data = search_subreddits(query, 10)
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
            
            relevance_score, relevance_reasons = calculate_relevance_score(subreddit_data, artist_name)
            
            if relevance_score >= CONFIG["MIN_RELEVANCE_SCORE"]:
                candidates.append({
                    'data': subreddit_data,
                    'relevance_score': relevance_score,
                    'relevance_reasons': relevance_reasons,
                    'subscribers': subscribers
                })
        
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    if not candidates:
        print("❌")
        return None
    
    primary = max(candidates, key=lambda x: x['subscribers'])
    print(f"✅ r/{primary['data'].get('display_name')}")
    
    return primary

def score_artist(artist_name):
    """Score an artist using the methodology."""
    primary_sub = find_primary_subreddit(artist_name)
    
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
            "relevance_score": 0,
            "relevance_reasons": "No qualifying subreddit found"
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
        "relevance_score": primary_sub['relevance_score'],
        "relevance_reasons": primary_sub['relevance_reasons']
    }

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Process a batch of artists')
    parser.add_argument('--start', type=int, required=True, help='Starting artist index (1-based)')
    parser.add_argument('--end', type=int, required=True, help='Ending artist index (1-based, inclusive)')
    
    args = parser.parse_args()
    
    print(f"🎵 REDDIT BATCH PROCESSOR - Artists {args.start}-{args.end}")
    print("=" * 60)
    
    artists = load_artist_list()
    start_idx = args.start - 1
    end_idx = args.end - 1
    
    batch_artists = artists[start_idx:end_idx + 1]
    
    print(f"\n🎯 Processing {len(batch_artists)} artists...")
    print("-" * 60)
    
    results = []
    start_time = time.time()
    
    try:
        for i, artist in enumerate(batch_artists, 1):
            actual_index = start_idx + i
            print(f"[{actual_index:3d}/100] ", end="", flush=True)
            
            artist_result = score_artist(artist)
            results.append(artist_result)
            
            if i % 5 == 0:
                elapsed = time.time() - start_time
                print(f"\n    📊 Progress: {i}/{len(batch_artists)} - {elapsed:.1f}s elapsed")
        
        results.sort(key=lambda x: x["popularity_score"], reverse=True)
        
        # Save batch results
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = OUTPUT_DIR / f"batch_{args.start}-{args.end}_{timestamp}.json"
        
        batch_output = {
            "batch_info": {
                "start_index": args.start,
                "end_index": args.end,
                "total_in_batch": len(batch_artists)
            },
            "analysis_date": datetime.datetime.now().isoformat(),
            "methodology": "Single Primary Subreddit - Engagement Density",
            "artists_sorted_by_score": results
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(batch_output, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Saved: {json_file}")
        
        with_scores = sum(1 for a in results if a["popularity_score"] > 0)
        print(f"\n✅ Found {with_scores} artists with Reddit presence")
        
        if with_scores > 0:
            print(f"\n🏆 Top 5 in this batch:")
            for i, artist in enumerate(results[:5], 1):
                if artist['popularity_score'] > 0:
                    print(f"   {i}. {artist['artist']}: {artist['popularity_score']} ({artist['tier']})")
        
        end_time = time.time()
        print(f"\n⏱️ Batch completed in {end_time - start_time:.1f} seconds")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Interrupted")

if __name__ == "__main__":
    main() 