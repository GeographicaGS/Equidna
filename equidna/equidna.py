# -*- coding: utf-8 -*-
#
# Equidna is a Tile builder which is based on Mapnik.
# For more information see Mapnik project at https://github.com/mapnik/mapnik or http://mapnik.org/
# Copyright (C) 2014  Geographica (Geografía Aplicada SL)
# Author: Alberto Asuero

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import mapnik,os
from mbtile import MBTile
from tms import Tile,Grid,Coordinate,Bbox
from tileworker import TileWorker
import math
import time
import multiprocessing

class Equidna(object):
    """Equidna is a Tile builder which is based on Mapnik"""
    __xml = None
    """ Mapnik xml"""
    __md = None
    """Metadata"""

    def __init__(self,mapnikxml,metadata,ncores=None):
        """Constructor."""
        self.__xml = mapnikxml
        self.__md = metadata
        self.__ncores = ncores

    def build(self,output,format):
		start_time = time.time()
	
		if format == "mbtiles":	
			self.__buildMBTiles(output)
		
		print "--- %f seconds ---" % (time.time() - start_time)

    def mapper(self,tiles,nworkers):
    	mapper_tiles = []
    	pos = 0
    	interval = int(math.floor(len(tiles)/nworkers))

    	while ( pos+interval<=len(tiles)):
    		
    		max = pos+interval
    		if max > len(tiles):
    			max = len(tiles) -1
    		mapper_tiles.append(tiles[pos:max])
    		pos = pos + interval

    	return mapper_tiles


    def __buildMBTiles(self,output):
    	# Create mapnik map
		m = mapnik.Map(256,256)
		m.buffer_size = 128
		# Load Mapnik stylesheet
		mapnik.load_map(m, self.__xml)

		# Create MBTiles object
		mb = MBTile(output)

		mb.open()
		mb.removeStructure()
		# # Create the structure whitout indexes, just for a faster insertion
		mb.createStructure(createIndexes=False)

		# Add metadata
		mb.addMetadata(self.__md)

		mb.close()

		boundsarray = self.__md["bounds"].split(",")
		lowerleft = Coordinate("4326",boundsarray[0],boundsarray[1]).wgs84LatLonToSphericalMercator()
		upperright = Coordinate("4326",boundsarray[2],boundsarray[3]).wgs84LatLonToSphericalMercator()
		bounds_3857 = Bbox(lowerleft.x,lowerleft.y,upperright.x,upperright.y)

		grid = Grid()

		allTiles = []

		for zoom in range(self.__md["minzoom"],self.__md["maxzoom"]+1):
			allTiles.extend(grid.getTilesInBounds(zoom,bounds_3857))

		workers = []

		# Number of cores
		ncores =  multiprocessing.cpu_count() if self.__ncores == None else self.__ncores

		nworkers = ncores

		mapTiles = self.mapper(allTiles,nworkers)

		lock = multiprocessing.Lock()

		for i in range(0,nworkers):
			worker = TileWorker(i,lock,mapTiles[i],output,m,self.__md)
			# Start a new worker
			worker.start()
			# Add a worker to the list
			workers.append(worker)

		# Wait for all worker to complete
		for t in workers:
		    t.join()

		print "COMPLETED"
		
		# # Let's create the indexes
		mb.open()
		mb.createIndexes()
		mb.close()