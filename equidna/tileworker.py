import multiprocessing
import time
import mapnik
from mbtile import MBTile
from pngquant.pngquant import tiny

class TileWorkerData(object):
	def __init__(self,tile,imagebuff):
		self.tile = tile
		self.imagebuff = imagebuff

class TileWorker (multiprocessing.Process):

    def __init__(self,i,queue, tiles, map, metadata,compressing=False):
        multiprocessing.Process.__init__(self)
        self.__i = i
        self.__tiles = tiles
        self.__map = map
        self.__md = metadata
        self.__queue = queue
        self.__compressing = compressing

    def run(self):
		
		for t in self.__tiles:

			bounds = t.bounds()
		
			extent = mapnik.Box2d(bounds.xmin,bounds.ymin,bounds.xmax,bounds.ymax)
			self.__map.zoom_to_box(extent)

			image = mapnik.Image(self.__map.width,self.__map.height)
			mapnik.render(self.__map, image)
			imagebuff = image.tostring(self.__md["format"])

			if self.__compressing:
				imagebuff = tiny(imagebuff, self.__map.width,self.__map.height)

			self.__queue.put(TileWorkerData(t,imagebuff))
		


		