#!/usr/bin/env python3
"""
Comprehensive Methodology Audit

Systematically checks our Reddit analysis methodology for all potential issues
to avoid duplicating work and ensure data quality.
"""

import json
import requests
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter, defaultdict

# Load environment
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'script:mb-script:v1.0 (by /u/tapinda)')

def load_current_data():
    """Load current Reddit analysis data."""
    data_file = project_root / "public" / "data" / "reddit_analysis.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def audit_data_patterns():
    """Audit 1: Check for suspicious data patterns."""
    print("🔍 AUDIT 1: DATA PATTERNS")
    print("=" * 50)
    
    data = load_current_data()
    results = data['artists_in_original_order']
    
    # Check post counts
    post_counts = [r['posts_last_month'] for r in results if r['posts_last_month'] > 0]
    post_counter = Counter(post_counts)
    
    print(f"📊 Post Count Distribution:")
    for count, frequency in sorted(post_counter.items()):
        if frequency > 1:
            print(f"   {count} posts: {frequency} artists {'⚠️' if count == 50 else ''}")
    
    # Check for exactly 50 posts (truncation issue)
    fifty_post_artists = [r for r in results if r['posts_last_month'] == 50]
    print(f"\n🚨 ISSUE FOUND: {len(fifty_post_artists)} artists with exactly 50 posts")
    print(f"   This indicates truncation for: {[r['artist'] for r in fifty_post_artists[:5]]}...")
    
    # Check comment patterns
    comment_ratios = []
    for r in results:
        if r['posts_last_month'] > 0:
            ratio = r['comments_last_month'] / r['posts_last_month']
            comment_ratios.append((r['artist'], ratio))
    
    # Look for unusually high comment ratios (might indicate calculation errors)
    high_ratio = [r for r in comment_ratios if r[1] > 100]
    if high_ratio:
        print(f"\n⚠️ SUSPICIOUS: High comment/post ratios:")
        for artist, ratio in sorted(high_ratio, key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {artist}: {ratio:.1f} comments per post")
    
    return fifty_post_artists

def audit_subreddit_relevance():
    """Audit 2: Check for irrelevant or incorrect subreddit matches."""
    print("\n🔍 AUDIT 2: SUBREDDIT RELEVANCE")
    print("=" * 50)
    
    data = load_current_data()
    results = [r for r in data['artists_in_original_order'] if r['primary_subreddit']]
    
    # Known problematic patterns
    problematic_patterns = [
        'type', 'thetype', 'meme', 'circlejerk', 'jerk', 'funny', 'humor',
        'hate', 'vs', 'versus', 'battle', 'cringe', 'mock'
    ]
    
    suspected_issues = []
    
    for result in results:
        subreddit = result['primary_subreddit'].lower()
        artist = result['artist']
        
        # Check for parody indicators
        for pattern in problematic_patterns:
            if pattern in subreddit:
                suspected_issues.append({
                    'artist': artist,
                    'subreddit': result['primary_subreddit'],
                    'issue': f"Contains '{pattern}' - likely parody/meme",
                    'priority': 'HIGH'
                })
        
        # Check for generic music subreddits that shouldn't be artist-specific
        generic_patterns = ['music', 'songs', 'hiphop', 'pop', 'rock']
        if any(pattern in subreddit for pattern in generic_patterns) and subreddit not in [artist.lower().replace(' ', '')]:
            suspected_issues.append({
                'artist': artist,
                'subreddit': result['primary_subreddit'],
                'issue': f"Generic music subreddit, not artist-specific",
                'priority': 'MEDIUM'
            })
    
    print(f"🚨 FOUND {len(suspected_issues)} potentially problematic subreddit matches:")
    for issue in suspected_issues:
        print(f"   {issue['priority']}: {issue['artist']} → r/{issue['subreddit']}")
        print(f"        {issue['issue']}")
    
    return suspected_issues

def audit_search_methodology():
    """Audit 3: Test if our search methodology finds the best subreddits."""
    print("\n🔍 AUDIT 3: SEARCH METHODOLOGY")
    print("=" * 50)
    
    # Test known artist-subreddit pairs
    known_correct = [
        ('Taylor Swift', 'TaylorSwift'),
        ('Drake', 'Drizzy'),
        ('Kanye West', 'Kanye'),
        ('Travis Scott', 'travisscott'),
        ('Kendrick Lamar', 'KendrickLamar')
    ]
    
    print("🧪 Testing if search finds known correct subreddits...")
    
    for artist, expected_subreddit in known_correct:
        print(f"\n   Testing: {artist}")
        
        # Simulate search
        queries = [
            artist,
            artist.replace(' ', '').lower(),
            f"{artist} fans",
            f"{artist} music"
        ]
        
        found_expected = False
        for query in queries:
            url = "https://www.reddit.com/subreddits/search.json"
            headers = {'User-Agent': USER_AGENT}
            params = {'q': query, 'limit': 20}
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                data = response.json()
                
                if 'data' in data:
                    subreddit_names = [item['data']['display_name'] for item in data['data']['children']]
                    if expected_subreddit in subreddit_names:
                        rank = subreddit_names.index(expected_subreddit) + 1
                        print(f"      ✅ Found r/{expected_subreddit} at rank {rank} for query '{query}'")
                        found_expected = True
                        break
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"      ❌ Search failed: {e}")
        
        if not found_expected:
            print(f"      🚨 ISSUE: r/{expected_subreddit} not found in top 20 results for {artist}")

def audit_scoring_calculation():
    """Audit 4: Verify scoring calculations are mathematically correct."""
    print("\n🔍 AUDIT 4: SCORING CALCULATIONS")
    print("=" * 50)
    
    data = load_current_data()
    
    calculation_errors = []
    
    for result in data['artists_in_original_order']:
        if result['popularity_score'] > 0:
            # Recalculate score
            posts = result['posts_last_month']
            comments = result['comments_last_month']
            subscribers = result['subscribers']
            
            expected_activity = posts + comments
            expected_score = (expected_activity / subscribers) * 1000 if subscribers > 0 else 0
            expected_score = round(expected_score, 2)
            
            actual_score = result['popularity_score']
            actual_activity = result['total_activity']
            
            # Check activity calculation
            if actual_activity != expected_activity:
                calculation_errors.append({
                    'artist': result['artist'],
                    'error': 'Activity calculation mismatch',
                    'expected': expected_activity,
                    'actual': actual_activity
                })
            
            # Check score calculation (allow small rounding differences)
            if abs(actual_score - expected_score) > 0.02:
                calculation_errors.append({
                    'artist': result['artist'],
                    'error': 'Score calculation mismatch',
                    'expected': expected_score,
                    'actual': actual_score
                })
    
    if calculation_errors:
        print(f"🚨 FOUND {len(calculation_errors)} calculation errors:")
        for error in calculation_errors[:5]:  # Show first 5
            print(f"   {error['artist']}: {error['error']}")
            print(f"      Expected: {error['expected']}, Actual: {error['actual']}")
    else:
        print("✅ All scoring calculations appear correct")

def audit_tier_classification():
    """Audit 5: Check tier classification consistency."""
    print("\n🔍 AUDIT 5: TIER CLASSIFICATION")
    print("=" * 50)
    
    data = load_current_data()
    
    tier_errors = []
    
    for result in data['artists_in_original_order']:
        score = result['popularity_score']
        tier = result['tier']
        
        # Define expected tier
        if score >= 5.0:
            expected_tier = "🔥 Viral"
        elif score >= 2.0:
            expected_tier = "⚡ Popular"
        elif score >= 0.5:
            expected_tier = "📊 Present"
        elif score > 0:
            expected_tier = "💤 Minimal"
        else:
            expected_tier = "❌ No Presence"
        
        if tier != expected_tier:
            tier_errors.append({
                'artist': result['artist'],
                'score': score,
                'expected_tier': expected_tier,
                'actual_tier': tier
            })
    
    if tier_errors:
        print(f"🚨 FOUND {len(tier_errors)} tier classification errors:")
        for error in tier_errors[:5]:
            print(f"   {error['artist']}: Score {error['score']} should be {error['expected_tier']}, got {error['actual_tier']}")
    else:
        print("✅ All tier classifications appear correct")

def audit_api_limitations():
    """Audit 6: Check for API and rate limiting issues."""
    print("\n🔍 AUDIT 6: API LIMITATIONS")
    print("=" * 50)
    
    data = load_current_data()
    
    # Check for artists with suspiciously low subscriber counts (might indicate API failures)
    low_sub_artists = [r for r in data['artists_in_original_order'] if r['primary_subreddit'] and r['subscribers'] < 1000]
    
    if low_sub_artists:
        print(f"⚠️ {len(low_sub_artists)} artists have <1000 subscribers:")
        for artist in low_sub_artists[:5]:
            print(f"   {artist['artist']}: r/{artist['primary_subreddit']} ({artist['subscribers']} subs)")
        print("   These might be failed API calls or genuinely small subreddits")
    
    # Check for zero activity (might indicate API failures)
    zero_activity = [r for r in data['artists_in_original_order'] if r['primary_subreddit'] and r['total_activity'] == 0]
    
    if zero_activity:
        print(f"⚠️ {len(zero_activity)} artists have zero activity:")
        for artist in zero_activity[:5]:
            print(f"   {artist['artist']}: r/{artist['primary_subreddit']}")
        print("   These likely indicate failed activity API calls")

def generate_audit_report():
    """Generate comprehensive audit report."""
    print("\n" + "=" * 70)
    print("🎯 COMPREHENSIVE METHODOLOGY AUDIT REPORT")
    print("=" * 70)
    
    # Run all audits
    fifty_post_artists = audit_data_patterns()
    subreddit_issues = audit_subreddit_relevance()
    audit_search_methodology()
    audit_scoring_calculation()
    audit_tier_classification()
    audit_api_limitations()
    
    # Summary
    print(f"\n📋 SUMMARY OF ISSUES FOUND:")
    print("=" * 50)
    print(f"1. 🚨 CRITICAL: {len(fifty_post_artists)} artists affected by 50-post truncation")
    print(f"2. 🚨 HIGH: {len([i for i in subreddit_issues if i['priority'] == 'HIGH'])} parody/meme subreddit matches")
    print(f"3. ⚠️ MEDIUM: {len([i for i in subreddit_issues if i['priority'] == 'MEDIUM'])} generic subreddit matches")
    
    print(f"\n💡 RECOMMENDED FIXES:")
    print("=" * 50)
    print("1. Implement enhanced activity collection (remove 50-post limit)")
    print("2. Add parody/meme subreddit filtering")
    print("3. Improve artist-specific subreddit detection")
    print("4. Add manual verification for high-profile artists")
    print("5. Implement better error handling for API failures")
    
    return {
        'truncation_issues': len(fifty_post_artists),
        'relevance_issues': len(subreddit_issues),
        'high_priority_issues': len([i for i in subreddit_issues if i['priority'] == 'HIGH'])
    }

if __name__ == "__main__":
    generate_audit_report() 