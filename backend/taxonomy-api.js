const express = require('express');
const router = express.Router();

const taxonomyStats = {
  totalSongs: 232,
  energyDistribution: { 'Chill': 8, 'Moderate': 84, 'Energetic': 95, 'High Energy': 45 },
  moodDistribution: { 'Melancholic': 36, 'Reflective': 89, 'Neutral': 76, 'Uplifting': 23, 'Euphoric': 8 },
  timeDistribution: { 'Morning': 41, 'Night': 21, 'Any Time': 170 },
  activityDistribution: { 'Study': 52, 'Workout': 41, 'Social': 31, 'General': 108 },
  averageEnergy: 0.561, averageValence: 0.393, averageIntimacy: 0.436, averageDanceability: 0.587
};

const sampleSongs = [
  { id: 1, title: "Anti-Hero", albumCode: "MIDNIGHTS", taxonomy_energy_level: 0.6, taxonomy_energy_label: "Moderate", taxonomy_emotional_valence: 0.3, taxonomy_emotional_label: "Reflective", taxonomy_time_primary: "Night", taxonomy_activity_category: "General", taxonomy_intimacy_level: 0.7, taxonomy_danceability: 0.5 },
  { id: 2, title: "Shake It Off", albumCode: "1989", taxonomy_energy_level: 0.9, taxonomy_energy_label: "High Energy", taxonomy_emotional_valence: 0.8, taxonomy_emotional_label: "Euphoric", taxonomy_time_primary: "Any Time", taxonomy_activity_category: "Social", taxonomy_intimacy_level: 0.2, taxonomy_danceability: 0.9 }
];

router.get('/stats', (req, res) => {
  res.json({ success: true, data: taxonomyStats, message: 'Taxonomy statistics retrieved successfully' });
});

router.get('/songs/with-taxonomies', (req, res) => {
  const { energy, mood, time, activity, limit = 20, offset = 0 } = req.query;
  let filteredSongs = [...sampleSongs];
  
  if (energy) filteredSongs = filteredSongs.filter(song => energy.split(',').includes(song.taxonomy_energy_label));
  if (mood) filteredSongs = filteredSongs.filter(song => mood.split(',').includes(song.taxonomy_emotional_label));
  
  const paginatedSongs = filteredSongs.slice(parseInt(offset), parseInt(offset) + parseInt(limit));
  res.json({ success: true, songs: paginatedSongs, total: filteredSongs.length, offset: parseInt(offset), limit: parseInt(limit), message: 'Retrieved songs with taxonomy data' });
});

module.exports = router;
