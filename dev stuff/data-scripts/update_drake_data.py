#!/usr/bin/env python3
"""
Update Drake Data

Updates the main Reddit analysis JSON with corrected Drake subreddit information.
"""

import json
from pathlib import Path
import datetime

# File paths
project_root = Path(__file__).parent.parent.parent
data_file = project_root / "public" / "data" / "reddit_analysis.json"
backup_file = project_root / "public" / "data" / "reddit_analysis_backup.json"

def update_drake_data():
    """Update Drake with correct subreddit."""
    
    print("🔄 UPDATING DRAKE DATA")
    print("=" * 50)
    
    # Load current data
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create backup
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Backup created: {backup_file}")
    
    # Find Drake
    drake_index = None
    for i, artist in enumerate(data['results']):
        if artist['artist'] == 'Drake':
            drake_index = i
            break
    
    if drake_index is None:
        print("❌ Drake not found!")
        return
    
    old_drake = data['results'][drake_index].copy()
    
    # Update with corrected r/Drizzy data
    corrected_drake = {
        "artist": "Drake",
        "primary_subreddit": "Drizzy", 
        "subreddit_url": "https://reddit.com/r/Drizzy",
        "subscribers": 310109,
        "posts_last_month": 50,
        "comments_last_month": 1336,
        "total_activity": 1386, 
        "popularity_score": 4.47,
        "tier": "⚡ Popular",
        "analysis_notes": "Corrected from r/DrakeTheType (parody) to r/Drizzy (genuine fan community)"
    }
    
    data['results'][drake_index] = corrected_drake
    data['last_updated'] = datetime.datetime.now().isoformat()
    
    # Save
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ Drake updated!")
    print(f"   🔴 OLD: r/{old_drake.get('primary_subreddit')} (parody)")  
    print(f"   🟢 NEW: r/Drizzy (genuine fan community)")
    print(f"   📈 Score: {old_drake.get('popularity_score')} → 4.47")

if __name__ == "__main__":
    update_drake_data() 