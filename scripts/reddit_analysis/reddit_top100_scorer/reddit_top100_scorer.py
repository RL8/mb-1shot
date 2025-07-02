#!/usr/bin/env python3
"""
Reddit Top 100 USA Musicians Scorer

Processes the top 100 USA musicians list and scores them using the
Single Primary Subreddit methodology, outputting results sorted by score.

Usage:
    python reddit_top100_scorer.py
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

# Configuration
CONFIG = {
    "MIN_SUBSCRIBERS": 50000,
    "MIN_RELEVANCE_SCORE": 8,
    "RATE_LIMIT_DELAY": 1.2,
    "REQUEST_TIMEOUT": 10,
    "ACTIVITY_CHECK_LIMIT": 50
}

def load_artist_list():
    """Load and parse the top 100 USA musicians from file."""
    artists_file = project_root / "top_100_usa_musicians_names_only.txt"
    
    if not artists_file.exists():
        print(f"❌ Artist file not found: {artists_file}")
        return []
    
    artists = []
    with open(artists_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Look for numbered lines like "1. Artist Name"
            match = re.match(r'^\s*\d+\.\s*(.+)$', line)
            if match:
                artist_name = match.group(1).strip()
                artists.append(artist_name)
    
    print(f"📋 Loaded {len(artists)} artists from file")
    return artists

def calculate_artist_score(posts_last_month, comments_last_month, total_subscribers):
    """Core scoring function: (Monthly Activity ÷ Total Subscribers) × 1000"""
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

def search_subreddits(query, limit=15):
    """Search subreddits using public Reddit API."""
    url = "https://www.reddit.com/subreddits/search.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'q': query, 'limit': limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"    ❌ Search Error: {e}")
        return None

def get_monthly_activity(subreddit_name):
    """Get posts + comments from last 30 days."""
    url = f"https://www.reddit.com/r/{subreddit_name}/new.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'limit': CONFIG["ACTIVITY_CHECK_LIMIT"]}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
        response.raise_for_status()
        data = response.json()
        
        if 'data' not in data:
            return 0, 0
        
        posts = data['data']['children']
        current_time = time.time()
        month_ago = current_time - (30 * 24 * 60 * 60)  # 30 days ago
        
        posts_last_month = 0
        total_comments = 0
        
        for post in posts:
            post_data = post.get('data', {})
            post_time = post_data.get('created_utc', 0)
            
            if post_time >= month_ago:
                posts_last_month += 1
                total_comments += post_data.get('num_comments', 0)
        
        return posts_last_month, total_comments
        
    except Exception as e:
        print(f"      ⚠️ Activity check failed: {e}")
        return 0, 0

def calculate_relevance_score(subreddit_data, artist_name):
    """Calculate relevance score for artist-subreddit match."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    
    artist_lower = artist_name.lower()
    artist_clean = artist_lower.replace(' ', '').replace(',', '').replace('.', '')
    
    score = 0
    reasons = []
    
    # Exact matches (highest priority)
    if artist_clean == display_name:
        score += 10
        reasons.append("Exact match")
    elif artist_lower in display_name:
        score += 8
        reasons.append("Name in title")
    
    # Fan community indicators
    if any(word in display_name for word in ['fans', 'fan', 'official']):
        score += 3
        reasons.append("Fan community")
    
    # Description mentions
    if artist_lower in description:
        score += 2
        reasons.append("Artist mentioned")
    
    return score, " | ".join(reasons) if reasons else "No clear relevance"

def find_primary_subreddit(artist_name):
    """Find the primary dedicated subreddit for an artist."""
    print(f"🎤 {artist_name}", end=" ", flush=True)
    
    # Generate search queries
    artist_clean = artist_name.replace(' ', '').replace(',', '').replace('.', '').lower()
    queries = [
        artist_name,
        artist_clean,
        f"{artist_name} fans"
    ]
    
    candidates = []
    processed_ids = set()
    
    for query in queries:
        data = search_subreddits(query, 15)  # Reduced to speed up
        if not data or 'data' not in data:
            continue
        
        for item in data['data'].get('children', []):
            subreddit_data = item.get('data', {})
            subreddit_id = subreddit_data.get('id')
            
            if subreddit_id in processed_ids:
                continue
            processed_ids.add(subreddit_id)
            
            # Apply minimum subscriber filter
            subscribers = subreddit_data.get('subscribers', 0) or 0
            if subscribers < CONFIG["MIN_SUBSCRIBERS"]:
                continue
            
            # Calculate relevance
            relevance_score, relevance_reasons = calculate_relevance_score(subreddit_data, artist_name)
            
            # Only consider highly relevant subreddits
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
    
    # Select primary subreddit (highest subscribers among relevant candidates)
    primary = max(candidates, key=lambda x: x['subscribers'])
    print(f"✅ r/{primary['data'].get('display_name')}")
    
    return primary

def score_artist(artist_name):
    """Score an artist using the Single Primary Subreddit methodology."""
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
    
    # Get activity metrics
    posts, comments = get_monthly_activity(subreddit_name)
    total_activity = posts + comments
    
    # Calculate score
    score = calculate_artist_score(posts, comments, primary_sub['subscribers'])
    tier = get_tier_classification(score)
    
    result = {
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
    
    return result

def main():
    """Main execution function."""
    print("🎵 REDDIT TOP 100 USA MUSICIANS SCORER")
    print("=" * 60)
    print("📋 Methodology: Single Primary Subreddit - Engagement Density")
    print("🎯 Score = (Monthly Activity ÷ Subscribers) × 1000")
    print("=" * 60)
    
    # Load artist list from file
    artists = load_artist_list()
    
    if not artists:
        print("❌ No artists loaded. Exiting.")
        return
    
    print(f"\n🎯 Processing {len(artists)} artists...")
    print("Format: Artist Name [Status] Subreddit")
    print("-" * 60)
    
    results = {
        "analysis_date": datetime.datetime.now().isoformat(),
        "methodology": "Single Primary Subreddit - Engagement Density",
        "total_artists_analyzed": len(artists),
        "scoring_criteria": {
            "min_subscribers": CONFIG["MIN_SUBSCRIBERS"],
            "min_relevance_score": CONFIG["MIN_RELEVANCE_SCORE"],
            "activity_period": "30 days",
            "score_formula": "(Monthly Activity ÷ Subscribers) × 1000"
        },
        "artist_scores": []
    }
    
    start_time = time.time()
    
    try:
        for i, artist in enumerate(artists, 1):
            print(f"[{i:3d}/100] ", end="", flush=True)
            
            artist_result = score_artist(artist)
            results["artist_scores"].append(artist_result)
            
            # Progress update every 10 artists
            if i % 10 == 0:
                elapsed = time.time() - start_time
                print(f"\n    📊 Progress: {i}/100 ({i}%) - {elapsed:.1f}s elapsed")
        
        # Sort by popularity score (descending)
        results["artist_scores"].sort(key=lambda x: x["popularity_score"], reverse=True)
        
        # Calculate tier distribution
        tier_counts = {}
        for score in results["artist_scores"]:
            tier = score["tier"]
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        results["tier_distribution"] = tier_counts
        results["top_10_by_score"] = results["artist_scores"][:10]
        
        # Save main results file
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = OUTPUT_DIR / f"top100_usa_musicians_reddit_scores_{timestamp}.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Saved: {json_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 ANALYSIS COMPLETE")
        print("=" * 60)
        
        print(f"\n🎯 Total Artists: {len(artists)}")
        with_scores = sum(1 for a in results["artist_scores"] if a["popularity_score"] > 0)
        print(f"✅ Artists with Reddit presence: {with_scores}")
        print(f"❌ Artists with no presence: {len(artists) - with_scores}")
        
        print(f"\n📈 Tier Distribution:")
        for tier, count in tier_counts.items():
            print(f"   • {tier}: {count} artists")
        
        print(f"\n🏆 Top 10 by Reddit Engagement Score:")
        for i, artist in enumerate(results["artist_scores"][:10], 1):
            print(f"   {i:2d}. {artist['artist']}: {artist['popularity_score']} ({artist['tier']})")
        
        end_time = time.time()
        print(f"\n⏱️ Total analysis time: {end_time - start_time:.1f} seconds")
        print(f"⚡ Average time per artist: {(end_time - start_time)/len(artists):.1f}s")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Analysis interrupted by user")
        # Save partial results
        if results["artist_scores"]:
            json_file = OUTPUT_DIR / f"top100_partial_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved partial results: {json_file}")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 