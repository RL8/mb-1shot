const express = require('express');
const router = express.Router();

// Mock taxonomy stats based on our Phase 1 AuraDB results
// In production, this would query AuraDB directly
const taxonomyStats = {
  totalSongs: 232,
  energyDistribution: {
    'Chill': 8,
    'Moderate': 84, 
    'Energetic': 95,
    'High Energy': 45
  },
  moodDistribution: {
    'Melancholic': 36,
    'Reflective': 89,
    'Neutral': 76,
    'Uplifting': 23,
    'Euphoric': 8
  },
  timeDistribution: {
    'Morning': 41,
    'Night': 21,
    'Any Time': 170
  },
  activityDistribution: {
    'Study': 52,
    'Workout': 41,
    'Social': 31,
    'General': 108
  },
  averageEnergy: 0.561,
  averageValence: 0.393,
  averageIntimacy: 0.436,
  averageDanceability: 0.587
};

// Sample songs with taxonomy data
const sampleSongs = [
  {
    id: 1,
    title: "Anti-Hero",
    albumCode: "MIDNIGHTS",
    taxonomy_energy_level: 0.6,
    taxonomy_energy_label: "Moderate",
    taxonomy_emotional_valence: 0.3,
    taxonomy_emotional_label: "Reflective",
    taxonomy_time_primary: "Night",
    taxonomy_activity_category: "General",
    taxonomy_intimacy_level: 0.7,
    taxonomy_danceability: 0.5
  },
  {
    id: 2,
    title: "Shake It Off",
    albumCode: "1989",
    taxonomy_energy_level: 0.9,
    taxonomy_energy_label: "High Energy",
    taxonomy_emotional_valence: 0.8,
    taxonomy_emotional_label: "Euphoric",
    taxonomy_time_primary: "Any Time",
    taxonomy_activity_category: "Social",
    taxonomy_intimacy_level: 0.2,
    taxonomy_danceability: 0.9
  },
  {
    id: 3,
    title: "All Too Well",
    albumCode: "RED",
    taxonomy_energy_level: 0.4,
    taxonomy_energy_label: "Moderate",
    taxonomy_emotional_valence: 0.2,
    taxonomy_emotional_label: "Melancholic",
    taxonomy_time_primary: "Night",
    taxonomy_activity_category: "General",
    taxonomy_intimacy_level: 0.9,
    taxonomy_danceability: 0.3
  },
  {
    id: 4,
    title: "22",
    albumCode: "RED",
    taxonomy_energy_level: 0.8,
    taxonomy_energy_label: "Energetic",
    taxonomy_emotional_valence: 0.9,
    taxonomy_emotional_label: "Euphoric",
    taxonomy_time_primary: "Any Time",
    taxonomy_activity_category: "Social",
    taxonomy_intimacy_level: 0.3,
    taxonomy_danceability: 0.8
  },
  {
    id: 5,
    title: "cardigan",
    albumCode: "FOLKLORE",
    taxonomy_energy_level: 0.3,
    taxonomy_energy_label: "Chill",
    taxonomy_emotional_valence: 0.4,
    taxonomy_emotional_label: "Reflective",
    taxonomy_time_primary: "Night",
    taxonomy_activity_category: "Study",
    taxonomy_intimacy_level: 0.8,
    taxonomy_danceability: 0.2
  },
  {
    id: 6,
    title: "ME!",
    albumCode: "LOVER",
    taxonomy_energy_level: 0.9,
    taxonomy_energy_label: "High Energy",
    taxonomy_emotional_valence: 0.9,
    taxonomy_emotional_label: "Euphoric",
    taxonomy_time_primary: "Morning",
    taxonomy_activity_category: "Workout",
    taxonomy_intimacy_level: 0.2,
    taxonomy_danceability: 0.9
  },
  {
    id: 7,
    title: "folklore",
    albumCode: "FOLKLORE",
    taxonomy_energy_level: 0.25,
    taxonomy_energy_label: "Chill",
    taxonomy_emotional_valence: 0.3,
    taxonomy_emotional_label: "Reflective",
    taxonomy_time_primary: "Night",
    taxonomy_activity_category: "Study",
    taxonomy_intimacy_level: 0.9,
    taxonomy_danceability: 0.15
  },
  {
    id: 8,
    title: "Blank Space",
    albumCode: "1989",
    taxonomy_energy_level: 0.7,
    taxonomy_energy_label: "Energetic",
    taxonomy_emotional_valence: 0.6,
    taxonomy_emotional_label: "Neutral",
    taxonomy_time_primary: "Any Time",
    taxonomy_activity_category: "Social",
    taxonomy_intimacy_level: 0.4,
    taxonomy_danceability: 0.7
  },
  {
    id: 9,
    title: "Love Story",
    albumCode: "FEARLESS",
    taxonomy_energy_level: 0.6,
    taxonomy_energy_label: "Moderate",
    taxonomy_emotional_valence: 0.8,
    taxonomy_emotional_label: "Uplifting",
    taxonomy_time_primary: "Any Time",
    taxonomy_activity_category: "General",
    taxonomy_intimacy_level: 0.5,
    taxonomy_danceability: 0.6
  },
  {
    id: 10,
    title: "Cruel Summer",
    albumCode: "LOVER",
    taxonomy_energy_level: 0.8,
    taxonomy_energy_label: "Energetic",
    taxonomy_emotional_valence: 0.7,
    taxonomy_emotional_label: "Uplifting",
    taxonomy_time_primary: "Any Time",
    taxonomy_activity_category: "Social",
    taxonomy_intimacy_level: 0.3,
    taxonomy_danceability: 0.8
  }
];

// GET /api/taxonomy/stats - Get taxonomy statistics
router.get('/stats', (req, res) => {
  try {
    res.json({
      success: true,
      data: taxonomyStats,
      message: 'Taxonomy statistics retrieved successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve taxonomy statistics',
      details: error.message
    });
  }
});

// GET /api/songs/with-taxonomies - Get songs with taxonomy data
router.get('/songs/with-taxonomies', (req, res) => {
  try {
    const { 
      energy, 
      mood, 
      time, 
      activity, 
      limit = 20, 
      offset = 0 
    } = req.query;

    let filteredSongs = [...sampleSongs];

    // Apply filters
    if (energy) {
      const energyLevels = energy.split(',');
      filteredSongs = filteredSongs.filter(song => 
        energyLevels.includes(song.taxonomy_energy_label)
      );
    }

    if (mood) {
      const moods = mood.split(',');
      filteredSongs = filteredSongs.filter(song => 
        moods.includes(song.taxonomy_emotional_label)
      );
    }

    if (time) {
      const times = time.split(',');
      filteredSongs = filteredSongs.filter(song => 
        times.includes(song.taxonomy_time_primary)
      );
    }

    if (activity) {
      const activities = activity.split(',');
      filteredSongs = filteredSongs.filter(song => 
        activities.includes(song.taxonomy_activity_category)
      );
    }

    // Apply pagination
    const paginatedSongs = filteredSongs.slice(
      parseInt(offset), 
      parseInt(offset) + parseInt(limit)
    );

    res.json({
      success: true,
      songs: paginatedSongs,
      total: filteredSongs.length,
      offset: parseInt(offset),
      limit: parseInt(limit),
      message: `Retrieved ${paginatedSongs.length} songs with taxonomy data`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve songs with taxonomies',
      details: error.message
    });
  }
});

// GET /api/songs/:id/taxonomy - Get detailed taxonomy for a specific song
router.get('/songs/:id/taxonomy', (req, res) => {
  try {
    const songId = parseInt(req.params.id);
    const song = sampleSongs.find(s => s.id === songId);

    if (!song) {
      return res.status(404).json({
        success: false,
        error: 'Song not found',
        message: `No song found with ID ${songId}`
      });
    }

    // Return detailed taxonomy analysis
    const detailedTaxonomy = {
      songInfo: {
        id: song.id,
        title: song.title,
        album: song.albumCode
      },
      energyAnalysis: {
        level: song.taxonomy_energy_level,
        label: song.taxonomy_energy_label,
        description: getEnergyDescription(song.taxonomy_energy_label)
      },
      emotionalAnalysis: {
        valence: song.taxonomy_emotional_valence,
        label: song.taxonomy_emotional_label,
        description: getMoodDescription(song.taxonomy_emotional_label)
      },
      contextualAnalysis: {
        timeOfDay: song.taxonomy_time_primary,
        activityContext: song.taxonomy_activity_category,
        intimacyLevel: song.taxonomy_intimacy_level,
        danceability: song.taxonomy_danceability
      },
      recommendations: generateRecommendations(song)
    };

    res.json({
      success: true,
      data: detailedTaxonomy,
      message: `Detailed taxonomy analysis for "${song.title}"`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve song taxonomy',
      details: error.message
    });
  }
});

// Helper functions
function getEnergyDescription(energyLabel) {
  const descriptions = {
    'Chill': 'Relaxed and mellow, perfect for unwinding',
    'Moderate': 'Balanced energy, suitable for most activities',
    'Energetic': 'Upbeat and lively, great for motivation',
    'High Energy': 'Intense and powerful, ideal for workouts'
  };
  return descriptions[energyLabel] || 'Energy level analysis';
}

function getMoodDescription(moodLabel) {
  const descriptions = {
    'Melancholic': 'Deeply emotional and introspective',
    'Reflective': 'Thoughtful and contemplative',
    'Neutral': 'Balanced emotional tone',
    'Uplifting': 'Positive and encouraging',
    'Euphoric': 'Joyful and exhilarating'
  };
  return descriptions[moodLabel] || 'Emotional analysis';
}

function generateRecommendations(song) {
  const recommendations = [];

  // Time-based recommendations
  if (song.taxonomy_time_primary === 'Morning') {
    recommendations.push('Perfect for your morning routine or workout playlist');
  } else if (song.taxonomy_time_primary === 'Night') {
    recommendations.push('Ideal for evening wind-down or late-night reflection');
  }

  // Activity-based recommendations
  if (song.taxonomy_activity_category === 'Study') {
    recommendations.push('Great background music for focused work or studying');
  } else if (song.taxonomy_activity_category === 'Workout') {
    recommendations.push('Excellent for high-intensity workouts and fitness');
  } else if (song.taxonomy_activity_category === 'Social') {
    recommendations.push('Perfect for parties, gatherings, or social events');
  }

  // Energy-based recommendations
  if (song.taxonomy_energy_level > 0.7) {
    recommendations.push('High energy track - great for motivation and movement');
  } else if (song.taxonomy_energy_level < 0.4) {
    recommendations.push('Calm and soothing - ideal for relaxation');
  }

  return recommendations;
}

module.exports = router; 