#!/usr/bin/env python
# encoding: utf=8
"""
offliberty gnabber
downloads tracks from soundcloud, always 128k mp3

cortexel.us 2012
"""
import urllib2, urllib, re

usage = "Offliberty Gnabber. Downloads tracks from soundcloud, youtube, etc.\n\
Usage: offliberty.py url\
Example: offliberty.py http://soundcloud.com/chopshopshockshack/mt-analogue-you-know-what-time"

def geturl(sc_url):
	off_url = "http://offliberty.com/off.php"
	req = urllib2.Request(off_url) 
	#res = urllib2.urlopen(req)
	
	data = { 'track' : sc_url, 'refext' : ""} 
	req.add_data(urllib.urlencode(data))
	res = urllib2.urlopen(req)
	
	offpage = res.read(600)
	
	url_list = re.findall('(?:http://|www.)[^"\' ]+', offpage)
	print url_list[0]
	return url_list[0]

def download(url, file_name):

	u = urllib2.urlopen(url)
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s \nBytes: %s" % (file_name, file_size)

	#if(file_size >= self.MAX_FILE_SIZE):
	#	raise Exception("File size too big!! %i > %i " % [file_size, self.MAX_FILE_SIZE])
		
	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break

		file_size_dl += len(buffer)
		f.write(buffer)
		status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		status = status + chr(8)*(len(status)+1)
		print status,

	print "\n"
	f.close()
	
def gnabsong(url, filename):
	download(geturl(url), filename)
	
if __name__ == '__main__':
    import sys
    try:
        url = sys.argv[1]
        filename = sys.argv[2]
    except:
        print usage
        sys.exit(-1)
    gnabsong(url, filename)
	
