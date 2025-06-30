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
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials not found")
        
        self.neo4j_uri = os.getenv("AURA_DB_URI")
        self.neo4j_user = os.getenv("AURA_DB_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("AURA_DB_PASSWORD")
        
        if not self.neo4j_uri or not self.neo4j_password:
            raise ValueError("Neo4j credentials not found")
        
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        ))
        
        self.driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
        print(" Spotify API and Neo4j connections initialized")

    def build_knowledge_graph(self, artist_names):
        print(" Starting Spotify Knowledge Graph Builder (Fixed Version)")
        print(" Note: Audio features disabled due to API permissions")
        print("=" * 60)
        
        for artist_name in artist_names:
            print(f" Processing: {artist_name}")
            artist = self.sp.search(q=artist_name, type='artist', limit=1)['artists']['items'][0]
            
            # Create artist node
            with self.driver.session() as session:
                session.run("""
                    MERGE (a:Artist {spotify_id: })
                    SET a.name = , a.popularity = 
                """, id=artist['id'], name=artist['name'], popularity=artist['popularity'])
            
            print(f" Created artist: {artist['name']}")
        
        print(" Knowledge Graph Build Complete!")

if __name__ == "__main__":
    builder = SpotifyKnowledgeGraphBuilder()
    builder.build_knowledge_graph(["Taylor Swift", "Ed Sheeran", "Billie Eilish"])
    builder.driver.close()
