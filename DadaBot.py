#!/usr/bin/env python
# encoding: utf-8

"""
DadaBot.py

Class for soundcloud bots. 

By CJ Carr [cortexel.us]
"""
import soundcloud
import time
import sys
import os.path
import urllib2
import gnabber
import artremixer as artremixer
from random import choice
import random
from random import randint
import pickle
import copy
import subprocess

usage = "Use it correctly, not incorrectly"

class DadaBot:
	 
	def __init__(bot):	
		bot.client = None #  need to call connectSC()
		bot.bot_user = None # need to call connectSC()
		bot.followers = None # list of all followers
		bot.follower = None # follower sc object whose music is remixed

		bot.track = None # track sc object to be remixed
		bot.track_mp3 = "" # file name of downloaded song to be remixed
		bot.track_art = "" # filename of track art downloaded
		bot.user_art = "" # filename of user art downloaded
		
		bot.always_find_new_tracks = True 
		# If True, will not remix a track which has been favorited by the bot
		# If False, all tracks are fair game.
		
		bot.creative_commons_only = True
		# ignores tracks which aren't creative commons

		bot.followerid = 0
		bot.trackid = 0
		bot.remix_trackid = 0
		bot.bot_userid = 0
		
		bot.remix_track = None # track sc of new remix track
		bot.remix_title = "" # title of new remix track
		bot.remix_mp3 = "" # filename of new remix 
		bot.remix_artwork = "" # filename of remixed artwork
		bot.remix_completed = False
		bot.remix_process_call = ""
		
		# DEFAULT info
		bot.username = "becawwrdsaekva"
		bot.password = "fckngtrdtn7.5"
		bot.genre = "[WEEV]"
		bot.tag = "" # for file names example: "song.rmx.weev.mp3"
		
		# unicode("z¬", errors='ignore')# unicode("ž¬", errors='ignore') # unicode("\u0290¬", errors='replace') #"ž¬" #.decode("utf-8", "replace")

		bot.MAX_TRACK_DURATION = 1000 * 60 * 8 # no tracks longer than 8 minutes
		bot.MIN_TRACK_DURATION = 60 * 1000 # minimum 1 minute
		bot.MAX_FILE_SIZE = 10000000
		bot.comments = [
			'hey I really like your track lol!!! Can I remix it? HERE I GO!! %s',
			'o_o i was totally inspired to make a remix. check it out %s',
			'<lol> %s </lol> o.o',
			'for some reason this track reminds me of this track: %s',
			'hey I hope you don\'t mind but I remixed your track: %s',
			'you gave me the best idea: %s',
			'YES! I love this. Is okay if I sample your track? %s'
		] 
	
	def connect(bot, *args):
		if len(args)==2:
			username = args[0]
			password = args[1]
		else:
			username = bot.username
			password = bot.password
		
		# intiialize
		print "Initializing soundcloud.Client . . . "
		bot.client = soundcloud.Client(
			client_id='5bcce9f74d00c0a8d465e7c4c054df78', 
			client_secret='caab92780ed015994bf7bf02c6aa4ed8',
			username=username, 
			password=password)
		bot.bot_user = bot.client.get('/me')
		bot.bot_userid = bot.bot_user.id
		
	def get_followers(bot, user):
		return bot.client.get('/users/%i/followers' % user.id, order='created_at')
		
	# follows all the followers' followers
	def amicabilify(bot, user):
		print "Following all the followers' followers . . . "
		followers = bot.get_followers(user)
		try:
			for follower in followers:
				bot.client.put('/me/followings/%d' % follower.id)
		except:
			print "failed at following the followers' followers"
		return followers
		
	def like_track(bot, track):
		print "Liking track . . . "
		bot.client.put('/me/favorites/%d' % track.id)
			
	# gets the user's list of favorite tracks
	def get_favorites(bot, user):
		return bot.client.get('/users/%i/favorites' % user.id)
		
	# returns true if user has favorited track
	def is_track_favorited(bot, user, track):
		for fav in bot.get_favorites(user):
			if track.id == fav.id:
				return True
		return False
		
	# if bot has remixed this song before, returns false
	# (based on the assumption that the bot liked the track after posting the remix)
	def havent_heard_this_before(bot, track):
		return not bot.is_track_favorited(bot.bot_user, track)
	
	# returns True if track has creative commons license 
	def is_creative_commons(bot, track):
		return track.license[:2] == "cc"
		
	def download_mp3_and_art(bot):
		url = bot.track.permalink_url
		
		p = bot.track.permalink_url.split('/')
		bot.track_mp3  = './mp3/' + p[-2] + "_" + p[-1] + ".mp3"
		bot.remix_mp3 = './mp3/' + p[-2] + "_" + p[-1] + ".rmx." + bot.tag + ".mp3"
		bot.track_art  = './art/' + p[-2] + "_" + p[-1] + ".jpg"
		bot.user_art = './art/' + bot.follower.username + ".avatar.jpg"
		
		try: 
			gnabber.gnabsong(url, bot.track_mp3)
		except:
			print "shit!!!!\n\n"
			return False
		
		if(bot.track.artwork_url):
			try: 
				gnabber.download(bot.track.artwork_url, bot.track_art)
			except:
				print "!! Failed to download trackartwork: " + bot.track.artwork_url
				bot.track_art = ""
		else:
			bot.track_art = ""
			
		if(bot.follower.avatar_url):
			try: 
				gnabber.download(bot.follower.avatar_url,bot.user_art)
			except:
				print "!! Failed to download trackartwork: " + bot.follower.avatar_url
				bot.user_art = ""
		else:
			bot.user_art = ""
			
		print "\n"
		print "MP3: " + bot.track_mp3
		print "TRACK_ART: " + bot.track_art
		print "USER_ART: " + bot.user_art
		return True
	
	def remix(bot):
		# and here is where a large security flaw lays dormant
		print "About to call the following process: " + bot.remix_process_call
		subprocess.call(bot.remix_process_call % (bot.track_mp3, bot.remix_mp3))
		bot.remix_completed = True
	
	# have we completed remixing yet?
	def already_remixed(bot):
		return bot.remix_completed and os.path.isfile(bot.track_mp3)
		
		
	def grab_track(bot, url):
		bot.track = bot.client.get('/resolve',url=url) 
		bot.follower = bot.client.get('/users/'+str(bot.track.user_id))
		if bot.download_mp3_and_art():
		
		
			bot.trackid = bot.track.id
			bot.followerid = bot.follower.id
			return True
		else:
			raise Exception ("BAD URL")
		
	#algorithm for choosing which track to download
	def find_track(bot):
		bot.followers = bot.get_followers(bot.bot_user)
		#bot.followers.reverse()
		track_found = False
		for follower in bot.followers:
			#print "Searching " + follower.username + "'s tracks . . . "
			#order='hotness' #filter='downloadable' #license='
			tracks = bot.client.get('/users/' + str(follower.id) + '/tracks', order='created_at', limit=100)
			tracks = filter(lambda track: 
				((bot.is_creative_commons(track) if bot.creative_commons_only else True) and 
				 (bot.havent_heard_this_before(track) if bot.always_find_new_tracks else True) and
				 track.duration <= bot.MAX_TRACK_DURATION and 
				 track.duration >= bot.MIN_TRACK_DURATION), tracks)
			
			for track in tracks:
				bot.follower = follower
				bot.track = track
				if bot.download_mp3_and_art(): 
					track_found = True
					break
				else:
					sys.stdout.write("Keep searching through " + follower.username + "'s tracks?")
					choice = raw_input().lower()
					if choice=="y" or choice=="yes":
						continue
					else:
						break
				
					
			if track_found:
				break
		
		if not track_found:
			raise Exception( "NO TRACKS!!!!!!!!!!" )
			
		print "\n"
		bot.trackid = bot.track.id
		bot.followerid = bot.follower.id
		
		return True
		

	def dump_intention(bot):
		intention_filename = "./intn/" + bot.track_mp3[6:-4] + "." + bot.tag + ".intention"
		
		# an intention is a copy of the bot object
		# except it does not contain the soundcloud objects (because this causes a stack overflow)
		intention = copy.copy(bot)
		intention.follower = None
		intention.followers = None
		intention.track = None
		intention.remix_track = None
		intention.client = None
		intention.bot_user = None 
		
		file = open(intention_filename, "wb" )
		pickle.dump(intention, file)
		file.close()
		print intention_filename
		return intention_filename
	
	@staticmethod
	def load(intention_filename):
		file = open( intention_filename, "rb" )
		sys.setrecursionlimit(10000)
		bot = pickle.load(file)
		file.close()
		bot.connect(bot.username, bot.password)
		bot.track = bot.client.get('/tracks/'+str(bot.trackid))
		bot.follower = bot.client.get('/users/'+str(bot.track.user_id))
		
		return bot
	
	def post_remix(bot):
		print "Uploading remix . . . "
		if(bot.remix_artwork):
			art_bytes = open(bot.remix_artwork, 'rb')
		else:
			art_bytes = ""
		if not bot.remix_description:
			bot.remix_description = '%s remix of %s' % (bot.tag, bot.track.permalink_url)
		bot.remix_track = bot.client.post('/tracks', track={
			'title': bot.remix_title,
			'asset_data': open(bot.remix_mp3, 'rb'),
			'sharing': 'public',
			'description' : bot.remix_description,
			'genre' : bot.genre,
			'artwork_data' : art_bytes
		})

		# print track link
		print bot.remix_track.permalink_url
		return bot.remix_track

	def update_avatar(bot,image):
		print "Updating avatar..." + image
		user = bot.client.put('/me', user={
			'avatar_data' :open(image, 'rb')
		})
		return user
		
	# returns a comment
	def comment(bot, url):
		comment = choice(bot.comments) % url
		return comment
		
	def main(bot):
		""" THIS IS JUST A DEPRECATED SAMPLEOF POSSIBLE USAGE. 
			See bot_*.py for an example of how DadaBots should actually be used """
	
		print "hi"
		
		#connect to soundcloud API
		bot.connect(bot.username, bot.password)
		
		# grab track from this follower
		# downloads mp3, track art, and user art, and returns filenames
		bot.find_track()
		
		# update bot user art
		if(bot.user_art):
			remix_avatar = artremixer.horzflip(bot, bot.user_art)
			bot.update_avatar(remix_avatar)
		
		# remix track art
		if(bot.track_art):
			bot.remix_artwork = artremixer.art_florp(bot, bot.track_art)
			
		bot.remix_mp3 = bot.track_mp3
		
		# remix title
		bot.remix_title = "%s: %s [%s]" % tuple([bot.follower.username, bot.track.title, bot.tag])
		print "Remix title: "+bot.remix_title
		
		# POST remix
		remix = bot.post_remix()
		
		# follow all the follower's followers
		bot.amicabilify(bot.follower) 
		
		# like track
		bot.like_track(bot.track)
		
		# comment on original track
		comment_string = bot.comment(bot.remix_track.permalink_url)
		print "Commenting . . . " + comment_string + "\n"
		track_comment = bot.client.post('/tracks/%d/comments' % bot.track.id, comment={
			'body': comment_string,
			'timestamp': random.randint(0,bot.track.duration-1)
		})
		
		# comment on remix
		remix_comment_string = "Original: " + bot.track.permalink_url
		print "Commenting . . . " + remix_comment_string + "\n"
		track_comment = bot.client.post('/tracks/%d/comments' % bot.remix_track.id, comment={
			'body': remix_comment_string,
			'timestamp': 100
		})
		
		# delete old mixes
		
		
		print "bye"

if __name__=='__main__':
	tic = time.time()
	bot = DadaBot()	
	bot.main()
	toc = time.time()
	print "Elapsed time: %.3f sec" % float(toc-tic)
