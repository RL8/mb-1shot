#!/usr/bin/env python3
"""
Configuration for Unified Word Identifier & Music Taxonomy System
Merges settings from concept.md, README.md, and additional_fields.md
"""

import os
from pathlib import Path

# ======= DATABASE CONNECTION =======

# AuraDB Connection Settings (from README.md)
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://your-instance.databases.neo4j.io")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password")

# Connection Optimization (from concept.md)
CONNECTION_POOL_SIZE = 100  # High concurrency for bulk operations
CONNECTION_TIMEOUT = 60
MAX_RETRY_TIME = 30

# ======= BATCH PROCESSING SETTINGS =======

# Processing Configuration (from README.md)
BATCH_SIZE = 50  # Songs per batch (memory optimized)
MAX_WORDS_PER_SONG = 500  # Reasonable limit for processing
VALIDATION_SAMPLE_SIZE = 10  # Songs to test before full implementation

# ======= WORD IDENTIFIER SYSTEM =======

# Word ID Configuration (from concept.md + README.md)
WORD_ID_PREFIX = "word_"  # Consistent prefix
WORD_ID_HASH_LENGTH = 8  # MD5 hash truncation
WORD_FREQUENCY_THRESHOLD = 1  # Minimum frequency to include

# System Versioning
WORD_SYSTEM_VERSION = "unified_v1.0"
TAXONOMY_VERSION = "unified_v1.0"

# ======= MUSIC TAXONOMY SETTINGS =======

# Taxonomy Calculation Weights (from additional_fields.md)
ENERGY_WEIGHTS = {
    'audio_energy': 0.4,
    'tempo_factor': 0.3, 
    'loudness_factor': 0.2,
    'vocabulary_complexity': 0.1  # Enhanced with word data
}

VALENCE_WEIGHTS = {
    'base_valence': 0.8,
    'lyrical_enhancement': 0.2  # Simpler words = more direct emotion
}

COMPLEXITY_WEIGHTS = {
    'audio_complexity': 0.6,
    'lyrical_complexity': 0.4  # Word-based enhancement
}

FOCUS_WEIGHTS = {
    'instrumentalness': 0.4,
    'low_speechiness': 0.3,
    'low_energy': 0.2,
    'simple_vocabulary': 0.1  # Enhanced with word analysis
}

# Taxonomy Confidence Thresholds
MIN_CALCULATION_CONFIDENCE = 0.7
TARGET_CALCULATION_CONFIDENCE = 0.85

# ======= PERFORMANCE OPTIMIZATION =======

# Index Configuration (from concept.md)
CREATE_INDEXES = True
VALIDATE_INDEXES = True

# Performance Targets
TARGET_STORAGE_REDUCTION = 0.6  # 60% reduction goal
TARGET_QUERY_SPEEDUP = 3.0  # 3x faster minimum
TARGET_RECONSTRUCTION_ACCURACY = 1.0  # 100% accuracy required

# ======= VALIDATION SETTINGS =======

# Quality Assurance (from README.md)
ENABLE_RECONSTRUCTION_VALIDATION = True
ENABLE_PERFORMANCE_BENCHMARKING = True
ENABLE_CONFIDENCE_CHECKING = True

# Validation Thresholds
MIN_RECONSTRUCTION_ACCURACY = 0.99  # 99% minimum
MAX_BATCH_FAILURE_RATE = 0.05  # 5% max failures
MIN_COVERAGE_PERCENTAGE = 0.95  # 95% song coverage

# ======= LOGGING & MONITORING =======

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
ENABLE_PROGRESS_TRACKING = True

# Performance Monitoring
TRACK_EXECUTION_TIME = True
TRACK_MEMORY_USAGE = True
TRACK_QUERY_PERFORMANCE = True

# ======= FILE PATHS =======

# Project Structure
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True) 
LOGS_DIR.mkdir(exist_ok=True)

# ======= FEATURE FLAGS =======

# Implementation Phases
ENABLE_PHASE_1_WORD_IDS = True
ENABLE_PHASE_2_TAXONOMIES = True  
ENABLE_PHASE_3_OPTIMIZATION = True

# Advanced Features
ENABLE_WORD_COMPLEXITY_ANALYSIS = True
ENABLE_CROSS_SONG_VOCABULARY = True
ENABLE_LYRICAL_ENHANCEMENT = True

# Safety Features
ENABLE_BACKUP_BEFORE_CHANGES = True
ENABLE_ROLLBACK_CAPABILITY = True
ENABLE_DRY_RUN_MODE = False  # Set to True for testing

# ======= TAXONOMY LABEL MAPPINGS =======

# Energy Level Labels (from additional_fields.md)
ENERGY_LABELS = {
    (0.8, 1.0): "High Energy",
    (0.6, 0.8): "Energetic", 
    (0.4, 0.6): "Moderate",
    (0.0, 0.4): "Chill"
}

# Emotional Valence Labels
EMOTIONAL_LABELS = {
    (0.8, 1.0): "Euphoric",
    (0.6, 0.8): "Uplifting",
    (0.4, 0.6): "Neutral", 
    (0.2, 0.4): "Reflective",
    (0.0, 0.2): "Melancholic"
}

# Complexity Labels
COMPLEXITY_LABELS = {
    (0.75, 1.0): "Very Complex",
    (0.5, 0.75): "Complex",
    (0.25, 0.5): "Moderate", 
    (0.0, 0.25): "Simple"
}

# Intimacy Labels
INTIMACY_LABELS = {
    (0.8, 1.0): "Very Intimate",
    (0.6, 0.8): "Intimate",
    (0.4, 0.6): "Personal",
    (0.2, 0.4): "Social",
    (0.0, 0.2): "Public"
}

# Focus Labels
FOCUS_LABELS = {
    (0.75, 1.0): "Ideal Focus",
    (0.5, 0.75): "Suitable",
    (0.25, 0.5): "Background",
    (0.0, 0.25): "Distracting"
}

# Time of Day Categories
TIME_CATEGORIES = [
    "3AM Thoughts", "Morning Motivation", "Afternoon Chill", 
    "Evening Party", "Wind Down", "Any Time"
]

# Activity Categories  
ACTIVITY_CATEGORIES = [
    "High Intensity Workout", "Deep Focus", "Cooking", "Driving",
    "Relaxing", "Dancing", "General Listening"
]

# ======= VALIDATION FUNCTIONS =======

def validate_config():
    """Validate configuration settings"""
    assert 0 < BATCH_SIZE <= 100, "Batch size must be between 1 and 100"
    assert 0 < CONNECTION_POOL_SIZE <= 200, "Connection pool too large"
    assert MIN_CALCULATION_CONFIDENCE <= TARGET_CALCULATION_CONFIDENCE
    assert all(sum(weights.values()) == 1.0 for weights in [
        ENERGY_WEIGHTS, VALENCE_WEIGHTS, COMPLEXITY_WEIGHTS, FOCUS_WEIGHTS
    ]), "Taxonomy weights must sum to 1.0"
    
    print("✅ Configuration validation passed")

if __name__ == "__main__":
    validate_config() 