# Reddit Artist Popularity Scoring - Single Primary Subreddit Methodology

## 🎯 **Objective**
Assess artist popularity on Reddit by measuring engagement density in their primary dedicated subreddit community.

## 📊 **Chosen Methodology: Single Primary Subreddit Approach**

### **Core Algorithm:**
```
Artist Popularity Score = (Monthly Activity ÷ Total Subscribers) × 1000
```

**Where:**
- **Monthly Activity** = Posts + Comments in last 30 days
- **Total Subscribers** = Current subreddit subscriber count
- **×1000** = Normalization factor for readability

### **Primary Subreddit Selection:**
1. Search for exact artist name (spaces removed): `taylorswift`, `billieeilish`
2. Search for artist name + common suffixes: `artistnamefans`, `artistnamemusic`
3. Select **largest dedicated subreddit** with relevance score 8+ (exact/close name match)
4. Must have minimum 50K subscribers to qualify

## 🧪 **Validation Results (5 Test Artists)**

| Artist | Primary Subreddit | Subscribers | Activity | Score | Tier |
|--------|------------------|-------------|----------|-------|------|
| Drake | r/DrakeTheType | 103K | 626 | **6.07** | ⚡ Popular |
| Dua Lipa | r/dualipa | 653K | 627 | **0.96** | 📊 Present |
| Kendrick Lamar | r/KendrickLamar | 1.4M | 1,324 | **0.92** | 📊 Present |
| Taylor Swift | r/TaylorSwift | 3.7M | 2,795 | **0.75** | 📊 Present |
| Billie Eilish | r/billieeilish | 1.2M | 678 | **0.56** | 💤 Minimal |

## 🎯 **Scoring Tiers**

- **🔥 Viral**: Score > 5.0 (Super engaged fanbase)
- **⚡ Popular**: Score 2.0-5.0 (Active dedicated community)  
- **📊 Present**: Score 0.5-2.0 (Moderate engagement)
- **💤 Minimal**: Score < 0.5 (Low engagement density)
- **❌ No Presence**: No qualifying subreddit found

## ✅ **Why This Approach Won**

### **Tested Alternatives:**
1. **❌ Multiple Subreddit Average**: Generic communities (r/popheads, r/Music) added noise
2. **❌ Hybrid Weighted Scoring**: Complexity without meaningful signal improvement
3. **❌ Activity Count Only**: Didn't account for fanbase size differences
4. **✅ Single Primary Focus**: Clean, scalable, meaningful comparisons

### **Key Advantages:**
- **🚀 Scalable**: One API call per artist (vs 5+ for alternatives)
- **🎯 Focused**: Measures dedicated fan engagement, not casual mentions
- **📊 Comparable**: Engagement density allows fair comparison across artist scales
- **⚡ Fast**: Minimal rate limiting for hundreds of artists
- **🔍 Clear**: Single score per artist for easy ranking

### **What It Measures:**
- **Fan Intensity**: How actively engaged are dedicated fans?
- **Community Vitality**: Is the fanbase growing/participating?
- **Reddit Presence**: Meaningful platform engagement vs just existence

### **What It Doesn't Measure:**
- Total mentions across all Reddit (breadth)
- Casual fan awareness in general communities
- Cross-genre influence or collaborations

## 🛠 **Implementation Requirements**

### **API Calls Needed:**
1. **Subreddit Search**: `GET /subreddits/search.json?q={artist_name}`
2. **Activity Analysis**: `GET /r/{subreddit}/new.json?limit=50`
3. **Subreddit Info**: Included in search results (subscriber count)

### **Rate Limiting:**
- 1.5 second delay between requests
- Max 100 requests per batch to avoid 429 errors
- Retry logic for temporary failures

### **Data Processing:**
```python
# Core scoring function
def calculate_artist_score(posts_last_month, comments_last_month, total_subscribers):
    activity_score = posts_last_month + comments_last_month
    engagement_density = (activity_score / total_subscribers) * 1000
    return engagement_density

# Time filtering (30 days)
month_ago = current_time - (30 * 24 * 60 * 60)
qualifying_posts = [post for post in posts if post['created_utc'] >= month_ago]
```

## 📈 **Expected Output Format**

### **Per Artist:**
```json
{
  "artist": "Taylor Swift",
  "primary_subreddit": "TaylorSwift",
  "subreddit_url": "https://reddit.com/r/TaylorSwift",
  "subscribers": 3724529,
  "posts_last_month": 50,
  "comments_last_month": 2745,
  "total_activity": 2795,
  "popularity_score": 0.75,
  "tier": "Present",
  "relevance_score": 12
}
```

### **Aggregated Results:**
```json
{
  "analysis_date": "2025-01-07",
  "total_artists_analyzed": 100,
  "scoring_criteria": "Single Primary Subreddit - Engagement Density",
  "tier_distribution": {
    "viral": 5,
    "popular": 15, 
    "present": 45,
    "minimal": 30,
    "no_presence": 5
  },
  "top_10_by_score": [...]
}
```

## 🎵 **Music Besties Integration**

### **User Onboarding:**
- **High Score Artists**: Suggest joining dedicated communities
- **Medium Score Artists**: Good for balanced engagement
- **Low Score Artists**: Focus on broader music communities

### **Matching Algorithm:**
- Users who like high-engagement artists likely prefer active communities
- Match engagement preference levels between users
- Use scores to predict community participation likelihood

### **Community Recommendations:**
- Direct users to most active subreddits for their favorite artists
- Avoid suggesting low-engagement communities
- Prioritize quality over quantity

---

## 📝 **Implementation Notes**

**Created:** January 7, 2025  
**Last Updated:** January 7, 2025  
**Status:** Validated with 5 test artists  
**Next Steps:** Scale to full artist database  
**Estimated Runtime:** ~2-3 seconds per artist with rate limiting 