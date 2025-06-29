import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from neo4j import GraphDatabase
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpotifyKnowledgeGraphBuilder:
    def __init__(self):
        """Initialize Spotify API client and Neo4j connection"""
        
        # Spotify API setup
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials not found. Check SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        
        # Neo4j setup
        self.neo4j_uri = os.getenv("AURA_DB_URI")
        self.neo4j_user = os.getenv("AURA_DB_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("AURA_DB_PASSWORD")
        
        if not self.neo4j_uri or not self.neo4j_password:
            raise ValueError("Neo4j credentials not found. Check AURA_DB_URI and AURA_DB_PASSWORD")
        
        # Initialize clients
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        ))
        
        self.driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
        
        print("✅ Spotify API and Neo4j connections initialized")
    
    def get_artist_by_name(self, artist_name):
        """Get artist information from Spotify by name"""
        try:
            results = self.sp.search(q=artist_name, type='artist', limit=1)
            if results['artists']['items']:
                artist = results['artists']['items'][0]
                print(f"✅ Found artist: {artist['name']} (ID: {artist['id']})")
                return artist
            else:
                print(f"❌ Artist not found: {artist_name}")
                return None
        except Exception as e:
            print(f"❌ Error searching for artist {artist_name}: {e}")
            return None
    
    def get_artist_albums(self, artist_id, limit=20):
        """Get albums for an artist (limited to prevent too many API calls)"""
        try:
            albums = []
            results = self.sp.artist_albums(artist_id, album_type='album', limit=limit)
            
            for album in results['items']:
                # Get full album details
                album_details = self.sp.album(album['id'])
                albums.append(album_details)
                
            print(f"✅ Found {len(albums)} albums for artist {artist_id}")
            return albums
        except Exception as e:
            print(f"❌ Error getting albums for artist {artist_id}: {e}")
            return []
    
    def get_album_tracks(self, album_id):
        """Get all tracks for an album with audio features"""
        try:
            results = self.sp.album_tracks(album_id)
            tracks = results['items']
            
            # Get audio features for all tracks
            track_ids = [track['id'] for track in tracks if track['id']]
            if track_ids:
                audio_features = self.sp.audio_features(track_ids)
                
                # Merge track info with audio features
                for i, track in enumerate(tracks):
                    if i < len(audio_features) and audio_features[i]:
                        track['audio_features'] = audio_features[i]
            
            print(f"✅ Found {len(tracks)} tracks for album {album_id}")
            return tracks
        except Exception as e:
            print(f"❌ Error getting tracks for album {album_id}: {e}")
            return []
    
    def create_artist_node(self, artist_data):
        """Create artist node in Neo4j"""
        with self.driver.session() as session:
            try:
                cypher = """
                MERGE (a:Artist {spotify_id: $spotify_id})
                SET a.name = $name,
                    a.followers = $followers,
                    a.popularity = $popularity,
                    a.genres = $genres,
                    a.image_url = $image_url,
                    a.spotify_url = $spotify_url,
                    a.updated_at = datetime()
                RETURN a
                """
                
                session.run(cypher, 
                    spotify_id=artist_data['id'],
                    name=artist_data['name'],
                    followers=artist_data['followers']['total'],
                    popularity=artist_data['popularity'],
                    genres=artist_data['genres'],
                    image_url=artist_data['images'][0]['url'] if artist_data['images'] else None,
                    spotify_url=artist_data['external_urls']['spotify']
                )
                print(f"✅ Created/updated artist node: {artist_data['name']}")
                
            except Exception as e:
                print(f"❌ Error creating artist node: {e}")
    
    def create_album_node(self, album_data, artist_id):
        """Create album node and link to artist"""
        with self.driver.session() as session:
            try:
                cypher = """
                MATCH (a:Artist {spotify_id: $artist_id})
                MERGE (al:Album {spotify_id: $album_id})
                SET al.name = $name,
                    al.release_date = $release_date,
                    al.total_tracks = $total_tracks,
                    al.album_type = $album_type,
                    al.image_url = $image_url,
                    al.spotify_url = $spotify_url,
                    al.updated_at = datetime()
                MERGE (a)-[:RELEASED]->(al)
                RETURN al
                """
                
                session.run(cypher,
                    artist_id=artist_id,
                    album_id=album_data['id'],
                    name=album_data['name'],
                    release_date=album_data['release_date'],
                    total_tracks=album_data['total_tracks'],
                    album_type=album_data['album_type'],
                    image_url=album_data['images'][0]['url'] if album_data['images'] else None,
                    spotify_url=album_data['external_urls']['spotify']
                )
                print(f"✅ Created/updated album node: {album_data['name']}")
                
            except Exception as e:
                print(f"❌ Error creating album node: {e}")
    
    def create_track_node(self, track_data, album_id):
        """Create track node with audio features and link to album"""
        with self.driver.session() as session:
            try:
                cypher = """
                MATCH (al:Album {spotify_id: $album_id})
                MERGE (t:Track {spotify_id: $track_id})
                SET t.name = $name,
                    t.duration_ms = $duration_ms,
                    t.explicit = $explicit,
                    t.track_number = $track_number,
                    t.preview_url = $preview_url,
                    t.spotify_url = $spotify_url,
                    t.updated_at = datetime()
                """
                
                # Add audio features if available
                if 'audio_features' in track_data and track_data['audio_features']:
                    af = track_data['audio_features']
                    cypher += """
                    SET t.danceability = $danceability,
                        t.energy = $energy,
                        t.valence = $valence,
                        t.tempo = $tempo,
                        t.acousticness = $acousticness,
                        t.instrumentalness = $instrumentalness,
                        t.speechiness = $speechiness,
                        t.liveness = $liveness,
                        t.loudness = $loudness
                    """
                
                cypher += """
                MERGE (al)-[:CONTAINS {track_number: $track_number}]->(t)
                RETURN t
                """
                
                params = {
                    'album_id': album_id,
                    'track_id': track_data['id'],
                    'name': track_data['name'],
                    'duration_ms': track_data['duration_ms'],
                    'explicit': track_data['explicit'],
                    'track_number': track_data['track_number'],
                    'preview_url': track_data.get('preview_url'),
                    'spotify_url': track_data['external_urls']['spotify']
                }
                
                # Add audio features to params if available
                if 'audio_features' in track_data and track_data['audio_features']:
                    af = track_data['audio_features']
                    params.update({
                        'danceability': af.get('danceability'),
                        'energy': af.get('energy'),
                        'valence': af.get('valence'),
                        'tempo': af.get('tempo'),
                        'acousticness': af.get('acousticness'),
                        'instrumentalness': af.get('instrumentalness'),
                        'speechiness': af.get('speechiness'),
                        'liveness': af.get('liveness'),
                        'loudness': af.get('loudness')
                    })
                
                session.run(cypher, **params)
                print(f"✅ Created/updated track: {track_data['name']}")
                
            except Exception as e:
                print(f"❌ Error creating track node: {e}")
    
    def process_artist(self, artist_name):
        """Process a single artist completely"""
        print(f"\n🎤 Processing artist: {artist_name}")
        print("=" * 60)
        
        # Get artist info
        artist = self.get_artist_by_name(artist_name)
        if not artist:
            return False
        
        # Create artist node
        self.create_artist_node(artist)
        
        # Get and process albums (limited to prevent too many API calls)
        albums = self.get_artist_albums(artist['id'], limit=10)
        
        for album in albums:
            print(f"\n💿 Processing album: {album['name']}")
            
            # Create album node
            self.create_album_node(album, artist['id'])
            
            # Get and process tracks
            tracks = self.get_album_tracks(album['id'])
            for track in tracks:
                self.create_track_node(track, album['id'])
            
            # Rate limiting between albums
            time.sleep(0.5)
        
        print(f"✅ Completed processing: {artist_name}")
        return True
    
    def build_knowledge_graph(self, artist_names):
        """Build complete knowledge graph for list of artists"""
        print("🎵 Starting Spotify Knowledge Graph Builder")
        print("=" * 60)
        
        successful = 0
        failed = 0
        
        for i, artist_name in enumerate(artist_names, 1):
            print(f"\n📊 Progress: {i}/{len(artist_names)} artists")
            
            if self.process_artist(artist_name):
                successful += 1
            else:
                failed += 1
            
            # Rate limiting between artists
            if i < len(artist_names):
                print("⏱️  Waiting 3 seconds before next artist...")
                time.sleep(3)
        
        print(f"\n🎯 Knowledge Graph Build Complete!")
        print(f"✅ Successful: {successful} artists")
        print(f"❌ Failed: {failed} artists")
        
        return successful, failed
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("✅ Neo4j connection closed")

# Test function
def test_spotify_builder():
    """Test the builder with a few artists"""
    test_artists = [
        "Taylor Swift",
        "Ed Sheeran", 
        "Billie Eilish"
    ]
    
    try:
        builder = SpotifyKnowledgeGraphBuilder()
        builder.build_knowledge_graph(test_artists)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        if 'builder' in locals():
            builder.close()

if __name__ == "__main__":
    test_spotify_builder()
