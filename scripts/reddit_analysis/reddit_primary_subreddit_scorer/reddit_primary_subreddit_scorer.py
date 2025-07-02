#!/usr/bin/env python3
"""
Reddit Artist Primary Subreddit Scorer

Implementation of the Single Primary Subreddit methodology for assessing
artist popularity on Reddit through engagement density scoring.

Based on methodology documented in REDDIT_ARTIST_SCORING_METHODOLOGY.md

Usage:
    python reddit_primary_subreddit_scorer.py
"""

import requests
import time
import datetime
import json
import csv
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

# Configuration
CONFIG = {
    "MIN_SUBSCRIBERS": 50000,
    "MIN_RELEVANCE_SCORE": 8,
    "RATE_LIMIT_DELAY": 1.5,
    "REQUEST_TIMEOUT": 10,
    "ACTIVITY_CHECK_LIMIT": 50
}

def calculate_artist_score(posts_last_month, comments_last_month, total_subscribers):
    """
    Core scoring function: (Monthly Activity ÷ Total Subscribers) × 1000
    
    Args:
        posts_last_month (int): Number of posts in last 30 days
        comments_last_month (int): Number of comments in last 30 days  
        total_subscribers (int): Total subreddit subscribers
        
    Returns:
        float: Engagement density score
    """
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

def search_subreddits(query, limit=20):
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
    artist_clean = artist_lower.replace(' ', '')
    
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
    """
    Find the primary dedicated subreddit for an artist.
    
    Args:
        artist_name (str): Artist name to search for
        
    Returns:
        dict or None: Primary subreddit data or None if not found
    """
    print(f"\n🎤 Analyzing: {artist_name}")
    
    # Generate search queries
    artist_clean = artist_name.replace(' ', '').lower()
    queries = [
        artist_name,
        artist_clean,
        f"{artist_name} fans",
        f"{artist_clean}fans",
        f"{artist_name} music"
    ]
    
    candidates = []
    processed_ids = set()
    
    for query in queries:
        print(f"  🔍 Searching: '{query}'")
        
        data = search_subreddits(query, 20)
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
                print(f"    ✅ Found: r/{subreddit_data.get('display_name')} ({subscribers:,} subs, relevance: {relevance_score})")
        
        time.sleep(CONFIG["RATE_LIMIT_DELAY"])
    
    if not candidates:
        print(f"    ❌ No qualifying subreddits found (min 50K subs, 8+ relevance)")
        return None
    
    # Select primary subreddit (highest subscribers among relevant candidates)
    primary = max(candidates, key=lambda x: x['subscribers'])
    print(f"    🎯 Primary: r/{primary['data'].get('display_name')} ({primary['subscribers']:,} subscribers)")
    
    return primary

def score_artist(artist_name):
    """
    Score an artist using the Single Primary Subreddit methodology.
    
    Args:
        artist_name (str): Artist name to analyze
        
    Returns:
        dict: Complete scoring result or None if no qualifying subreddit
    """
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
    
    print(f"    📊 Analyzing activity for r/{subreddit_name}...")
    
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
    
    print(f"    📈 Score: {score} ({tier}) - Activity: {total_activity} over {primary_sub['subscribers']:,} subscribers")
    
    return result

def save_results(results, filename="primary_subreddit_scores"):
    """Save results to JSON and CSV files."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON
    json_file = OUTPUT_DIR / f"{filename}_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"📄 Saved JSON: {json_file}")
    
    # Save CSV
    if results['artist_scores']:
        csv_file = OUTPUT_DIR / f"{filename}_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = results['artist_scores'][0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results['artist_scores'])
        print(f"📊 Saved CSV: {csv_file}")

def main():
    """Main execution function."""
    print("🎵 REDDIT PRIMARY SUBREDDIT SCORER")
    print("=" * 60)
    print("📋 Methodology: Single Primary Subreddit - Engagement Density")
    print("🎯 Score = (Monthly Activity ÷ Subscribers) × 1000")
    print("=" * 60)
    
    # Test artists (can be replaced with full artist list)
    test_artists = [
        "Taylor Swift",
        "Billie Eilish", 
        "Dua Lipa",
        "Kendrick Lamar",
        "Drake"
    ]
    
    print(f"\n🎯 Analyzing {len(test_artists)} artists...")
    
    results = {
        "analysis_date": datetime.datetime.now().isoformat(),
        "methodology": "Single Primary Subreddit - Engagement Density",
        "total_artists_analyzed": len(test_artists),
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
        for i, artist in enumerate(test_artists, 1):
            print(f"\n[{i}/{len(test_artists)}] Processing: {artist}")
            
            artist_result = score_artist(artist)
            results["artist_scores"].append(artist_result)
        
        # Calculate tier distribution
        tier_counts = {}
        for score in results["artist_scores"]:
            tier = score["tier"]
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        results["tier_distribution"] = tier_counts
        
        # Get top scores
        sorted_scores = sorted(results["artist_scores"], 
                             key=lambda x: x["popularity_score"], 
                             reverse=True)
        results["top_artists_by_score"] = sorted_scores[:10]
        
        # Save results
        save_results(results)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 ANALYSIS COMPLETE")
        print("=" * 60)
        
        print(f"\n🎯 Total Artists: {len(test_artists)}")
        print(f"📈 Tier Distribution:")
        for tier, count in tier_counts.items():
            print(f"   • {tier}: {count} artists")
        
        print(f"\n🏆 Top Artists by Score:")
        for i, artist in enumerate(sorted_scores[:5], 1):
            print(f"   {i}. {artist['artist']}: {artist['popularity_score']} ({artist['tier']})")
        
        end_time = time.time()
        print(f"\n⏱️ Analysis completed in {end_time - start_time:.1f} seconds")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 