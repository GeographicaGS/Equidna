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

from pngquant.pngquant import tiny

COMPRESSING = True

class Equidna(object):
    """Equidna is a Tile builder which is based on Mapnik"""
    __xml = None
    """ Mapnik xml"""
    __md = None
    """Metadata"""

    def __init__(self,mapnikxml,metadata,ncores=None,debug=1):
        """Constructor.
          Keyword arguments:
            mapnikxml -- String - Path to Mapnik XML file
            metadata -- Dictionary - MBTiles metadata
            ncores -- Int - Number of cores to use. Use None for get all cores
        """
        self.__xml = mapnikxml
        self.__md = metadata
        self.__ncores = ncores
        self.__debug = debug

    def __timeString(self,elapsed_time):
    
        if elapsed_time >= 60*60:
            hours = int(elapsed_time/(60*60))
            minutes = int((elapsed_time%(60*60)) / 60) 
            seconds = (elapsed_time%(60*60))%60
            return str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
        elif elapsed_time >= 60:
            minutes = int(elapsed_time/60) 
            seconds = elapsed_time%60
            return str(minutes) + "m " + str(seconds) + "s"
        else:
            return str(elapsed_time) + "s"    

    def build(self,output,format):
        start_time = time.time()
    
        if format == "mbtiles": 
            self.__buildMBTiles(output)

        elapsed_time = self.__timeString(time.time() - start_time)

        if self.__debug>0:
            print "Elapsed time: %s seconds " % (elapsed_time)

    def mapper(self,tiles,nworkers):
        mapper_tiles = []

        interval = int(math.ceil(len(tiles)/float(nworkers)))

        for i in range(0,nworkers):
            loweridx = i*interval
            upperidx = (i+1)*interval
            mapper_tiles.append(tiles[loweridx:upperidx])

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
        ncores =  multiprocessing.cpu_count() if self.__ncores == None or multiprocessing.cpu_count() < self.__ncores  else self.__ncores

        nworkers = ncores

        if ncores == 1:
            for t in allTiles:

                bounds = t.bounds()
        
                extent = mapnik.Box2d(bounds.xmin,bounds.ymin,bounds.xmax,bounds.ymax)
                m.zoom_to_box(extent)

                image = mapnik.Image(m.width,m.height)
                mapnik.render(m, image)
                imagebuff = image.tostring(self.__md["format"])

                if COMPRESSING:
                    imagebuff = tiny(imagebuff, m.width,m.height)

                mb.addTile(t.zoom,t.x,t.y,imagebuff)

        else:

            mapTiles = self.mapper(allTiles,nworkers)

            lock = multiprocessing.Lock()
            queue = multiprocessing.JoinableQueue()

            n = 0
            for i in range(0,nworkers):
                n = n+len(mapTiles[i])
                worker = TileWorker(i,queue,mapTiles[i],m,self.__md, COMPRESSING)
                # Start a new worker
                worker.start()
                # Add a worker to the list
                workers.append(worker)
            
            for i in range(0,n):
                tileWorkerData = queue.get()
                print i*100/n,"%         \r",
                mb.addTile(tileWorkerData.tile.zoom,tileWorkerData.tile.x,tileWorkerData.tile.y,tileWorkerData.imagebuff)           

            # Wait for all worker to complete
            for t in workers:
                t.join()
        
        # Let's create the indexes
        mb.createIndexes()
        mb.close()