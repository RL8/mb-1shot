import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_spotify_api():
    """
    Test Spotify API connectivity and basic functionality
    """
    print("🎵 Testing Spotify API Connectivity")
    print("=" * 50)
    
    # Get credentials from environment
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Spotify credentials not found in environment variables")
        print("   Make sure SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are set in .env")
        return False
    
    print(f"✅ Found Spotify Client ID: {client_id[:8]}...")
    print(f"✅ Found Spotify Client Secret: {client_secret[:8]}...")
    
    try:
        # Set up Spotify client with Client Credentials flow
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        print("\n🔐 Attempting authentication...")
        
        # Test API call - search for a popular artist
        print("🔍 Testing API call: Searching for Taylor Swift...")
        results = sp.search(q='Taylor Swift', type='artist', limit=1)
        
        if results and 'artists' in results and results['artists']['items']:
            artist = results['artists']['items'][0]
            print(f"✅ API Call Successful!")
            print(f"   Artist Found: {artist['name']}")
            print(f"   Followers: {artist['followers']['total']:,}")
            print(f"   Popularity: {artist['popularity']}/100")
            print(f"   Genres: {', '.join(artist['genres'])}")
            
            # Test getting artist's albums
            print(f"\n🎵 Testing album retrieval...")
            albums = sp.artist_albums(artist['id'], album_type='album', limit=5)
            print(f"✅ Found {len(albums['items'])} albums:")
            for album in albums['items']:
                print(f"   - {album['name']} ({album['release_date'][:4]})")
            
            print(f"\n🎯 Spotify API Integration: READY!")
            return True
        else:
            print("❌ No results found in API response")
            return False
            
    except spotipy.exceptions.SpotifyException as e:
        print(f"❌ Spotify API Error: {e}")
        if e.http_status == 401:
            print("   This usually means invalid credentials")
        elif e.http_status == 429:
            print("   Rate limit exceeded - wait a moment and try again")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_integration_potential():
    """
    Test how Spotify data could enhance our music knowledge graph
    """
    print("\n🎯 Testing Integration Potential")
    print("=" * 50)
    
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Get detailed artist info
        results = sp.search(q='Taylor Swift', type='artist', limit=1)
        artist = results['artists']['items'][0]
        artist_id = artist['id']
        
        # Get top tracks
        top_tracks = sp.artist_top_tracks(artist_id)
        print(f"🔥 Top Tracks for {artist['name']}:")
        for i, track in enumerate(top_tracks['tracks'][:3], 1):
            print(f"   {i}. {track['name']} (Popularity: {track['popularity']})")
        
        # Get related artists
        related = sp.artist_related_artists(artist_id)
        print(f"\n👥 Related Artists:")
        for i, related_artist in enumerate(related['artists'][:3], 1):
            print(f"   {i}. {related_artist['name']}")
        
        # Get album details with tracks
        albums = sp.artist_albums(artist_id, album_type='album', limit=2)
        for album in albums['items']:
            album_tracks = sp.album_tracks(album['id'])
            print(f"\n💿 Album: {album['name']} ({len(album_tracks['items'])} tracks)")
            for track in album_tracks['items'][:3]:
                duration_ms = track['duration_ms']
                duration_min = duration_ms // 60000
                duration_sec = (duration_ms % 60000) // 1000
                print(f"   - {track['name']} ({duration_min}:{duration_sec:02d})")
        
        print(f"\n✅ Spotify can provide:")
        print(f"   • Real-time popularity scores")
        print(f"   • Audio features (tempo, energy, etc.)")
        print(f"   • Related artist networks")
        print(f"   • Detailed track information")
        print(f"   • Release dates and album art")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_spotify_api()
    if success:
        test_integration_potential()
        print(f"\n🚀 Spotify API is ready for integration with your music knowledge graph!")
    else:
        print(f"\n❌ Please check your Spotify credentials and try again.") 