#!/usr/bin/env python
# encoding: utf=8
"""
dadarays.py

timbrally guided dadaist dissociated array maker
based on dissociated array (adam lindsay) reimagined by Zack Zukowski and CJ Carr

"""
import random
import echonest.audio as audio
from echonest.sorting import *
from echonest.selection import *


import pyechonest.config as config
config.MP3_BITRATE = 192


usage = """
python dadarays.py <input_filename> <output_filename>

Example:
python dadarays.py of_the_sun.mp3 not_of_the_sun.mp3
"""

def strong_meter(choices, song, meter, sections, sl, outchunks):
    #itterate through every section
    for section in sections:
        #store all beats and segments in this section
        beats = song.analysis.beats.that(are_contained_by(section))
        segments = song.analysis.segments.that(overlap(section))
        # store the number of bars in this section
        num_bars = len(section.children())
        #create new arrays for organizing beats and segments
        b = []
        segstarts = []
        #itterate from 0 - the number of beats in a measure
        for m in range(meter):
            #store all beats in this section that fall on the current metrical beat number
            b.append(beats.that(fall_on_the(m+1)))
            #store all segments overlapping start time of the above beats
            segstarts.append(segments.that(overlap_starts_of(b[m])))
        #initiate the current time and stop time
        now = b[0][0]
        end_range = num_bars * meter
        #replace all measures beat by beat
        for x in range(0, end_range + 1):
            #store the current and next location in the meter
            beat = x % meter
            next_beat = (x + 1) % meter
            #store the last segment of this beat
            now_end_segment = segments.that(contain_point(now.end))[0]
            #make a list of beats whos starting timbres best match this ending timbre
            next_candidates = segstarts[next_beat].ordered_by(timbre_distance_from(now_end_segment))
            
            """
            identify the optimum segment variation
            unless now is a transition segment
            transition segments are the first or last beats in a section
            """
            #store how percussive this ending timbre is
            perc_num = ((now_end_segment.timbre[10] + now_end_segment.timbre[6] + now_end_segment.timbre[8] + now_end_segment.timbre[11]) / 4)
            #store how ambient this ending timbre is
            ambi_num = ((now_end_segment.timbre[2] + now_end_segment.timbre[5]) /2)
            # is this the second last beat in the section?
            if x == end_range - 1:
                print "beat number in section"
                print x
                #this is the end so pick the last beat!
                choices = 0
                now = beats[len(beats) - 1]
            #Ambient or Percussive?
            elif ambi_num > perc_num:
                #be smooth
                choices = 0
                x = x + meter
            else:
                if end_range > meter * 6:
                    randoo = random.randrange(0, 3, 1)
                else:
                    randoo = random.randrange(0, 1, 1)
                choices = choices + randoo
            # reduce choices to be within range of next candidates
            while choices >= len(next_candidates) and choices > 0:
                choices -= 1
            #pick the next beat    
            next_choice = next_candidates[choices]
            #store the next beat
            is_next = b[next_beat].that(start_during(next_choice))[0]
            #add the current beat to the remix
            outchunks.append(now)
            #remember the next choosen one...
            now = is_next
        # is this a long or short section (4 bars)
        #randomly choose the timbral dissociation ammount in this section !!!!CJ L00k!!!!
        if end_range > meter * 4:
            rando = random.randrange(2, 6, 1)
        else:
            rando = random.randrange(0, 1, 1)
        choices = rando
    return outchunks
        
def weak_meter(choices, song, sections, sl, outchunks):
    for section in sections:
        i = 0
        # store all the segments in this section
        segments = song.analysis.segments.that(overlap(section))
        # store number of segments
        e = len(segments)
        #only use 1/4 of the length
        e = e / 4
        #initiate the curent segment
        now_segment = segments[0]
        #pick a segment until desired length is rebuilt
        while i < e:
            #add this segment to the remix
            outchunks.append(now_segment)
            #do the following a third of the time
            if random.randrange(0, 2, 1) == 0:
                #pick the next segment
                next_segment = (segments.ordered_by(timbre_distance_from(now_segment))[0])
                #add the segment to the remix
                outchunks.append(next_segment)
                #pick the next next and store it as now
                next_next_segment = (segments.ordered_by(timbre_distance_from(next_segment))[0])
                now_segment = next_next_segment
            #order by similar durations
            time_candidates = song.analysis.segments.ordered_by(duration(now_segment))
            n = 0
            #keep just the first 20 most similar durations
            for segment in time_candidates:
                if n > 20:
                    del segment
                n += 1
            #pick similar timbre out of the 20 segments with similar durations
            timbre_candidates = time_candidates.ordered_by(timbre_distance_from(now_segment))
            #pick one out of the 4 best
            choosen = timbre_candidates[random.randrange(4)]
            #store this choice as the next segment
            now_segment = choosen
            i += 1
    return outchunks

def main(input_filename, output_filename):
    choices = 0
    song = audio.LocalAudioFile(input_filename)
    meter = song.analysis.time_signature.values()[1]
    meter_conf = song.analysis.time_signature.values()[0]
    tempo_conf = song.analysis.tempo.values()[0]
    sections = song.analysis.sections
    last_segment = song.analysis.segments[len(song.analysis.segments) - 1]
    sl = len(sections)
    print "meter confidence"
    print meter_conf
    print "meter"
    print song.analysis.time_signature
    print "number of sections"
    print sl
    outchunks = audio.AudioQuantumList()
    if (meter_conf > 0.2):
        outchunks = strong_meter(choices, song, meter, sections, sl, outchunks)
    else:
        outchunks = weak_meter(choices, song, sections, sl, outchunks)
    outchunks.append(last_segment)
    out = audio.getpieces(song, outchunks)
    out.encode(output_filename)


if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)
