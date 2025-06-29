// Music Besties AuraDB Schema Setup
// Run these Cypher queries in your AuraDB instance to set up the music knowledge graph

// Create indexes for better performance
CREATE INDEX artist_name_index IF NOT EXISTS FOR (a:Artist) ON (a.name);
CREATE INDEX album_name_index IF NOT EXISTS FOR (al:Album) ON (al.name);
CREATE INDEX song_title_index IF NOT EXISTS FOR (s:Song) ON (s.title);

// Taylor Swift - Complete discography with relationships
CREATE (taylor:Artist {
  name: "Taylor Swift",
  genre: "Pop/Country", 
  activeYears: "2006-Present",
  spotifyId: "06HL4z0CvFAxyc27GXpf02",
  country: "United States",
  debutYear: 2006,
  grammyWins: 12,
  themes: ["love", "relationships", "personal growth", "storytelling"]
});

// Taylor Swift Albums
CREATE (debut:Album {name: "Taylor Swift", year: 2006, genre: "Country", popularity: 75, themes: ["young love", "small town life"]});
CREATE (fearless:Album {name: "Fearless", year: 2008, genre: "Country", popularity: 92, themes: ["love", "heartbreak", "growing up"]});
CREATE (speakNow:Album {name: "Speak Now", year: 2010, genre: "Country Pop", popularity: 85, themes: ["independence", "personal stories"]});
CREATE (red:Album {name: "Red", year: 2012, genre: "Pop", popularity: 88, themes: ["passionate love", "loss", "transition"]});
CREATE (nineteen89:Album {name: "1989", year: 2014, genre: "Pop", popularity: 94, themes: ["new beginnings", "self-discovery"]});
CREATE (reputation:Album {name: "Reputation", year: 2017, genre: "Pop", popularity: 82, themes: ["reputation", "revenge", "love"]});
CREATE (lover:Album {name: "Lover", year: 2019, genre: "Pop", popularity: 89, themes: ["love", "acceptance", "celebration"]});
CREATE (folklore:Album {name: "Folklore", year: 2020, genre: "Indie Folk", popularity: 96, themes: ["storytelling", "nostalgia", "nature"]});
CREATE (evermore:Album {name: "Evermore", year: 2020, genre: "Indie Folk", popularity: 90, themes: ["winter", "melancholy", "stories"]});
CREATE (midnights:Album {name: "Midnights", year: 2022, genre: "Pop", popularity: 98, themes: ["sleeplessness", "self-reflection", "midnight thoughts"]});

// Connect Taylor to her albums
CREATE (taylor)-[:RELEASED]->(debut);
CREATE (taylor)-[:RELEASED]->(fearless);
CREATE (taylor)-[:RELEASED]->(speakNow);
CREATE (taylor)-[:RELEASED]->(red);
CREATE (taylor)-[:RELEASED]->(nineteen89);
CREATE (taylor)-[:RELEASED]->(reputation);
CREATE (taylor)-[:RELEASED]->(lover);
CREATE (taylor)-[:RELEASED]->(folklore);
CREATE (taylor)-[:RELEASED]->(evermore);
CREATE (taylor)-[:RELEASED]->(midnights);

// Key Taylor Swift songs
CREATE (cardigan:Song {title: "cardigan", themes: ["nostalgia", "love", "storytelling"], keySignature: "Bb major", album: "Folklore"});
CREATE (allTooWell:Song {title: "All Too Well", themes: ["heartbreak", "memory", "loss"], keySignature: "C major", album: "Red"});
CREATE (shakeItOff:Song {title: "Shake It Off", themes: ["resilience", "self-acceptance"], keySignature: "G major", album: "1989"});

CREATE (folklore)-[:CONTAINS]->(cardigan);
CREATE (red)-[:CONTAINS]->(allTooWell);
CREATE (nineteen89)-[:CONTAINS]->(shakeItOff);

// Taylor's influences
CREATE (joni:Artist {name: "Joni Mitchell", genre: "Folk", activeYears: "1964-Present", influence: "storytelling and confessional songwriting"});
CREATE (dolly:Artist {name: "Dolly Parton", genre: "Country", activeYears: "1967-Present", influence: "country storytelling"});
CREATE (shania:Artist {name: "Shania Twain", genre: "Country Pop", activeYears: "1983-Present", influence: "country-pop crossover"});

CREATE (taylor)-[:INFLUENCED_BY]->(joni);
CREATE (taylor)-[:INFLUENCED_BY]->(dolly);
CREATE (taylor)-[:INFLUENCED_BY]->(shania);

// The Weeknd - Complete setup
CREATE (weeknd:Artist {
  name: "The Weeknd",
  genre: "R&B/Pop",
  activeYears: "2010-Present",
  realName: "Abel Tesfaye",
  country: "Canada",
  debutYear: 2010,
  grammyWins: 4,
  themes: ["dark romance", "hedonism", "fame", "relationships"]
});

// The Weeknd Albums
CREATE (hob:Album {name: "House of Balloons", year: 2011, genre: "Alternative R&B", popularity: 85, themes: ["dark romance", "drugs", "nightlife"]});
CREATE (thursday:Album {name: "Thursday", year: 2011, genre: "Alternative R&B", popularity: 82, themes: ["loneliness", "excess"]});
CREATE (trilogy:Album {name: "Trilogy", year: 2012, genre: "Alternative R&B", popularity: 88, themes: ["compilation", "definitive era"]});
CREATE (kissLand:Album {name: "Kiss Land", year: 2013, genre: "Alternative R&B", popularity: 76, themes: ["isolation", "touring life"]});
CREATE (bbtm:Album {name: "Beauty Behind the Madness", year: 2015, genre: "R&B Pop", popularity: 94, themes: ["mainstream success", "relationships"]});
CREATE (starboy:Album {name: "Starboy", year: 2016, genre: "Pop R&B", popularity: 91, themes: ["fame", "transformation"]});
CREATE (afterHours:Album {name: "After Hours", year: 2020, genre: "Synth-pop", popularity: 96, themes: ["heartbreak", "redemption", "80s nostalgia"]});
CREATE (dawnFM:Album {name: "Dawn FM", year: 2022, genre: "Synth-pop", popularity: 89, themes: ["purgatory", "radio concept", "reflection"]});

CREATE (weeknd)-[:RELEASED]->(hob);
CREATE (weeknd)-[:RELEASED]->(thursday);
CREATE (weeknd)-[:RELEASED]->(trilogy);
CREATE (weeknd)-[:RELEASED]->(kissLand);
CREATE (weeknd)-[:RELEASED]->(bbtm);
CREATE (weeknd)-[:RELEASED]->(starboy);
CREATE (weeknd)-[:RELEASED]->(afterHours);
CREATE (weeknd)-[:RELEASED]->(dawnFM);

// The Weeknd's influences
CREATE (prince:Artist {name: "Prince", genre: "Pop/R&B", activeYears: "1976-2016", influence: "funk and R&B innovation"});
CREATE (mj:Artist {name: "Michael Jackson", genre: "Pop", activeYears: "1964-2009", influence: "pop perfection and performance"});

CREATE (weeknd)-[:INFLUENCED_BY]->(prince);
CREATE (weeknd)-[:INFLUENCED_BY]->(mj);

// Billie Eilish
CREATE (billie:Artist {
  name: "Billie Eilish",
  genre: "Alternative Pop", 
  activeYears: "2016-Present",
  country: "United States",
  debutYear: 2016,
  grammyWins: 7,
  themes: ["mental health", "youth", "darkness", "vulnerability"]
});

// Billie's Albums
CREATE (dontSmile:Album {name: "dont smile at me (EP)", year: 2017, genre: "Alternative Pop", popularity: 78, themes: ["teenage angst", "debut"]});
CREATE (wwafawdwg:Album {name: "When We All Fall Asleep, Where Do We Go?", year: 2019, genre: "Alternative Pop", popularity: 95, themes: ["sleep", "nightmares", "youth"]});
CREATE (hte:Album {name: "Happier Than Ever", year: 2021, genre: "Alternative Pop", popularity: 92, themes: ["growth", "relationships", "self-reflection"]});

CREATE (billie)-[:RELEASED]->(dontSmile);
CREATE (billie)-[:RELEASED]->(wwafawdwg);
CREATE (billie)-[:RELEASED]->(hte);

// Cross-artist relationships
CREATE (taylor)-[:COLLABORATED_WITH {song: "Soon You'll Get Better", type: "featured artist"}]->(billie);
CREATE (weeknd)-[:INFLUENCED {era: "After Hours"}]->(mj);

// Genre relationships
CREATE (indie:Genre {name: "Indie Folk", characteristics: ["acoustic", "storytelling", "intimate", "nature themes"]});
CREATE (altPop:Genre {name: "Alternative Pop", characteristics: ["experimental", "youth-focused", "genre-blending"]});
CREATE (rbPop:Genre {name: "R&B Pop", characteristics: ["smooth vocals", "pop sensibility", "R&B roots"]});

CREATE (folklore)-[:BELONGS_TO]->(indie);
CREATE (evermore)-[:BELONGS_TO]->(indie);
CREATE (wwafawdwg)-[:BELONGS_TO]->(altPop);
CREATE (afterHours)-[:BELONGS_TO]->(rbPop);

// Production relationships - key producers
CREATE (aaron:Producer {name: "Aaron Dessner", known_for: "The National, Taylor Swift's indie era"});
CREATE (jack:Producer {name: "Jack Antonoff", known_for: "Bleachers, Taylor Swift, Lorde"});
CREATE (finneas:Producer {name: "FINNEAS", known_for: "Billie Eilish's brother and producer"});

CREATE (folklore)-[:PRODUCED_BY]->(aaron);
CREATE (evermore)-[:PRODUCED_BY]->(aaron);
CREATE (lover)-[:PRODUCED_BY]->(jack);
CREATE (wwafawdwg)-[:PRODUCED_BY]->(finneas);
CREATE (hte)-[:PRODUCED_BY]->(finneas);

// Thematic connections
CREATE (storytelling:Theme {name: "Storytelling", artists: ["Taylor Swift", "Joni Mitchell"], characteristics: ["narrative lyrics", "character development", "vivid imagery"]});
CREATE (darkRomance:Theme {name: "Dark Romance", artists: ["The Weeknd"], characteristics: ["complex relationships", "hedonistic themes", "emotional intensity"]});
CREATE (youthAnxiety:Theme {name: "Youth Anxiety", artists: ["Billie Eilish"], characteristics: ["mental health", "generational issues", "vulnerability"]});

CREATE (taylor)-[:EXPLORES]->(storytelling);
CREATE (weeknd)-[:EXPLORES]->(darkRomance);
CREATE (billie)-[:EXPLORES]->(youthAnxiety);

// Query examples for AG-UI to use:

// Find artistic influences:
// MATCH (artist:Artist {name: $artistName})-[:INFLUENCED_BY*1..2]->(influence)
// RETURN influence.name, influence.genre

// Album evolution analysis:  
// MATCH (artist:Artist {name: $artistName})-[:RELEASED]->(album:Album)
// RETURN album.name, album.year, album.genre, album.themes
// ORDER BY album.year

// Thematic analysis:
// MATCH (artist:Artist {name: $artistName})-[:EXPLORES]->(theme:Theme)
// RETURN theme.name, theme.characteristics

// Production network:
// MATCH (artist:Artist {name: $artistName})-[:RELEASED]->(album)-[:PRODUCED_BY]->(producer)
// RETURN producer.name, count(album) as collaborations
// ORDER BY collaborations DESC

// Cross-artist connections:
// MATCH (artist1:Artist {name: $artistName})-[:COLLABORATED_WITH|INFLUENCED|INFLUENCED_BY]-(artist2:Artist)
// RETURN artist2.name, type(r) as relationship_type 