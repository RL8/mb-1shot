# 🎵 Spotify Knowledge Graph Scripts

## 🎯 **Overview**

This directory contains Spotify API integration scripts for building comprehensive music knowledge graphs with era-based consolidation and universal tagging.

---

## 📂 **Scripts Description**

### **🧪 1. `test_spotify_api/`** - API Testing & Validation
- **Purpose**: Tests Spotify API connectivity and validates credentials
- **When to use**: Before running main scripts to ensure setup is correct
- **Output**: API connection status and sample data

### **🎼 2. `spotify_knowledge_builder/`** - **ENHANCED MAIN SCRIPT** ⭐
- **Purpose**: Builds comprehensive knowledge graph with era-based consolidation
- **Features**:
  - ✅ **Era-based consolidation** - Groups albums by natural career periods
  - ✅ **Universal tagging system** - Works for all artists (Taylor Swift, Kanye, BTS, etc.)
  - ✅ **Comprehensive metadata** - Captures full Spotify API data
  - ✅ **Smart deduplication** - Consolidates duplicate tracks across album variants
  - ✅ **Artist-agnostic** - Handles different release patterns automatically

### **⚡ 3. `spotify_knowledge_builder_enhanced/`** - Speed-Optimized Version
- **Purpose**: Faster processing with essential data only
- **Trade-offs**: Less comprehensive but 2-3x faster execution

### **🔧 4. `spotify_knowledge_builder_fixed/`** - Legacy Fixed Version
- **Purpose**: Bug fixes for original implementation
- **Status**: Superseded by main enhanced script

### **🏗️ 5. `music_graph_builder/`** - Core Graph Architecture
- **Purpose**: Foundational graph building components
- **Status**: Integrated into main enhanced script

---

## 🎭 **Era-Based Consolidation System**

### **How It Works**
1. **Era Detection**: Automatically detects natural career periods based on:
   - Time gaps between releases
   - Genre shifts
   - Label changes
   - Musical evolution patterns

2. **Main Album Selection**: Chooses canonical album per era using:
   - Studio albums over singles/compilations
   - Original releases over remasters
   - Earlier releases over later variants
   - Higher track counts (more complete)

3. **Track Consolidation**: Merges duplicate tracks with comprehensive tagging:
   ```
   "Shake It Off" appears on:
   - 1989 (original_release)
   - 1989 Deluxe (deluxe_edition)  
   - 1989 Taylor's Version (taylors_version)
   
   Result: ONE track node with tags: [original_release, deluxe_edition, taylors_version]
   ```

### **Universal Tag Categories**
```python
'release_type': ['original', 'deluxe', 'remaster', 'anniversary']
'content_type': ['standard', 'explicit', 'clean', 'acoustic', 'live']
'exclusivity': ['vault', 'bonus', 'exclusive', 'rare', 'unreleased']
'version': ['radio_edit', 'extended', 'taylors_version']
```

---

## 📊 **Enhanced Metadata Captured**

### **Album Data**
- **Basic**: Name, release date, track count, album type
- **Enhanced**: Genres, popularity, label, copyrights, external IDs
- **Commercial**: Available markets, restrictions, album group
- **Era**: Era name, consolidated albums list, main album designation

### **Track Data**
- **Basic**: Name, duration, track number, explicit flag
- **Audio**: Full audio features (danceability, energy, valence, etc.)
- **Enhanced**: Source albums, comprehensive tags, era assignment
- **Technical**: Key, mode, time signature, disc number

---

## 🚀 **Usage**

### **Quick Start**
```bash
cd scripts/spotify_knowledge_graph/spotify_knowledge_builder/
python spotify_knowledge_builder.py
```

### **Configuration**
Ensure your `.env` file contains:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
NEO4J_URI=your_auradb_uri
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### **Expected Output**
- **Processing Time**: 60-90 minutes for 10 artists
- **Data Volume**: Significantly reduced due to consolidation
- **Quality**: Comprehensive metadata with rich relationships

---

## 🎯 **Benefits for Lyrics Analysis Pipeline**

1. **Cleaner Data**: No duplicate tracks, consolidated per era
2. **Rich Context**: Era information helps understand song themes
3. **Universal System**: Works for any artist's release patterns
4. **Comprehensive Tags**: Perfect for filtering and analysis
5. **Reduced Volume**: Easier to manage and query

---

## 🔄 **Version Comparison**

| Feature | Original | Enhanced | Speed-Optimized |
|---------|----------|----------|-----------------|
| Era Consolidation | ❌ | ✅ | ❌ |
| Universal Tagging | ❌ | ✅ | ❌ |
| Full Metadata | ❌ | ✅ | ❌ |
| Deduplication | ❌ | ✅ | ❌ |
| Processing Speed | Medium | Slower | Fast |
| Data Quality | Basic | Comprehensive | Essential |
| Future-Proof | ❌ | ✅ | ❌ |

**Recommendation**: Use the **Enhanced Main Script** for production lyrics analysis pipeline.

---

## 🏆 **Ready for Integration**

This enhanced system is specifically designed for your lyrics analysis pipeline, providing:
- Clean, consolidated track data
- Rich era context for thematic analysis  
- Universal tagging for advanced filtering
- Comprehensive metadata for deep insights

Perfect foundation for Week 1 of your lyrics collection strategy! 🎵 