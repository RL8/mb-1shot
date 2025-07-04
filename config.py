# Configuration for Taylor Swift Word-Level Data Integration

import os
from pathlib import Path

# AuraDB Connection Settings
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://your-instance.databases.neo4j.io")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password")

# File Paths
BASE_DIR = Path(__file__).parent
TAYLOR_SWIFT_DATA_DIR = BASE_DIR / "taylor_swift_data"
WORD_DATA_CSV = TAYLOR_SWIFT_DATA_DIR / "Taylor_Swift_Words" / "taylor_swift_words_data.csv"

# Integration Settings
MAX_WORDS_PER_SONG = 50  # Limit word relationships per song
BATCH_SIZE = 100  # Number of songs to process in each batch

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 