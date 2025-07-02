# Reddit Artist Subreddit Discovery

This directory contains improved scripts for discovering and analyzing artist fan subreddits using the Reddit API.

## 🎯 Overview

The `reddit_artist_subreddit_finder.py` script is an enhanced version of the original subreddit discovery tool, specifically optimized for the Music Besties project.

## ✨ Key Improvements

- ✅ **Environment Integration**: Uses credentials from project `.env` file
- ✅ **Enhanced Scoring**: Better relevance and activity algorithms  
- ✅ **Modern Artist List**: Updated with current popular artists across genres
- ✅ **Better Error Handling**: Robust API error management
- ✅ **Structured Output**: Saves results in both JSON and CSV formats
- ✅ **Project Integration**: Proper file paths and directory structure

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd "dev stuff/data-scripts"
pip install -r requirements.txt
```

### 2. Verify Reddit API Credentials
Ensure your `.env` file contains:
```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here  
REDDIT_USER_AGENT=web:music-besties:v1.0 (by /u/your_username)
```

### 3. Run the Discovery Script
```bash
python reddit_artist_subreddit_finder.py
```

## 📊 Output

The script creates a `reddit_results` directory with:
- **JSON files**: Complete data with metadata
- **CSV files**: Spreadsheet-friendly summaries
- **Timestamped files**: Each run creates unique files

### Example Output Structure:
```
reddit_results/
├── reddit_subreddits_discovery_20240101_120000.json
├── reddit_subreddits_discovery_20240101_120000.csv
└── ...
```

## 🎵 Default Artist List

The script searches for subreddits for these artists:

**Pop/Mainstream**: Taylor Swift, Billie Eilish, Dua Lipa, Olivia Rodrigo, Harry Styles

**Hip-Hop/Rap**: Kendrick Lamar, Drake, Tyler The Creator, J. Cole, Childish Gambino

**Rock/Alternative**: Arctic Monkeys, Tame Impala, The 1975, Radiohead

**Electronic/Dance**: Daft Punk, Flume, ODESZA, Disclosure

**Indie/Alternative**: Phoebe Bridgers, Mac Miller, Frank Ocean, Bon Iver

**R&B/Soul**: The Weeknd, SZA, Anderson .Paak, H.E.R.

## ⚙️ Configuration

You can modify the `CONFIG` dictionary in the script to adjust:
- Search limits
- Scoring thresholds  
- Rate limiting delays
- Activity requirements

## 🔧 Troubleshooting

### Common Issues:

1. **"Reddit API credentials not found"**
   - Check your `.env` file exists in project root
   - Verify all three Reddit variables are set

2. **"Failed to connect to Reddit API"**
   - Check your internet connection
   - Verify Reddit credentials are correct
   - Check if Reddit API is down

3. **Rate limiting errors**
   - The script includes built-in delays
   - Reddit allows ~60 requests per minute for web apps

## 🔗 Integration with Music Besties

This script generates data that can be used for:
- Music community discovery
- User preference analysis  
- Genre-based recommendations
- Social music features

## 📝 Next Steps

After running the script, you can:
1. Analyze the CSV results in Excel/Google Sheets
2. Import JSON data into your music knowledge graph
3. Use subreddit data for user onboarding
4. Build music community features

## 🆚 Comparison with Original

| Feature | Original Script | Improved Script |
|---------|----------------|-----------------|
| Credentials | Hardcoded | Environment variables |
| Artist List | 10 mixed artists | 23 current diverse artists |
| Output | Basic audit files | JSON + CSV with timestamps |
| Error Handling | Basic | Enhanced with retry logic |
| Project Integration | None | Full path integration |
| Configuration | Scattered constants | Centralized CONFIG dict |

## 🛠️ Advanced Usage

To customize the artist list, edit the `artists` array in the main script or create a separate configuration file.

For production use, consider:
- Adding database integration
- Implementing caching
- Setting up scheduled runs
- Adding email notifications

---

**Note**: This script respects Reddit's API rate limits and terms of service. Always use responsibly and follow Reddit's guidelines. 