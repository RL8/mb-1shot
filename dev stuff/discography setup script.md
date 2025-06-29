You're looking for a comprehensive Python script that orchestrates the entire process, from a list of artist names to a knowledge graph in AuraDB. This is an advanced script as it combines web scraping, LLM interaction, and database loading.

Here's the conceptual structure of the script, with explanations for each section. **Please note:** A complete, production-ready script would require significant development, error handling, and potential fine-tuning of LLM prompts and parsing logic. This provides the blueprint.

-----

## **Full Python Script: Wikipedia to AuraDB Knowledge Graph**

**Pre-requisites:**

1.  **Python 3.x** installed.
2.  **Installed Libraries:**
    ```bash
    pip install requests beautifulsoup4 neo4j langchain openai # or other LLM provider library
    ```
3.  **AuraDB Instance:**
      * You need an AuraDB (Neo4j) instance.
      * Get your **AuraDB URI**, **username** (usually `neo4j`), and **password** from your AuraDB console.
4.  **LLM API Key:**
      * You'll need an API key for the Large Language Model you choose (e.g., OpenAI API Key, Google Gemini API Key). This should be stored securely, ideally not directly in the script.

-----

```python
import requests
import json
import time
from bs4 import BeautifulSoup
from neo4j import GraphDatabase
import os
# from langchain_openai import ChatOpenAI # Uncomment if using OpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import JsonOutputParser # For structured JSON output from LLM
# from langchain.schema import SystemMessage, HumanMessage # For basic LLM interaction

# --- Configuration ---
# Wikipedia API
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "MyMusicKnowledgeGraphBuilder/1.0 (your_email@example.com)" # IMPORTANT: Replace with your email/app name

# AuraDB (Neo4j) Connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687") # Replace with your AuraDB URI or use environment variable
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# LLM Configuration (Example using OpenAI - adjust for other LLMs like Google Gemini)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Store securely
# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY environment variable not set.")
# llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0) # Choose your LLM model

# --- Data Model Definition ---
# This is a conceptual representation for what we expect the LLM to output
# and what we will map to our graph.
# Nodes: Artist, Album, Song, (Optional: Person, Genre)
# Relationships: RELEASED, CONTAINS (with trackNumber), (Optional: WRITTEN_BY, PRODUCED_BY, HAS_GENRE)

# --- Step 1: Fetch Album List for Each Artist ---

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
        "srlimit": 1 # We usually only want the top result for discography
    }
    try:
        response = requests.get(WIKIPEDIA_API_URL, params=params, headers={"User-Agent": USER_AGENT})
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()

        if data and 'query' in data and 'search' in data['query'] and data['query']['search']:
            # Take the first search result
            discography_title = data['query']['search'][0]['title']
            # Construct the full Wikipedia URL
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

def extract_album_titles_from_discography(html_content: str) -> list[dict]:
    """
    Parses the discography page HTML to extract album titles and their potential Wikipedia URLs.
    This requires specific knowledge of Wikipedia's HTML structure, which can vary.
    This is a simplified example and might need significant refinement.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    albums = []

    # Look for common patterns for discography tables
    # This is a very simplified example. Real parsing needs more robust selectors.
    # Often, studio albums are in tables with class 'wikitable'
    for table in soup.find_all('table', class_='wikitable'):
        # Heuristic: Check if the table seems to contain album info by looking at headers
        headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
        if any(h in headers for h in ['title', 'album details', 'year', 'peak chart positions']):
            for row in table.find_all('tr')[1:]: # Skip header row
                cols = row.find_all(['td', 'th']) # Use both for robustness
                if len(cols) > 0:
                    album_link_tag = cols[0].find('a', title=True) # Assuming title is in the first column
                    if album_link_tag and album_link_tag.get('href') and album_link_tag.get('title'):
                        album_title = album_link_tag['title']
                        # Filter out non-album pages (e.g., songs, singles, EPs if they appear)
                        # A common pattern for album pages is "Album Title (Artist album)"
                        if "(album)" in album_title.lower() or "(taylor swift album)" in album_title.lower():
                             albums.append({
                                'title': album_title,
                                'url': f"https://en.wikipedia.org{album_link_tag['href']}"
                            })
    return albums

# --- Step 2: Use LLM to Process Page Text and Extract Structured Data ---

# Define the expected JSON schema for the LLM output
ALBUM_SCHEMA = {
    "type": "object",
    "properties": {
        "album_title": {"type": "string"},
        "artist_name": {"type": "string"},
        "release_date": {"type": "string", "format": "date"},
        "genres": {"type": "array", "items": {"type": "string"}},
        "tracks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "track_number": {"type": "integer"},
                    "song_title": {"type": "string"},
                    "duration": {"type": "string", "description": "e.g., 3:45"},
                    "featured_artists": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["track_number", "song_title"]
            }
        }
    },
    "required": ["album_title", "artist_name", "release_date", "tracks"]
}

# Example of an LLM extraction function using LangChain
# This part requires an LLM provider set up (e.g., OpenAI API Key)
# def extract_album_data_with_llm(album_page_text: str, artist_name: str) -> dict | None:
#     """
#     Uses an LLM to extract structured album and tracklist data from raw Wikipedia page text.
#     """
#     parser = JsonOutputParser(pydantic_object=ALBUM_SCHEMA) # For schema enforcement
#     prompt = ChatPromptTemplate.from_messages([
#         SystemMessage(content=f"You are an expert at extracting structured music album information from text. "
#                               "Extract album title, artist name, release date (YYYY-MM-DD), genres, "
#                               "and a list of tracks including track number, song title, and optional duration "
#                               "and featured artists. The artist is {artist_name}. "
#                               "Ensure the output strictly follows this JSON schema:\n"
#                               f"{json.dumps(ALBUM_SCHEMA, indent=2)}"),
#         HumanMessage(content=f"Extract data from the following Wikipedia page content:\n\n{album_page_text[:10000]}") # Limit text size for LLM context
#     ])

#     try:
#         chain = prompt | llm | parser
#         response = chain.invoke({"artist_name": artist_name, "album_page_text": album_page_text})
#         return response
#     except Exception as e:
#         print(f"Error during LLM extraction: {e}")
#         return None

# --- Step 3: Load Structured Data into AuraDB ---

def load_data_to_auradb(driver, parsed_data: dict):
    """
    Loads parsed album and song data into AuraDB using Cypher MERGE statements.
    """
    with driver.session() as session:
        try:
            # Create/Merge Artist Node
            session.run("MERGE (a:Artist {name: $artistName})",
                        artistName=parsed_data['artist_name'])

            # Create/Merge Album Node and link to Artist
            session.run("""
                MATCH (a:Artist {name: $artistName})
                MERGE (al:Album {title: $albumTitle})
                SET al.releaseDate = $releaseDate, al.wikipediaUrl = $wikipediaUrl
                MERGE (a)-[:RELEASED]->(al)
                """,
                artistName=parsed_data['artist_name'],
                albumTitle=parsed_data['album_title'],
                releaseDate=parsed_data['release_date'],
                wikipediaUrl=parsed_data.get('wikipedia_url') # LLM might not directly provide this
            )

            # Create/Merge Genre Nodes and link to Album
            for genre_name in parsed_data.get('genres', []):
                session.run("MERGE (g:Genre {name: $genreName})", genreName=genre_name)
                session.run("""
                    MATCH (al:Album {title: $albumTitle})
                    MATCH (g:Genre {name: $genreName})
                    MERGE (al)-[:HAS_GENRE]->(g)
                    """,
                    albumTitle=parsed_data['album_title'],
                    genreName=genre_name
                )

            # Create/Merge Song Nodes and link to Album
            for track in parsed_data['tracks']:
                # Ensure track number is an integer
                try:
                    track_number = int(track['track_number'])
                except (ValueError, TypeError):
                    print(f"Skipping song '{track.get('song_title')}' due to invalid track number: {track.get('track_number')}")
                    continue

                session.run("""
                    MATCH (al:Album {title: $albumTitle})
                    MERGE (s:Song {title: $songTitle})
                    SET s.duration = $duration
                    MERGE (al)-[:CONTAINS {trackNumber: $trackNumber}]->(s)
                    """,
                    albumTitle=parsed_data['album_title'],
                    songTitle=track['song_title'],
                    trackNumber=track_number,
                    duration=track.get('duration')
                )

                # Optional: Handle featured artists for songs
                for featured_artist_name in track.get('featured_artists', []):
                    session.run("MERGE (p:Person {name: $personName})", personName=featured_artist_name)
                    session.run("""
                        MATCH (s:Song {title: $songTitle})
                        MATCH (p:Person {name: $personName})
                        MERGE (s)-[:FEATURES]->(p)
                        """,
                        songTitle=track['song_title'],
                        personName=featured_artist_name
                    )

            print(f"Successfully loaded data for album: {parsed_data['album_title']}")

        except Exception as e:
            print(f"Error loading data for album {parsed_data.get('album_title', 'Unknown')}: {e}")

# --- Main Execution Flow ---

def run_pipeline(artist_names: list[str]):
    """
    Orchestrates the entire process from fetching to loading.
    """
    neo4j_driver = None
    try:
        neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        neo4j_driver.verify_connectivity()
        print("Successfully connected to AuraDB.")

        all_processed_albums_data = []

        for artist_name in artist_names:
            print(f"\n--- Processing {artist_name}'s discography ---")
            discography_url = fetch_artist_discography_url(artist_name)

            if not discography_url:
                print(f"Could not find discography page for {artist_name}. Skipping.")
                continue

            discography_title = discography_url.split('/')[-1].replace('_', ' ')
            discography_html = get_wikipedia_page_html(discography_title)

            if not discography_html:
                print(f"Could not retrieve HTML for {discography_title}. Skipping.")
                continue

            album_links = extract_album_titles_from_discography(discography_html)
            print(f"Found {len(album_links)} potential albums for {artist_name}.")

            for album_link in album_links:
                album_title_wiki = album_link['title'] # This is the full Wikipedia page title
                print(f"  Fetching and processing album: {album_title_wiki}")

                album_html_content = get_wikipedia_page_html(album_title_wiki)
                if not album_html_content:
                    print(f"    Failed to get content for {album_title_wiki}. Skipping.")
                    continue

                # --- LLM Integration ---
                # This is where you would call your LLM function.
                # For this example, I'll simulate a dummy output.
                # In a real scenario, you'd uncomment and use extract_album_data_with_llm
                # parsed_album_data = extract_album_data_with_llm(album_html_content, artist_name)
                # if parsed_album_data:
                #     parsed_album_data['wikipedia_url'] = album_link['url'] # Add URL to data
                #     all_processed_albums_data.append(parsed_album_data)
                #     time.sleep(1) # Be polite to LLM API

                # Dummy LLM Output (REMOVE IN REAL IMPLEMENTATION)
                dummy_parsed_data = {
                    "album_title": album_title_wiki.replace(f" ({artist_name.lower()} album)", "").replace(" (album)", ""),
                    "artist_name": artist_name,
                    "release_date": "2000-01-01", # Placeholder, LLM would extract this
                    "genres": ["Pop", "Rock"], # Placeholder
                    "tracks": [
                        {"track_number": 1, "song_title": f"Dummy Song 1 from {album_title_wiki}"},
                        {"track_number": 2, "song_title": f"Dummy Song 2 from {album_title_wiki}", "duration": "3:30"}
                    ],
                    "wikipedia_url": album_link['url']
                }
                all_processed_albums_data.append(dummy_parsed_data)
                time.sleep(0.1) # Be polite to Wikipedia API

        # --- Load all collected data into AuraDB ---
        print("\n--- Starting data loading into AuraDB ---")
        for album_data in all_processed_albums_data:
            load_data_to_auradb(neo4j_driver, album_data)

        print("\n--- All processing and loading complete! ---")

    except Exception as e:
        print(f"An unhandled error occurred: {e}")
    finally:
        if neo4j_driver:
            neo4j_driver.close()
            print("AuraDB connection closed.")

# --- Run the Script ---
if __name__ == "__main__":
    artists_to_process = [
        "Taylor Swift",
        "Ed Sheeran",
        # Add your other 18 artists here
    ]
    run_pipeline(artists_to_process)

```

-----

**Explanation of the Script Structure:**

1.  **Configuration (`--- Configuration ---`)**:

      * `WIKIPEDIA_API_URL`, `USER_AGENT`: Essential for Wikipedia API calls. Remember to set a descriptive `USER_AGENT`.
      * `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`: Your AuraDB connection details. **Crucially, use environment variables (`os.getenv`) for sensitive information like passwords and API keys.**
      * `OPENAI_API_KEY`, `llm`: Placeholder for your LLM setup (e.g., OpenAI's `ChatOpenAI`). You'll need to uncomment and configure this if you use an LLM.

2.  **Data Model Definition (`--- Data Model Definition ---`)**:

      * This section conceptually defines the nodes and relationships you want in your graph.
      * `ALBUM_SCHEMA`: This is a crucial JSON schema that you'll pass to your LLM. It explicitly tells the LLM what structure and properties to extract from the text. This helps ensure consistent output.

3.  **Step 1: Fetch Album List for Each Artist (`--- Step 1: Fetch Album List for Each Artist ---`)**:

      * `fetch_artist_discography_url(artist_name)`:
          * Takes an artist name.
          * Uses the Wikipedia API (`action=query`, `list=search`) to find the *discography page* (e.g., "Taylor Swift discography").
          * Returns the full Wikipedia URL of that discography page.
      * `get_wikipedia_page_html(page_title)`:
          * Takes a Wikipedia page title (e.g., "Taylor Swift discography").
          * Uses the Wikipedia API (`action=parse`, `prop=text`) to fetch the *rendered HTML content* of that page. This is easier to parse for table structures than raw wikitext.
      * `extract_album_titles_from_discography(html_content)`:
          * **This is a critical parsing step.** It uses `BeautifulSoup` to go through the HTML of the discography page.
          * It looks for `<table>` elements, often with a `class='wikitable'`, which are commonly used for discographies.
          * It then tries to extract the album titles and their Wikipedia page URLs.
          * **Important:** The HTML structure of Wikipedia pages can vary. This function provides a *simplified heuristic* and will likely need significant customization and robustness based on the actual HTML you encounter for different artist discographies. You'll need to inspect the HTML of several discography pages (using your browser's developer tools) to make this robust.

4.  **Step 2: Use LLM to Process Page Text and Extract Structured Data (`--- Step 2: Use LLM to Process Page Text and Extract Structured Data ---`)**:

      * `extract_album_data_with_llm(album_page_text, artist_name)`:
          * **(Currently commented out - requires LLM setup)**
          * This is where the magic happens with the LLM. It takes the *full HTML content* of an individual album page (or you could pre-process it to plain text) and the artist name.
          * It constructs a prompt for the LLM, clearly instructing it to extract specific data (album title, release date, genres, tracks, etc.) and, importantly, to adhere to the `ALBUM_SCHEMA` JSON format.
          * `JsonOutputParser` from LangChain helps enforce that the LLM's response is valid JSON according to your schema.
          * **LLM Choice:** You'd replace `ChatOpenAI` with your chosen LLM (e.g., from `langchain_google_genai` for Gemini).
          * **Dummy LLM Output:** For demonstration purposes, I've included a `dummy_parsed_data` section. **You MUST replace this with your actual LLM call once your LLM setup is ready.**

5.  **Step 3: Load Structured Data into AuraDB (`--- Step 3: Load Structured Data into AuraDB ---`)**:

      * `load_data_to_auradb(driver, parsed_data)`:
          * Takes the `neo4j` driver object and the `parsed_data` (the structured JSON output from the LLM) as input.
          * Uses `session.run()` to execute Cypher queries.
          * **`MERGE` statements:** These are crucial. `MERGE` creates a node or relationship if it doesn't exist, or matches it if it does. This prevents duplicate nodes (e.g., multiple "Taylor Swift" artists or duplicate "1989" albums if you run the script multiple times).
          * It creates `Artist`, `Album`, `Song` nodes and the `RELEASED` and `CONTAINS` relationships (with `trackNumber` as a property on the `CONTAINS` relationship).
          * Includes optional handling for `Genre` and `Person` (featured artists) if your LLM extracts them.

6.  **Main Execution Flow (`--- Main Execution Flow ---`)**:

      * `run_pipeline(artist_names)`:
          * This function orchestrates the entire process.
          * Initializes the Neo4j driver.
          * Loops through each `artist_name` provided.
          * For each artist, it finds their discography page, parses it to get album links.
          * Then, it loops through each album, fetches its HTML, and (in a real scenario) sends it to the LLM for extraction.
          * Finally, it iterates through all the collected and parsed album data and loads it into AuraDB.
      * `if __name__ == "__main__":`: This ensures the `run_pipeline` function is called when the script is executed directly.

**How to Use:**

1.  **Save the script** as a `.py` file (e.g., `music_graph_builder.py`).
2.  **Set Environment Variables:**
    ```bash
    export NEO4J_URI="bolt+s://xxxx-xxxx-xxxx.databases.neo4j.io"
    export NEO4J_USERNAME="neo4j"
    export NEO4J_PASSWORD="your_auradb_password"
    # export OPENAI_API_KEY="sk-your_openai_key" # If using OpenAI
    ```
    (On Windows, use `set` instead of `export`).
3.  **Customize the `artists_to_process` list** with your 20 artists.
4.  **Crucially, implement the LLM integration:** Uncomment the LLM related lines, replace `ChatOpenAI` with your chosen LLM (e.g., `ChatGoogleGenerativeAI` for Gemini), and ensure your LLM API key is set.
5.  **Run the script:**
    ```bash
    python music_graph_builder.py
    ```

This script provides a strong foundation for your automated knowledge graph creation\! Remember, the LLM part is powerful but requires careful prompting and potentially some iterative refinement of the `ALBUM_SCHEMA` and the LLM's system message to get the exact structured output you need.