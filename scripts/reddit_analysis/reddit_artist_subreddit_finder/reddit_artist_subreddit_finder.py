#!/usr/bin/env python3
"""
Reddit Artist Subreddit Finder for Music Besties

This script discovers and analyzes artist fan subreddits using the Reddit API.
It integrates with the Music Besties project configuration and saves results
in the project's data structure.

Requirements:
- Install dependencies: pip install -r requirements.txt

Usage:
    python reddit_artist_subreddit_finder.py
"""

import praw
import time
import datetime
from collections import defaultdict
import json
import csv
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

print(f"📁 Loading config from: {env_path}")

# --- REDDIT API CONFIGURATION FROM ENV ---
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET') 
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

# Validate credentials
if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
    print("❌ ERROR: Reddit API credentials not found in .env file!")
    print("Please ensure these variables are set:")
    print("  - REDDIT_CLIENT_ID")
    print("  - REDDIT_CLIENT_SECRET") 
    print("  - REDDIT_USER_AGENT")
    sys.exit(1)

print(f"✅ Reddit API credentials loaded successfully")
print(f"   Client ID: {REDDIT_CLIENT_ID[:8]}...")
print(f"   User Agent: {REDDIT_USER_AGENT}")

# --- ENHANCED CONFIGURATION PARAMETERS ---
CONFIG = {
    "SUBREDDIT_SEARCH_LIMIT": 20,
    "POST_ACTIVITY_CHECK_LIMIT": 15,
    "MIN_SUBSCRIBERS_FOR_CONSIDERATION": 50,
    "MIN_AVG_COMMENTS_PER_POST": 1.5,
    "MIN_HOT_POST_AGE_HOURS": 48,
    "RATE_LIMIT_DELAY": 1.2,
    "RELEVANCE_WEIGHT": 0.65,
    "ACTIVITY_WEIGHT": 0.35,
    "FINAL_CONFIDENCE_THRESHOLD": 4.5,
    "FINAL_CONFIDENCE_THRESHOLD_SMALL_ACTIVE": 2.5,
    "MAX_ARTISTS_PER_RUN": 25,
}

# --- OUTPUT DIRECTORY ---
OUTPUT_DIR = project_root / "dev stuff" / "data-scripts" / "reddit_results"
OUTPUT_DIR.mkdir(exist_ok=True)

# --- INITIALIZE REDDIT API ---
try:
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    # Test connection
    print(f"✅ Reddit API connection established")
except Exception as e:
    print(f"❌ ERROR: Failed to connect to Reddit API: {e}")
    sys.exit(1)

def safe_filename(name):
    """Convert string to safe filename."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '.', '_')).rstrip().replace(' ', '_')

def get_timestamp():
    """Get formatted timestamp."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

def find_artist_subreddits(artist_name):
    """Find and analyze subreddits for an artist."""
    print(f"\n🎵 Searching for: {artist_name}")
    
    # Generate search queries
    queries = [
        artist_name,
        f"{artist_name} fans",
        f"{artist_name} music",
        artist_name.replace(' ', '').lower(),
        f"{artist_name.replace(' ', '').lower()}fans"
    ]
    
    found_subreddits = []
    processed_ids = set()
    
    for query in queries:
        print(f"  🔍 Query: '{query}'")
        try:
            for subreddit in reddit.subreddits.search(query=query, limit=CONFIG["SUBREDDIT_SEARCH_LIMIT"]):
                if subreddit.id in processed_ids:
                    continue
                processed_ids.add(subreddit.id)
                
                # Calculate relevance score
                relevance = 0
                display_name = subreddit.display_name.lower()
                description = (subreddit.public_description or "").lower()
                
                if artist_name.lower() in display_name:
                    relevance += 5
                if "fans" in display_name or "music" in display_name:
                    relevance += 2
                if artist_name.lower() in description:
                    relevance += 2
                
                # Check activity
                try:
                    hot_posts = list(subreddit.hot(limit=5))
                    if hot_posts:
                        avg_comments = sum(p.num_comments for p in hot_posts) / len(hot_posts)
                        recent_activity = any((time.time() - p.created_utc) < 86400 for p in hot_posts)
                    else:
                        avg_comments = 0
                        recent_activity = False
                except:
                    avg_comments = 0
                    recent_activity = False
                
                # Calculate final score
                activity_score = 0
                if avg_comments >= CONFIG["MIN_AVG_COMMENTS_PER_POST"]:
                    activity_score += 2
                if recent_activity:
                    activity_score += 2
                if subreddit.subscribers > 1000:
                    activity_score += 1
                
                confidence = (relevance * CONFIG["RELEVANCE_WEIGHT"] + 
                            activity_score * CONFIG["ACTIVITY_WEIGHT"])
                
                if confidence > CONFIG["FINAL_CONFIDENCE_THRESHOLD"] or \
                   (confidence > CONFIG["FINAL_CONFIDENCE_THRESHOLD_SMALL_ACTIVE"] and avg_comments > 0):
                    
                    found_subreddits.append({
                        "artist": artist_name,
                        "subreddit": subreddit.display_name,
                        "url": f"https://reddit.com/r/{subreddit.display_name}",
                        "subscribers": subreddit.subscribers,
                        "relevance_score": relevance,
                        "activity_score": activity_score,
                        "confidence_score": round(confidence, 2),
                        "avg_comments": round(avg_comments, 1),
                        "description": (subreddit.public_description or "")[:200]
                    })
                
                time.sleep(CONFIG["RATE_LIMIT_DELAY"])
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            time.sleep(CONFIG["RATE_LIMIT_DELAY"] * 2)
    
    # Sort by confidence score
    found_subreddits.sort(key=lambda x: x['confidence_score'], reverse=True)
    print(f"  ✅ Found {len(found_subreddits)} qualifying subreddits")
    
    return found_subreddits

def save_results(results, filename):
    """Save results to JSON and CSV."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON
    json_file = OUTPUT_DIR / f"{filename}_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"📄 Saved JSON: {json_file}")
    
    # Save CSV
    if results:
        csv_file = OUTPUT_DIR / f"{filename}_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"📊 Saved CSV: {csv_file}")

if __name__ == "__main__":
    print("🎵 MUSIC BESTIES - Reddit Artist Subreddit Discovery")
    print(f"📅 {get_timestamp()}")
    print("📋 Key improvements over original script:")
    print("   ✅ Uses environment variables from .env")
    print("   ✅ Enhanced error handling")
    print("   ✅ Improved scoring algorithm")
    print("   ✅ Better project integration")
    print("   ✅ Updated artist list")
    
    # Updated diverse artist list for Music Besties
    artists = [
        # Pop/Mainstream
        "Taylor Swift", "Billie Eilish", "Dua Lipa", "Olivia Rodrigo", "Harry Styles",
        
        # Hip-Hop/Rap  
        "Kendrick Lamar", "Drake", "Tyler The Creator", "J. Cole", "Childish Gambino",
        
        # Rock/Alternative
        "Arctic Monkeys", "Tame Impala", "The 1975", "Radiohead", 
        
        # Electronic/Dance
        "Daft Punk", "Flume", "ODESZA", "Disclosure",
        
        # Indie/Alternative
        "Phoebe Bridgers", "Mac Miller", "Frank Ocean", "Bon Iver",
        
        # R&B/Soul
        "The Weeknd", "SZA", "Anderson .Paak", "H.E.R."
    ]
    
    print(f"\n🎯 Discovering subreddits for {len(artists)} artists...")
    print(f"📁 Results will be saved to: {OUTPUT_DIR}")
    
    all_results = []
    start_time = time.time()
    
    try:
        for i, artist in enumerate(artists, 1):
            print(f"\n[{i}/{len(artists)}] Processing: {artist}")
            artist_results = find_artist_subreddits(artist)
            all_results.extend(artist_results)
        
        # Save all results
        save_results(all_results, "reddit_subreddits_discovery")
        
        # Print summary
        end_time = time.time()
        print(f"\n🎉 DISCOVERY COMPLETE!")
        print(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
        print(f"📊 Total subreddits found: {len(all_results)}")
        print(f"📁 Results saved to: {OUTPUT_DIR}")
        
        if all_results:
            print(f"\n📈 TOP DISCOVERIES:")
            top_results = sorted(all_results, key=lambda x: x['confidence_score'], reverse=True)[:10]
            for result in top_results:
                print(f"  🎵 {result['artist']}: r/{result['subreddit']} ({result['subscribers']:,} subs, {result['confidence_score']} score)")
        
        print(f"\n✅ Reddit subreddit discovery completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Discovery interrupted by user")
    except Exception as e:
        print(f"\n❌ Discovery failed: {e}")
        sys.exit(1) 