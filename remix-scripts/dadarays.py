#!/usr/bin/env python
# encoding: utf=8
"""
dadarays.py

timbrally guided dadaist dissociated array maker on the bot beat and tatum level
based on dissociated array (adam lindsay) mod by Zack Zukowski and CJ Carr

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
    for section in sections:
        beats = song.analysis.beats.that(are_contained_by(section))
        segments = song.analysis.segments.that(overlap(section))
        num_bars = len(section.children())
        b = []
        segstarts = []
        for m in range(meter):
            b.append(beats.that(fall_on_the(m+1)))
            segstarts.append(segments.that(overlap_starts_of(b[m])))
        now = b[0][0]
        end_range = num_bars * meter
        
        for x in range(0, end_range):
            if x == 5:
                beat = 1
            else:
                beat = x % meter
            next_beat = (x + 1) % meter
            now_end_segment = segments.that(contain_point(now.end))[0]
            next_candidates = segstarts[next_beat].ordered_by(timbre_distance_from(now_end_segment))
            if len(next_candidates) == 0:
                next_candidates = segstarts[next_beat]
                                                      
            """
            identify the optimum segment varriation
            unless now is a transition segment
            transition segments are the first or last in a section
            """
            perc_num = ((now_end_segment.timbre[10] + now_end_segment.timbre[6] + now_end_segment.timbre[8] + now_end_segment.timbre[11]) / 4)
            ambi_num = ((now_end_segment.timbre[2] + now_end_segment.timbre[5]) /2)

            if x == end_range - 1 or x == 0:
                next_choice = next_candidates[0]
            elif ambi_num > perc_num:
                choices = 1
                while choices > len(next_candidates) and choices > 0:
                    choices -= 1
                    print next_candidates
                next_choice = next_candidates[choices]
            else:
                if sl > 6:
                    randoo = random.randrange(0, 2, 1)
                else:
                    randoo = random.randrange(0, 1, 1)
                choices = choices + randoo
                # normalize choices to be with in range of next candidates
                while choices > len(next_candidates) and choices > 0:
                    choices -= 1
                if choices == 0:
                    next_choice = next_candidates[0]
                else:
                    next_choice = next_candidates[random.randrange(0, choices, 1)]
            is_next = b[next_beat].that(start_during(next_choice))[0]
            outchunks.append(now)
            now = is_next
            
        if sl > 12:
            rando = random.randrange(1, 4, 1)
        else:
            rando = random.randrange(2, 3, 1)
        choices = rando
    return outchunks
        
def weak_meter(choices, song, sections, sl, outchunks):
    for section in sections:
        i = 0
        segments = song.analysis.segments.that(overlap(section))
        e = len(segments)
        if e > 0:
            e = e / 4
        now_segment = segments[0]
        while i < e:
            outchunks.append(now_segment)
            if random.randrange(0, 2, 1) == 0:
                next_segment = (segments.ordered_by(timbre_distance_from(now_segment))[0])
                outchunks.append(next_segment)
                next_next_segment = (segments.ordered_by(timbre_distance_from(next_segment))[0])
                now_segment = next_next_segment
            nso_duration = now_segment.duration
            time_candidates = song.analysis.segments.ordered_by(duration)
            n = 0
            for segment in time_candidates:
                if n > 20:
                    del segment
                n += 1
            timbre_candidates = time_candidates.ordered_by(timbre_distance_from(now_segment))
            choosen = timbre_candidates[random.randrange(4)]
            now_segment = choosen
            i += 1
    return outchunks

def main(input_filename, output_filename):
    choices = 0
    song = audio.LocalAudioFile(input_filename)
    meter = song.analysis.time_signature.values()[1]
    meter_conf = song.analysis.time_signature.values()[0]
    tempo_conf = song.analysis.tempo.values()[0]
    print meter_conf
    sections = song.analysis.sections
    sl = len(sections)
    print "number of sections"
    print sl
    outchunks = audio.AudioQuantumList()
    if (meter_conf > 0.4):
        outchunks = strong_meter(choices, song, meter, sections, sl, outchunks)
    else:
        outchunks = weak_meter(choices, song, sections, sl, outchunks)
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
