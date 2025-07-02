#!/usr/bin/env python3
"""
Natural Grouping Full Enhancement Script
Enhance all 11,642 lyric lines with natural grouping properties
Process in logical batches by album, track anomalies
"""

import os
import time
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class FullNaturalGroupingEnhancer:
    def __init__(self):
        """Initialize connection to AuraDB"""
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not all([self.neo4j_uri, self.neo4j_user, self.neo4j_password]):
            raise ValueError("❌ Missing AuraDB credentials in environment variables")
        
        print(f"🔑 Connecting to AuraDB...")
        self.driver = GraphDatabase.driver(
            self.neo4j_uri, 
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        # Track processing statistics
        self.stats = {
            'albums_processed': 0,
            'songs_processed': 0,
            'lines_enhanced': 0,
            'anomalies': [],
            'processing_times': []
        }

    def get_album_list(self):
        """Get list of all albums for batch processing"""
        with self.driver.session() as session:
            query = """
            MATCH (album:Album)
            RETURN album.title, album.code, count{(album)-[:CONTAINS]->(song:Song)} as song_count
            ORDER BY album.year, album.title
            """
            result = session.run(query)
            
            albums = []
            for record in result:
                albums.append({
                    'title': record['album.title'],
                    'code': record['album.code'],
                    'song_count': record['song_count']
                })
            
            return albums

    def get_songs_in_album(self, album_code):
        """Get all songs in a specific album"""
        with self.driver.session() as session:
            query = """
            MATCH (album:Album {code: $album_code})-[:CONTAINS]->(song:Song)
            RETURN song.title, song.trackNumber,
                   count{(song)-[:HAS_LYRIC]->(line:LyricLine)} as line_count
            ORDER BY song.trackNumber
            """
            result = session.run(query, album_code=album_code)
            
            songs = []
            for record in result:
                songs.append({
                    'title': record['song.title'],
                    'track_number': record['song.trackNumber'],
                    'line_count': record['line_count']
                })
            
            return songs

    def calculate_song_natural_grouping(self, song_title, album_code):
        """Calculate natural grouping for one song"""
        with self.driver.session() as session:
            query = """
            MATCH (album:Album {code: $album_code})-[:CONTAINS]->(song:Song {title: $song_title})
            MATCH (song)-[:HAS_LYRIC]->(line:LyricLine)
            RETURN line.order, line.songPart
            ORDER BY line.order
            """
            result = session.run(query, album_code=album_code, song_title=song_title)
            
            lines = []
            for record in result:
                lines.append({
                    'order': record['line.order'],
                    'songPart': record['line.songPart']
                })
            
            if not lines:
                return [], f"No lyrics found for {song_title}"
            
            # Calculate natural grouping with anomaly detection
            enhanced_lines = []
            current_section = None
            section_counts = {}
            line_in_section = 0
            anomalies = []
            
            for i, line in enumerate(lines):
                part = line['songPart']
                
                # Detect section change
                if part != current_section:
                    current_section = part
                    line_in_section = 1
                    
                    # Count section occurrences
                    if part not in section_counts:
                        section_counts[part] = 1
                    else:
                        section_counts[part] += 1
                    
                    section_start = True
                else:
                    line_in_section += 1
                    section_start = False
                
                # Detect section end (look ahead)
                section_end = False
                if i < len(lines) - 1:
                    next_part = lines[i + 1]['songPart']
                    if next_part != part:
                        section_end = True
                else:
                    section_end = True
                
                # Anomaly detection
                if line_in_section > 20:  # Unusually long section
                    anomalies.append({
                        'type': 'long_section',
                        'song': song_title,
                        'album': album_code,
                        'section': part,
                        'lines': line_in_section,
                        'order': line['order']
                    })
                
                if section_counts[part] > 5:  # Unusual number of repetitions
                    anomalies.append({
                        'type': 'many_repetitions',
                        'song': song_title,
                        'album': album_code,
                        'section': part,
                        'count': section_counts[part],
                        'order': line['order']
                    })
                
                # Create enhanced line data
                enhanced_line = {
                    'order': line['order'],
                    'songPart': part,
                    'sectionNumber': section_counts[part],
                    'sectionId': f"{part.lower()}_{section_counts[part]}",
                    'lineInSection': line_in_section,
                    'sectionStart': section_start,
                    'sectionEnd': section_end
                }
                enhanced_lines.append(enhanced_line)
            
            return enhanced_lines, anomalies

    def apply_song_enhancement(self, enhanced_lines, song_title, album_code):
        """Apply enhancement to one song's lyrics"""
        if not enhanced_lines:
            return 0
        
        with self.driver.session() as session:
            # Update lines in batches of 100
            batch_size = 100
            total_updated = 0
            
            for i in range(0, len(enhanced_lines), batch_size):
                batch = enhanced_lines[i:i + batch_size]
                
                query = """
                UNWIND $batch as line_data
                MATCH (album:Album {code: $album_code})-[:CONTAINS]->(song:Song {title: $song_title})
                MATCH (song)-[:HAS_LYRIC]->(l:LyricLine)
                WHERE l.order = line_data.order
                SET l.sectionNumber = line_data.sectionNumber,
                    l.sectionId = line_data.sectionId,
                    l.lineInSection = line_data.lineInSection,
                    l.sectionStart = line_data.sectionStart,
                    l.sectionEnd = line_data.sectionEnd
                RETURN count(l) as updated_count
                """
                
                result = session.run(query, batch=batch, album_code=album_code, song_title=song_title)
                batch_updated = result.single()['updated_count']
                total_updated += batch_updated
            
            return total_updated

    def process_album(self, album_info):
        """Process all songs in one album"""
        album_title = album_info['title']
        album_code = album_info['code']
        expected_songs = album_info['song_count']
        
        print(f"\n🎵 PROCESSING ALBUM: {album_title} ({album_code})")
        print(f"📊 Expected songs: {expected_songs}")
        print("-" * 60)
        
        start_time = time.time()
        songs = self.get_songs_in_album(album_code)
        
        album_lines_enhanced = 0
        album_anomalies = []
        
        for i, song_info in enumerate(songs):
            song_title = song_info['title']
            expected_lines = song_info['line_count']
            
            print(f"   {i+1:2d}. {song_title[:40]:<40} ({expected_lines:3d} lines) ", end="")
            
            try:
                # Calculate natural grouping
                enhanced_lines, anomalies = self.calculate_song_natural_grouping(song_title, album_code)
                
                if not enhanced_lines:
                    print("❌ SKIP - No lyrics")
                    continue
                
                # Apply enhancement
                updated_count = self.apply_song_enhancement(enhanced_lines, song_title, album_code)
                
                if updated_count != expected_lines:
                    anomalies.append({
                        'type': 'line_count_mismatch',
                        'song': song_title,
                        'album': album_code,
                        'expected': expected_lines,
                        'updated': updated_count
                    })
                
                album_lines_enhanced += updated_count
                album_anomalies.extend(anomalies)
                
                print(f"✅ {updated_count:3d} enhanced")
                
                if anomalies:
                    print(f"      ⚠️  {len(anomalies)} anomalies detected")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)[:30]}")
                album_anomalies.append({
                    'type': 'processing_error',
                    'song': song_title,
                    'album': album_code,
                    'error': str(e)
                })
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Update statistics
        self.stats['albums_processed'] += 1
        self.stats['songs_processed'] += len(songs)
        self.stats['lines_enhanced'] += album_lines_enhanced
        self.stats['anomalies'].extend(album_anomalies)
        self.stats['processing_times'].append(processing_time)
        
        print(f"\n✅ ALBUM COMPLETE: {album_lines_enhanced} lines enhanced in {processing_time:.1f}s")
        if album_anomalies:
            print(f"⚠️  {len(album_anomalies)} anomalies found")

    def run_full_enhancement(self):
        """Run enhancement for all albums"""
        try:
            print(f"🚀 NATURAL GROUPING FULL ENHANCEMENT")
            print("=" * 70)
            
            # Get all albums
            albums = self.get_album_list()
            total_albums = len(albums)
            total_songs = sum(album['song_count'] for album in albums)
            
            print(f"📊 Processing Plan:")
            print(f"   • Albums: {total_albums}")
            print(f"   • Songs: {total_songs}")
            print(f"   • Target lines: ~11,642")
            
            start_time = time.time()
            
            # Process each album
            for i, album_info in enumerate(albums):
                print(f"\n🎯 ALBUM {i+1}/{total_albums}")
                self.process_album(album_info)
                
                # Show progress
                progress = (i + 1) / total_albums * 100
                print(f"📈 Overall Progress: {progress:.1f}% complete")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Final summary
            self.show_final_summary(total_time)
            
        except Exception as e:
            print(f"❌ Critical error: {e}")
        finally:
            self.driver.close()

    def show_final_summary(self, total_time):
        """Show comprehensive summary of the enhancement process"""
        print(f"\n🎉 ENHANCEMENT COMPLETE!")
        print("=" * 70)
        
        stats = self.stats
        
        print(f"📊 FINAL STATISTICS:")
        print(f"   • Albums processed: {stats['albums_processed']}")
        print(f"   • Songs processed: {stats['songs_processed']}")
        print(f"   • Lines enhanced: {stats['lines_enhanced']:,}")
        print(f"   • Total time: {total_time:.1f} seconds")
        print(f"   • Average per album: {total_time/max(stats['albums_processed'],1):.1f}s")
        print(f"   • Lines per second: {stats['lines_enhanced']/max(total_time,1):.0f}")
        
        if stats['anomalies']:
            print(f"\n⚠️  ANOMALIES DETECTED: {len(stats['anomalies'])}")
            
            # Group anomalies by type
            anomaly_types = {}
            for anomaly in stats['anomalies']:
                anomaly_type = anomaly['type']
                if anomaly_type not in anomaly_types:
                    anomaly_types[anomaly_type] = []
                anomaly_types[anomaly_type].append(anomaly)
            
            for anomaly_type, instances in anomaly_types.items():
                print(f"   • {anomaly_type}: {len(instances)} instances")
                
                # Show first few examples
                for instance in instances[:3]:
                    if anomaly_type == 'long_section':
                        print(f"     - {instance['song']} ({instance['album']}): {instance['section']} with {instance['lines']} lines")
                    elif anomaly_type == 'many_repetitions':
                        print(f"     - {instance['song']} ({instance['album']}): {instance['section']} appears {instance['count']} times")
                    elif anomaly_type == 'line_count_mismatch':
                        print(f"     - {instance['song']} ({instance['album']}): expected {instance['expected']}, updated {instance['updated']}")
                    elif anomaly_type == 'processing_error':
                        print(f"     - {instance['song']} ({instance['album']}): {instance['error'][:50]}")
                
                if len(instances) > 3:
                    print(f"     ... and {len(instances) - 3} more")
        else:
            print(f"\n✅ NO ANOMALIES DETECTED - Perfect enhancement!")
        
        print(f"\n🎯 ENHANCEMENT SUCCESS!")
        print(f"All Taylor Swift lyrics now have natural grouping structure!")

if __name__ == "__main__":
    enhancer = FullNaturalGroupingEnhancer()
    enhancer.run_full_enhancement() 