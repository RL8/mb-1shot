#!/usr/bin/env python3
"""
Reddit Artist Subreddit Finder - Simplified Criteria

EXCLUSION CRITERIA:
- Less than 50K subscribers

ASSESSMENT CRITERIA:  
- Activity Score = Posts + Comments in last month
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

# Config
MIN_SUBSCRIBERS = 50000
RATE_DELAY = 1.5

def search_subreddits(query, limit=20):
    """Search subreddits via public API."""
    url = "https://www.reddit.com/subreddits/search.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'q': query, 'limit': limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def get_activity_metrics(subreddit_name):
    """Get posts + comments from last month."""
    url = f"https://www.reddit.com/r/{subreddit_name}/new.json"
    headers = {'User-Agent': USER_AGENT}
    params = {'limit': 50}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' not in data:
            return 0, 0, 0
        
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
        
        activity_score = posts_last_month + total_comments
        return posts_last_month, total_comments, activity_score
        
    except Exception as e:
        print(f"      ⚠️ Activity check failed: {e}")
        return 0, 0, 0

def calculate_relevance(subreddit_data, artist_name):
    """Calculate relevance score."""
    display_name = subreddit_data.get('display_name', '').lower()
    description = (subreddit_data.get('public_description') or '').lower()
    
    artist_lower = artist_name.lower()
    artist_clean = artist_lower.replace(' ', '')
    
    score = 0
    reasons = []
    
    if artist_clean == display_name:
        score += 10
        reasons.append("Exact match")
    elif artist_lower in display_name:
        score += 8
        reasons.append("Name in title")
    
    if any(word in display_name for word in ['fans', 'fan', 'official', 'music']):
        score += 3
        reasons.append("Fan community")
    
    if artist_lower in description:
        score += 2
        reasons.append("Mentioned in description")
    
    return score, " | ".join(reasons)

def analyze_artist(artist_name):
    """Analyze subreddits for an artist with simplified criteria."""
    print(f"\n🎤 {artist_name}")
    print("-" * 40)
    
    queries = [
        artist_name,
        f"{artist_name} fans",
        f"{artist_name} music",
        artist_name.replace(' ', '').lower()
    ]
    
    qualifying_subs = []
    processed_ids = set()
    
    for query in queries:
        print(f"  🔍 '{query}'")
        
        data = search_subreddits(query, 20)
        if not data or 'data' not in data:
            continue
        
        found = len(data['data'].get('children', []))
        print(f"    Found {found} results")
        
        for item in data['data'].get('children', []):
            sub_data = item.get('data', {})
            sub_id = sub_data.get('id')
            
            if sub_id in processed_ids:
                continue
            processed_ids.add(sub_id)
            
            # Check 50K minimum
            subscribers = sub_data.get('subscribers', 0) or 0
            sub_name = sub_data.get('display_name', 'unknown')
            
            if subscribers < MIN_SUBSCRIBERS:
                print(f"      ⏭️ r/{sub_name}: {subscribers:,} subscribers (< 50K)")
                continue
            
            print(f"      ✅ r/{sub_name}: {subscribers:,} subscribers (≥ 50K)")
            print(f"        📊 Checking activity...")
            
            # Get activity
            posts, comments, activity = get_activity_metrics(sub_name)
            relevance_score, reasons = calculate_relevance(sub_data, artist_name)
            
            result = {
                "artist": artist_name,
                "subreddit": sub_name,
                "url": f"https://reddit.com/r/{sub_name}",
                "subscribers": subscribers,
                "posts_last_month": posts,
                "comments_last_month": comments,
                "activity_score": activity,
                "relevance_score": relevance_score,
                "relevance_reasons": reasons,
                "description": (sub_data.get('public_description') or '')[:150]
            }
            
            qualifying_subs.append(result)
            print(f"        📈 Activity: {activity} (Posts: {posts}, Comments: {comments})")
        
        time.sleep(RATE_DELAY)
    
    # Sort by activity score
    qualifying_subs.sort(key=lambda x: x['activity_score'], reverse=True)
    
    print(f"  ✅ {len(qualifying_subs)} qualifying subreddits found")
    return qualifying_subs

def save_results(results, filename):
    """Save to JSON and CSV."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    json_file = OUTPUT_DIR / f"{filename}_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"📄 Saved: {json_file}")
    
    if results:
        csv_file = OUTPUT_DIR / f"{filename}_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"📊 Saved: {csv_file}")

def main():
    print("🎵 REDDIT SUBREDDIT FINDER - SIMPLIFIED CRITERIA")
    print("=" * 60)
    print("📋 NEW CRITERIA:")
    print("   • EXCLUSION: Less than 50K subscribers")
    print("   • ASSESSMENT: Activity = Posts + Comments (last 30 days)")
    print("=" * 60)
    
    artists = ["Taylor Swift", "Billie Eilish", "Dua Lipa", "Kendrick Lamar", "Drake"]
    
    all_results = {}
    all_combined = []
    start_time = time.time()
    
    try:
        for i, artist in enumerate(artists, 1):
            print(f"\n[{i}/{len(artists)}] Processing: {artist}")
            results = analyze_artist(artist)
            all_results[artist] = results
            all_combined.extend(results)
        
        # Save results
        if all_combined:
            save_results(all_combined, "simplified_criteria_results")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS SUMMARY")
        print("=" * 60)
        
        total_qualifying = len(all_combined)
        print(f"🎯 Artists analyzed: {len(artists)}")
        print(f"📍 Total qualifying subreddits: {total_qualifying}")
        
        print(f"\n📈 Results per artist:")
        for artist, subs in all_results.items():
            print(f"   • {artist}: {len(subs)} subreddits")
        
        if all_combined:
            # Show detailed results
            print(f"\n📋 DETAILED RESULTS:")
            for artist, subs in all_results.items():
                if subs:
                    print(f"\n🎤 {artist}:")
                    for i, sub in enumerate(subs, 1):
                        print(f"   {i}. r/{sub['subreddit']}")
                        print(f"      👥 {sub['subscribers']:,} subscribers")
                        print(f"      📊 Activity: {sub['activity_score']} (Posts: {sub['posts_last_month']}, Comments: {sub['comments_last_month']})")
                        print(f"      ⭐ Relevance: {sub['relevance_score']}/10 - {sub['relevance_reasons']}")
                else:
                    print(f"\n🎤 {artist}: No subreddits meet 50K criteria")
            
            # Top by activity
            top_active = sorted(all_combined, key=lambda x: x['activity_score'], reverse=True)[:5]
            print(f"\n🏆 TOP 5 BY ACTIVITY:")
            for i, sub in enumerate(top_active, 1):
                print(f"   {i}. r/{sub['subreddit']} ({sub['artist']}) - Activity: {sub['activity_score']}")
        
        end_time = time.time()
        print(f"\n⏱️ Analysis completed in {end_time - start_time:.1f} seconds")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Analysis interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 