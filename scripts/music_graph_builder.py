import requests
import json
import time
import os
from bs4 import BeautifulSoup
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
# Wikipedia API
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "MusicBestiesKnowledgeGraph/1.0 (musicbesties@example.com)"

# AuraDB (Neo4j) Connection - using existing env vars
NEO4J_URI = os.getenv("AURA_DB_URI")
NEO4J_USERNAME = os.getenv("AURA_DB_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("AURA_DB_PASSWORD")

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validation
if not all([NEO4J_URI, NEO4J_PASSWORD, OPENAI_API_KEY]):
    raise ValueError("Missing required environment variables. Check AURA_DB_URI, AURA_DB_PASSWORD, and OPENAI_API_KEY")

print("✅ Configuration loaded successfully")
print(f"Neo4j URI: {NEO4J_URI}")
print(f"OpenAI API Key: {'Set' if OPENAI_API_KEY else 'Missing'}")

# --- Step 1: Wikipedia Data Fetching ---

def fetch_artist_discography_url(artist_name: str) -> str | None:
    """
    Searches Wikipedia for an artist's discography page and returns its full URL.
    """
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{artist_name} discography",
        "format": "json",
        "redirects": 1,
        "srlimit": 1
    }
    try:
        response = requests.get(WIKIPEDIA_API_URL, params=params, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        data = response.json()

        if data and 'query' in data and 'search' in data['query'] and data['query']['search']:
            discography_title = data['query']['search'][0]['title']
            return f"https://en.wikipedia.org/wiki/{discography_title.replace(' ', '_')}"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching discography URL for {artist_name}: {e}")
    return None

def get_wikipedia_page_html(page_title: str) -> str | None:
    """
    Fetches the parsed HTML content of a Wikipedia page.
    """
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "text",
        "format": "json",
        "redirects": 1
    }
    try:
        response = requests.get(WIKIPEDIA_API_URL, params=params, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        data = response.json()
        if data and 'parse' in data and 'text' in data['parse']:
            return data['parse']['text']['*']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML for '{page_title}': {e}")
    return None

# --- Step 2: Database Loading ---

def load_artist_to_auradb(driver, artist_name: str):
    """
    Creates an artist node in AuraDB.
    """
    with driver.session() as session:
        try:
            session.run("MERGE (a:Artist {name: $artistName})", artistName=artist_name)
            print(f"✅ Created/updated artist: {artist_name}")
        except Exception as e:
            print(f"❌ Error loading artist {artist_name}: {e}")

# --- Main Test Function ---

def test_connection():
    """
    Test database connection and basic functionality.
    """
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("✅ Successfully connected to AuraDB")
        
        # Test with one artist
        test_artist = "Taylor Swift"
        load_artist_to_auradb(driver, test_artist)
        
        # Test Wikipedia API
        discography_url = fetch_artist_discography_url(test_artist)
        if discography_url:
            print(f"✅ Found discography URL: {discography_url}")
        else:
            print("❌ Could not fetch discography URL")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

# --- Run Test ---
if __name__ == "__main__":
    print("🎵 Music Besties - Knowledge Graph Builder")
    print("=" * 50)
    success = test_connection()
    if success:
        print("\n✅ System is ready for full implementation!")
    else:
        print("\n❌ Please check your configuration and try again.") 