#!/usr/bin/env python3
"""
🎵 TOP 100 USA MUSICIANS FETCHER
==================================

This script uses the Spotify API to fetch the current top 100 musicians in the USA
based on their appearance in popular playlists and track popularity.

Results are saved to a JSON file and a human-readable text file.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import json
from collections import defaultdict, Counter
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import time

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class Top100USAMusiciansFetcher:
    def __init__(self):
        """Initialize Spotify API client"""
        print("🎵 Initializing Top 100 USA Musicians Fetcher")
        print("=" * 60)
        
        # Get Spotify credentials
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("❌ Spotify credentials not found. Check SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
        
        # Initialize Spotify client
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        ))
        
        print("✅ Spotify API connection initialized")
        print("=" * 60)
    
    def search_popular_artists_by_genre(self):
        """Search for popular artists in different genres"""
        print("🔍 Searching for popular artists by genre...")
        genres = ['pop', 'hip hop', 'rock', 'country', 'r&b', 'indie', 'electronic', 'jazz', 'rap']
        all_artists = []
        
        for genre in genres:
            try:
                # Search for artists in this genre
                results = self.sp.search(q=f'genre:{genre}', type='artist', market='US', limit=50)
                artists = results['artists']['items']
                
                # Filter for popular artists (popularity > 50)
                popular_artists = [a for a in artists if a['popularity'] > 50]
                all_artists.extend(popular_artists)
                print(f"   ✅ {genre}: {len(popular_artists)} popular artists")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ⚠️  {genre}: {e}")
                continue
        
        print(f"✅ Found {len(all_artists)} artists from genre searches")
        return all_artists
    
    def search_trending_terms(self):
        """Search for artists using trending/popular terms"""
        print("🔥 Searching using trending terms...")
        trending_terms = [
            'top hits', 'viral hits', 'trending now', 'hot 100', 'chart toppers',
            'billboard', 'popular now', 'most played', 'radio hits'
        ]
        
        all_tracks = []
        for term in trending_terms:
            try:
                results = self.sp.search(q=term, type='track', market='US', limit=50)
                tracks = results['tracks']['items']
                # Filter for popular tracks
                popular_tracks = [t for t in tracks if t['popularity'] > 60]
                all_tracks.extend(popular_tracks)
                print(f"   ✅ {term}: {len(popular_tracks)} popular tracks")
                time.sleep(0.1)
            except Exception as e:
                print(f"   ⚠️  {term}: {e}")
                continue
        
        print(f"✅ Found {len(all_tracks)} tracks from trending searches")
        return all_tracks
    
    def find_top_playlists(self):
        """Find 'Top 50' and similar popular playlists"""
        print("📊 Searching for Top 50 and chart playlists...")
        search_terms = [
            'Top 50 USA', 'Top 100 USA', 'Hot Hits USA', 'Trending USA',
            'Billboard Hot 100', 'Top Hits', 'Pop Rising', 'Viral 50'
        ]
        
        found_playlists = []
        for term in search_terms:
            try:
                results = self.sp.search(q=term, type='playlist', market='US', limit=10)
                playlists = results['playlists']['items']
                found_playlists.extend(playlists)
                print(f"   ✅ {term}: {len(playlists)} playlists")
                time.sleep(0.1)
            except Exception as e:
                print(f"   ⚠️  {term}: {e}")
                continue
        
        print(f"✅ Found {len(found_playlists)} chart playlists")
        return found_playlists

    def get_featured_playlists_us(self, limit=50):
        """Get featured playlists in the US market"""
        try:
            print("🎯 Fetching featured playlists in USA...")
            results = self.sp.featured_playlists(country='US', limit=limit)
            playlists = results['playlists']['items']
            print(f"✅ Found {len(playlists)} featured playlists")
            return playlists
        except Exception as e:
            print(f"❌ Error fetching featured playlists: {e}")
            return []

    def get_playlist_tracks(self, playlist_id, playlist_name, max_tracks=100):
        """Get tracks from a playlist"""
        try:
            all_tracks = []
            results = self.sp.playlist_tracks(playlist_id, limit=100, market='US')
            tracks = results['items']
            
            # Get additional pages if needed
            while results['next'] and len(all_tracks) < max_tracks:
                results = self.sp.next(results)
                tracks.extend(results['items'])
            
            # Filter out None values and podcasts
            valid_tracks = []
            for item in tracks[:max_tracks]:
                if item and item['track'] and item['track']['type'] == 'track':
                    valid_tracks.append(item['track'])
            
            print(f"   📀 {playlist_name}: {len(valid_tracks)} tracks")
            return valid_tracks
        except Exception as e:
            print(f"   ❌ Error getting tracks from {playlist_name}: {e}")
            return []
    
    def extract_artists_from_tracks(self, tracks):
        """Extract artist information from tracks"""
        artist_data = defaultdict(lambda: {
            'name': '',
            'spotify_id': '',
            'total_appearances': 0,
            'total_popularity': 0,
            'track_titles': [],
            'max_track_popularity': 0
        })
        
        for track in tracks:
            for artist in track['artists']:
                artist_id = artist['id']
                artist_name = artist['name']
                
                # Update basic info
                artist_data[artist_id]['name'] = artist_name
                artist_data[artist_id]['spotify_id'] = artist_id
                artist_data[artist_id]['total_appearances'] += 1
                artist_data[artist_id]['total_popularity'] += track['popularity']
                artist_data[artist_id]['track_titles'].append(track['name'])
                artist_data[artist_id]['max_track_popularity'] = max(
                    artist_data[artist_id]['max_track_popularity'], track['popularity']
                )
        
        return artist_data
    
    def merge_artist_data(self, search_artists, track_artists):
        """Merge artists from different sources"""
        print("🔗 Merging artist data from multiple sources...")
        
        # Start with track-based artists (they have appearance data)
        merged_data = dict(track_artists)
        
        # Add search-based artists
        for artist in search_artists:
            artist_id = artist['id']
            if artist_id not in merged_data:
                merged_data[artist_id] = {
                    'name': artist['name'],
                    'spotify_id': artist_id,
                    'total_appearances': 1,  # Minimum value for search results
                    'total_popularity': artist['popularity'],
                    'track_titles': [],
                    'max_track_popularity': artist['popularity']
                }
            else:
                # Update existing entry
                merged_data[artist_id]['total_appearances'] += 1
                merged_data[artist_id]['total_popularity'] += artist['popularity']
        
        print(f"✅ Merged data for {len(merged_data)} unique artists")
        return merged_data
    
    def enrich_artist_data(self, artist_data):
        """Get additional artist information from Spotify"""
        print("🔍 Enriching artist data...")
        
        enriched_artists = []
        artist_ids = list(artist_data.keys())
        
        # Process artists in batches of 50 (Spotify API limit)
        for i in range(0, len(artist_ids), 50):
            batch_ids = artist_ids[i:i+50]
            try:
                artists_info = self.sp.artists(batch_ids)
                
                for artist_info in artists_info['artists']:
                    if artist_info:  # Sometimes None if artist not found
                        artist_id = artist_info['id']
                        data = artist_data[artist_id]
                        
                        # Calculate average popularity
                        avg_popularity = data['total_popularity'] / data['total_appearances'] if data['total_appearances'] > 0 else 0
                        
                        enriched_artist = {
                            'rank': 0,  # Will be set later
                            'name': artist_info['name'],
                            'spotify_id': artist_id,
                            'followers': artist_info['followers']['total'],
                            'popularity': artist_info['popularity'],
                            'avg_track_popularity': round(avg_popularity, 1),
                            'max_track_popularity': data['max_track_popularity'],
                            'total_appearances': data['total_appearances'],
                            'genres': artist_info['genres'],
                            'spotify_url': artist_info['external_urls']['spotify'],
                            'image_url': artist_info['images'][0]['url'] if artist_info['images'] else '',
                            'sample_tracks': data['track_titles'][:5]  # First 5 tracks
                        }
                        enriched_artists.append(enriched_artist)
                        
            except Exception as e:
                print(f"   ⚠️  Error enriching batch {i//50 + 1}: {e}")
                continue
        
        print(f"✅ Enriched {len(enriched_artists)} artists")
        return enriched_artists
    
    def calculate_artist_scores(self, artists):
        """Calculate composite scores for ranking artists"""
        print("📊 Calculating artist scores...")
        
        for artist in artists:
            # Composite score based on multiple factors
            # - Spotify popularity (0-100)
            # - Number of playlist appearances
            # - Follower count (normalized)
            # - Average track popularity
            
            follower_score = min(artist['followers'] / 1000000, 100)  # Normalize to 0-100
            appearance_score = min(artist['total_appearances'] * 2, 100)  # Normalize to 0-100
            
            composite_score = (
                artist['popularity'] * 0.4 +  # 40% weight
                artist['avg_track_popularity'] * 0.3 +  # 30% weight
                follower_score * 0.2 +  # 20% weight
                appearance_score * 0.1  # 10% weight
            )
            
            artist['composite_score'] = round(composite_score, 2)
        
        # Sort by composite score
        artists.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Assign ranks
        for i, artist in enumerate(artists, 1):
            artist['rank'] = i
        
        print("✅ Artist scores calculated and ranked")
        return artists
    
    def fetch_top_100_musicians(self):
        """Main method to fetch top 100 USA musicians"""
        print("🚀 Starting Top 100 USA Musicians fetch...")
        
        # Get artists from multiple sources
        search_artists = self.search_popular_artists_by_genre()
        trending_tracks = self.search_trending_terms()
        chart_playlists = self.find_top_playlists()
        featured_playlists = self.get_featured_playlists_us(limit=20)
        
        # Combine playlists and filter out None values
        all_playlists = [p for p in chart_playlists + featured_playlists if p is not None]
        
        # Remove duplicates based on playlist ID
        unique_playlists = {p['id']: p for p in all_playlists if p is not None}.values()
        print(f"📋 Processing {len(unique_playlists)} unique playlists")
        
        # Collect all tracks
        all_tracks = trending_tracks.copy()
        for playlist in list(unique_playlists)[:20]:  # Limit to prevent rate limiting
            tracks = self.get_playlist_tracks(playlist['id'], playlist['name'])
            all_tracks.extend(tracks)
        
        print(f"🎵 Collected {len(all_tracks)} total tracks")
        
        # Extract and merge artist data
        track_artists = self.extract_artists_from_tracks(all_tracks)
        merged_artists = self.merge_artist_data(search_artists, track_artists)
        print(f"🎤 Found {len(merged_artists)} unique artists")
        
        # Filter artists with minimum appearances
        filtered_artists = {k: v for k, v in merged_artists.items() if v['total_appearances'] >= 1}
        print(f"🎯 Filtered to {len(filtered_artists)} artists")
        
        # Enrich with detailed artist information
        enriched_artists = self.enrich_artist_data(filtered_artists)
        
        # Calculate scores and rank
        ranked_artists = self.calculate_artist_scores(enriched_artists)
        
        # Return top 100
        top_100 = ranked_artists[:100]
        print(f"🏆 Top 100 USA musicians identified!")
        
        return top_100
    
    def save_results(self, artists):
        """Save results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_filename = f"top_100_usa_musicians_{timestamp}.json"
        json_data = {
            'generated_at': datetime.now().isoformat(),
            'total_artists': len(artists),
            'data_source': 'Spotify API - USA Market',
            'methodology': 'Based on genre searches, trending tracks, playlist appearances, popularity, and follower count',
            'artists': artists
        }
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # Save as human-readable text
        txt_filename = f"top_100_usa_musicians_{timestamp}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("🎵 TOP 100 CURRENT USA MUSICIANS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Source: Spotify API (USA Market)\n")
            f.write(f"Total Artists: {len(artists)}\n\n")
            
            f.write("Ranking Methodology:\n")
            f.write("- Spotify Popularity Score (40%)\n")
            f.write("- Average Track Popularity (30%)\n")
            f.write("- Follower Count (20%)\n")
            f.write("- Playlist Appearances (10%)\n\n")
            f.write("=" * 50 + "\n\n")
            
            for artist in artists:
                f.write(f"#{artist['rank']:2d}. {artist['name']}\n")
                f.write(f"     Score: {artist['composite_score']}/100\n")
                f.write(f"     Popularity: {artist['popularity']}/100\n")
                f.write(f"     Followers: {artist['followers']:,}\n")
                f.write(f"     Playlist Appearances: {artist['total_appearances']}\n")
                f.write(f"     Genres: {', '.join(artist['genres'][:3])}\n")  # Top 3 genres
                f.write(f"     Sample Tracks: {', '.join(artist['sample_tracks'][:3])}\n")
                f.write(f"     Spotify: {artist['spotify_url']}\n")
                f.write("-" * 50 + "\n")
        
        print(f"💾 Results saved:")
        print(f"   📄 {json_filename} (JSON format)")
        print(f"   📄 {txt_filename} (Human-readable)")
        
        return json_filename, txt_filename

def main():
    """Main execution function"""
    try:
        fetcher = Top100USAMusiciansFetcher()
        top_100_artists = fetcher.fetch_top_100_musicians()
        json_file, txt_file = fetcher.save_results(top_100_artists)
        
        print("\n🎉 SUCCESS!")
        print("=" * 60)
        print(f"✅ Fetched top 100 USA musicians")
        print(f"📊 Top 3 artists:")
        for i, artist in enumerate(top_100_artists[:3], 1):
            print(f"   {i}. {artist['name']} (Score: {artist['composite_score']}, Followers: {artist['followers']:,})")
        print(f"\n📁 Results saved to:")
        print(f"   • {json_file}")
        print(f"   • {txt_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

if __name__ == "__main__":
    main() 