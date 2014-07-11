import multiprocessing
import time
import mapnik
from mbtile import MBTile


class TileWorkerData(object):
	def __init__(self,tile,imagebuff):
		self.tile = tile
		self.imagebuff = imagebuff

class TileWorker (multiprocessing.Process):

    def __init__(self,i,lock,queue, tiles, mbtilespath, map, metadata):
        multiprocessing.Process.__init__(self)
        self.__i = i
        self.__lock = lock
        self.__tiles = tiles
        self.__map = map
        self.__md = metadata
        self.__mbtiles = MBTile(mbtilespath)
        self.__queue = queue

    def run(self):
		
		#self.__mbtiles.open()
		
		for t in self.__tiles:

			bounds = t.bounds()
		
			extent = mapnik.Box2d(bounds.xmin,bounds.ymin,bounds.xmax,bounds.ymax)
			self.__map.zoom_to_box(extent)

			image = mapnik.Image(self.__map.width,self.__map.height)
			mapnik.render(self.__map, image)
			imagebuff = image.tostring(self.__md["format"])

			#self.__lock.acquire()

			self.__queue.put(TileWorkerData(t,imagebuff))

			# Really bad to open an close connection each time but neested for multithreading support.
			# That will be fixed when moves to MongoDB
			
			#self.__mbtiles.addTile(t.zoom,t.x,t.y,image_buff)			
			#self.__mbtiles.commit()

			#self.__lock.release()

		#self.__mbtiles.close()
		


		