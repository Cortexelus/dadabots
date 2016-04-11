# dadabots

Soundcloud bots that 
 * spider soundcloud for tracks
 * remix the music, title, and artwork
 * post the remixes 
 * comment on tracks
 * Free account: repeat until account limit is reached
 * Soundcloud Pro: repeat forever, or until temporary bans for too much activity (Avoid more than 50 songs a day)

# See them in action! 

Active
* https://soundcloud.com/autochiptune

Inactive
* https://soundcloud.com/phasedandconfused
* https://soundcloud.com/chopshopshockshack
* https://soundcloud.com/bonafide-slideglide-ride
* https://soundcloud.com/becawwrdsaekva

## Presentations

* [DadaBots: Socially Automated Dadaist Music Remix Bots](https://vimeo.com/72277348)
* [Northeastern ACM Speaker Series: Dadabots &  Computational Creativity](https://www.facebook.com/events/165144357029161/?ref=5)
* [REMIX.ARMY](https://youtu.be/ue_KHvQZH8M)

## In the media

* [Algopop](http://algopop.tumblr.com/post/67950573648/dadabots-socially-automated-dadaist-music-remix)
* [Highway Magazine](http://www.highwaymagazine.info/2015/12/dadabots-music-algorithms/)
* [When Algorithms Create Our Culture](http://www.worldcrunch.com/tech-science/when-algorithms-create-our-culture/c4s19935/)


## dadabots_old/

This directory contains older bots temporarily banished to purgatory. They need to be updated to function with the latest Soundcloud API. 

## How to run AUTOCHIPTUNE bot 

```
git clone https://github.com/Cortexelus/dadabots
pip install soundcloud
```

Install Librosa either `pip install librosa` or from [source](https://github.com/bmcfee/librosa/)

Install [jupyter notebook](http://jupyter.org/)

Run ```jupyter notebook```

Register for the [Soundcloud API](https://developers.soundcloud.com/) and get a secret key. 

Register a [new account](https://soundcloud.com/signup) on soundcloud for your bot. 

Open *Dadabot_Autochiptune.ipynb* in jupyter notebook. 

Search for `client_id` and `client_secret` and update them with your soundcloud API credentials. 

Search for `bot.username` and `bot.password` to your new soundcloud account credentials. 

Execute all the code.

Needs at least one follower in order to start spidering. 

As long as jupyter notebook server is running, the bot will continue to make new tracks. 

If you register for Soundcloud Pro the bot will post new tracks FOREVER


## Making a new bot

Copy *Dadabot_Autochiptune.ipynb* and edit it. 


## Example output 
```
awake.
Autochiptune remix.
hi
Initializing soundcloud.Client . . . 
Searching Check Me Out!'s tracks . . . 
Searching j.j.g.89's tracks . . . 
Searching B Floss's tracks . . . 
Hmm..  Floss  Love Me Or Hate Me (ISDGAF)
url http://soundcloud.com/b-floss-2/floss-love-me-or-hate-me
http://soundcloud.com/b-floss-2/floss-love-me-or-hate-me
gnab download..
opening url http://cf-media.sndcdn.com/ZTcmznvxt383.128.mp3?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNuZGNkbi5jb20vWlRjbXpudnh0MzgzLjEyOC5tcDMiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE0NTI5MTAyMDl9fX1dfQ__&Signature=ilU4KDuu7YCpGlCS7MOp4gC8yF0N9yEeDSO5PmiB-DihRQavkky3TwF48jt9u-zNm2vHpQJNp9fkg6NB6M5IvdFgT9XmeEmvimjhiCf-Jttf92CnqrE5ajPELIoFX39MvwJ4ZM6iDUl2Pmjhw87Cd7u4OdhNbYVnTgzFZNVpF8xFguzh0M2Knbn1JxGiTjCqLZC1jgPUiRwiwed~-lezXd94tgtXSQQBEgAvLT7Ue8ZwswPUFvG5Vk-r1uTHR6MnI4dMFLISXCJSKdj2lnTd-9x-hvL2vDuDgU8VwLeTOpgsFl2XywBcLoo6EPgYUmSyOsWblutbk6JAPtvAp~PRXA__&Key-Pair-Id=APKAJAGZ7VMH2PFPW6UQ


bot.track.artwork_url https://i1.sndcdn.com/artworks-000139724823-vc8lch-large.jpg
artwork_url http://i1.sndcdn.com/artworks-000139724823-vc8lch-large.jpg
gnab download..
opening url http://i1.sndcdn.com/artworks-000139724823-vc8lch-large.jpg


avatar_url http://i1.sndcdn.com/avatars-000157974264-o74oqd-large.jpg
gnab download..
opening url http://i1.sndcdn.com/avatars-000157974264-o74oqd-large.jpg




MP3: ./dadabots/mp3/b-floss-2_floss-love-me-or-hate-me.mp3
TRACK_ART: ./dadabots/art/b-floss-2_floss-love-me-or-hate-me.jpg
USER_ART: ./dadabots/art/b-floss-2.avatar.jpg


Updating avatar..../dadabots/art/b-floss-2.avatar.rmx.autochip.jpg
Remixing track art ./dadabots/art/b-floss-2_floss-love-me-or-hate-me.jpg
Calling autochip(./dadabots/mp3/b-floss-2_floss-love-me-or-hate-me.mp3, ./dadabots/mp3/b-floss-2_floss-love-me-or-hate-me.rmx.autochiptune.mp3)
Processing b-floss-2_floss-love-me-or-hate-me.mp3
Synthesizing squares...
Synthesizing triangles...
Synthesizing drums...
Mixing... 
Done.
Remix title: B Floss: Floss  Love Me Or Hate Me (ISDGAF) [autochip rmx]
Uploading remix . . . 
Remix track art ./dadabots/art/b-floss-2_floss-love-me-or-hate-me.rmx.autochip.jpg
http://soundcloud.com/autochiptune/b-floss-floss-love-me-or-hate
Liking track . . . 
Commenting . . . autochiptune_remix: http://soundcloud.com/autochiptune/b-floss-floss-love-me-or-hate

Commenting . . . Original: http://soundcloud.com/b-floss-2/floss-love-me-or-hate-me

bye
sleeping..
```

## todo 

* Dadabots became a monolithic notebook of code. Separate it back into its reusable pieces, so new bots are easier to make, and old bots are easier to update (whenever soundcloud API changes).

* Store activity in database.

* One follower got annoyed because the bot remixed 5 of his tracks (randomly). Instead remix one track per user until all users have been remixed. 

* Remix tracks which users send bot in a private message. 

* Unfollow users which do not follow back after n days. 



