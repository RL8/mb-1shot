#!/usr/bin/env python3
"""
Focused Reddit Search - Test specific artists likely to have communities
"""

import requests
import time
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'script:mb-script:v1.0')

def search_artist(artist_name):
    """Test search for a specific artist."""
    print(f"\n🎵 TESTING: {artist_name}")
    print("-" * 40)
    
    artist_clean = artist_name.replace(' ', '').lower()
    queries = [artist_name, artist_clean, f"{artist_name} fans"]
    
    for query in queries:
        print(f"  🔍 '{query}'", end="")
        
        url = "https://www.reddit.com/subreddits/search.json"
        headers = {'User-Agent': USER_AGENT}
        params = {'q': query, 'limit': 10}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            found = 0
            if data and 'data' in data:
                for item in data['data'].get('children', []):
                    sub_data = item.get('data', {})
                    subs = sub_data.get('subscribers', 0) or 0
                    name = sub_data.get('display_name', '')
                    
                    if subs >= 10000:  # 10K+ threshold
                        print(f"\n    ✅ r/{name}: {subs:,} subscribers")
                        found += 1
            
            if found == 0:
                print(" ❌")
                
        except Exception as e:
            print(f" Error: {e}")
        
        time.sleep(1.5)

def main():
    """Test search on likely candidates."""
    print("🎯 FOCUSED REDDIT SEARCH TEST")
    print("=" * 40)
    
    # Test artists likely to have communities
    test_artists = [
        "Bad Bunny",      # Huge global artist
        "Bruno Mars",     # Major pop artist  
        "Adele",          # Mega-popular
        "Beyoncé",        # Iconic
        "Justin Bieber",  # Pop star
        "Rihanna",        # Huge fanbase
        "Kanye West",     # Controversial/popular
        "Jay-Z"           # Hip-hop legend
    ]
    
    for artist in test_artists:
        search_artist(artist)

if __name__ == "__main__":
    main() 