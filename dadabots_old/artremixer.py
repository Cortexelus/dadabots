from PIL import Image
import PIL.ImageOps
import PIL.ImageFilter as ImageFilter
import ImageChops

# takes art, finds edges, creates horz and vert symmetry
def art_florp(bot,track_art):
	image = Image.open(track_art)
	image = image.filter(ImageFilter.FIND_EDGES)
	image = Image.blend(Image.blend(image, image.rotate(90), 0.5), Image.blend(image.rotate(180), image.rotate(270), 0.5), 0.5)
	new_track_art = track_art[:-3] + "rmx.florp." + track_art[-3:]
	image.save(new_track_art) 
	return new_track_art

# simple horz flip, kinda dumb
def horzflip(bot,art):
	image = Image.open(art)
	image = Image.blend(image, image.rotate(180), 0.5)
	new_art = art[:-3] + "rmx.horzflip." + art[-3:]
	image.save(new_art)
	return new_art
	
#octogon flip
def octoflip(bot,art):
	image = Image.open(art)
	image = Image.blend(Image.blend(image, image.rotate(90), 0.5), Image.blend(image.rotate(180), image.rotate(270), 0.5), 0.5)
	image = Image.blend(image, image.rotate(45), 0.5)
	image = image.filter(ImageFilter.SHARPEN)
	image = image.filter(ImageFilter.SHARPEN)
	new_art = art[:-3] + "rmx.octo." + art[-3:]
	image.save(new_art)
	return new_art