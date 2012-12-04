

import DadaBot
from DadaBot import DadaBot
import artremixer
import random 
import os
import sys


usage = ("\nDadaBots this_bot usage:\n"
		 "*****************************************************************\n"
		 "| python this_bot.py [url|file.intention] [remix] [post] [clean]\n"
		 "*****************************************************************\n"
		 "| Given a soundcloud track url it will download it and make a .intention file\n"
		 "| Given a .intention file it will load the previously incomplete remix session\n"
		 "| Given neither, it will find a new track on soundcloud from its followers\n"
		 "|\n"
		 "| The remix flag will remix the track and create a .rmx.mp3 file\n"
		 "| The post flag will post the track to soundcloud.\n"
		 "| The clean flag will delete the intention file after it's done.\n"
		 "|\n"
		 "| Examples:\n"
		 "| * Totally automated bot from start to finish:\n"
		 "|   python this_bot.py remix post \n"
		 "|\n"
		 "| * Grab track at URL and remix it, but don't post it yet:\n"
		 "|   python this_bot.py http://soundcloud.com/dadabots/some-song remix\n"
		 "|\n"
		 "| * Repost an old remix, then delete the intention: \n"
		 "|   python this_bot.py ./intn/newatthetime.intention post clean\n"
		 "|\n"
		 "| Makes sense yet?\n"
		 )
"""
	The .intention files are there so you can divvy download/remix/upload tasks. 
	Also this helps make bot activity scalable.
	It doesn't require any computing power to download/upload.
	It doesn't require any internet bandwidth to remix.
	In a large bot ecosystem, these tasks should be threaded, and cloudified. 
"""

bot = None
def grabsong(url):
	global bot
	bot = DadaBot()
	bot.connect("chopshopshockshack", "fckngtrdtn7.5")
	
	bot.remix_process_call = "python remix-scripts/dadarays.py %s %s" 
	bot.tag = "(@)"
	
	if url=="":
		bot.always_find_new_tracks = True # will not remix the same song twice
		bot.creative_commons_only = True # only remixes creative commons tracks
		bot.find_track()
	else:
		bot.grab_track(url)
		
	
	return bot.dump_intention() 
	
def remixsong(remixintention):
	global bot
	# load bot, reconnect to soundcloud, but only if we haven't already connected
	bot = DadaBot.load(remixintention) if not bot else bot 

	if bot.already_remixed():
		print "This song has already been remixed"
		return remixintention
	
	###
	# Do it! remix() runs a subprocess (probably an EchoNest python script), 
	# it assumes the original mp3 is located at bot.track_mp3
	# it outputs the remixed mp3 to the location specified at: bot.remix_mp3
	bot.remix()
	
	return bot.dump_intention() 
	
def postsong(postintention):
	global bot
	# load bot, reconnect to soundcloud, but only if we haven't already connected

	bot = DadaBot.load(postintention) if not bot else bot 	

	if not bot.already_remixed():
		print usage
		raise Exception("Sorry I can't post this song, it doesn't appear to be remixed")
	
	###
	# Here is all the social activity of the bot:
	### 
	
	# update bot user art
	if(bot.user_art):
		remix_avatar = artremixer.octoflip(bot, bot.user_art)
		bot.update_avatar(remix_avatar)
	
	# remix track art
	if(bot.track_art):
		bot.remix_artwork = artremixer.art_florp(bot, bot.track_art)
	
	# remix title
	bot.remix_title = "%s - %s RMX (@)" % (bot.follower.username, bot.track.title)
				
	bot.genre = "@"
	bot.remix_description = ""
	
	# POST remix
	remix = bot.post_remix()
	
	# follow all the follower's followers
	bot.amicabilify(bot.follower) 
	
	# like original track (this marks the track so that bot doesn't remix it twice)
	bot.like_track(bot.track)
	
	
	# edit comments here
	# %s is where remix url goes. 
	bot.comments = [
		"Ideas are kinky and what matters is a fun, but your swag is the acquisition of culture. %s",
		"If nothing is boring after two minutes? Try it four. Then Sixteen. You discover that nothing is eventually boring after all. %s",
		"I can understand why people are so frightened of new music for i'm frightened of old music. %s",
		"I knowww this is poetry! %s",
		"Killer drop. We need to annoy the past or it will not be gone. %s",
		"i like to discover for no reason.  %s",
		"you enable me to fly. %s",
		"When you separated music from life we got art. %s",
		"You carry your home on your back? %s",
		"Those four sounds are good! %s",
		"Let's mingle or swap genes? %s"
	]


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
	
	
	


if __name__ == '__main__':
	import sys
	
	if len(sys.argv)<=1:
		intention = grabsong("") # if given no input, grabs a new song from soundcloud followers
	elif "help" in sys.argv:
		print usage
		sys.exit()
	elif sys.argv[1][:4] == "http":
		intention = grabsong(sys.argv[1]) # if given an url, grabs that song
	elif sys.argv[1][-10:] == ".intention":
		intention = sys.argv[1] # loads previously incomplete bot intention
		if(len(sys.argv)<=2): 
			print usage
			print "Warning: intentions must be accompanied with a post or remix flag"
			sys.exit()
	else:
		intention = grabsong("") # if not given url/file, grabs a new song from soundcloud followers

	if "remix" in sys.argv:
		intention = remixsong(intention) # if remix flag is set, remix the song!
	if "post" in sys.argv:
		intention = postsong(intention) # will throw exception if you try to post a song which hasn't been remixed
	
	if "clean" in sys.argv:
		if intention and os.path.exists(intention):
			os.remove(intention)
			print "Deleted " + intention
		else:
			print "Warning, no valid intention file given: " + str(intention)
		

