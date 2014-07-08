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

class Equidna(object):
    """Equidna is a Tile builder which is based on Mapnik"""
    __xml = None
    """ Mapnik xml"""
    __md = None
    """Metadata"""

    def __init__(self,mapnikxml,metadata):
        """Constructor."""
        self.__xml = mapnikxml;
        self.__md = metadata;

    def build(self,output,format):
    	if format == "mbtiles":
    		self.__buildMBTiles(output)

    def __buildMBTiles(self,output):
    	# Create mapnik map
		m = mapnik.Map(256,256)
		# Load Mapnik stylesheet
		mapnik.load_map(m, self.__xml)

		# Create MBTiles object
		mb = MBTile(output)

		mb.open()
		mb.removeStructure()
		# # Create the structure whitout indexes, just for a faster insertion
		mb.createStructure(createIndexes=False)

		# # Add metadata
		mb.addMetadata(self.__md)

		#bbox = Bbox(self.__md["bounds"][0],self.__md["bounds"][1])
		boundsarray = self.__md["bounds"].split(",")
		lowerleft = Coordinate("4326",boundsarray[0],boundsarray[1]).wgs84LatLonToSphericalMercator()
		upperright = Coordinate("4326",boundsarray[2],boundsarray[3]).wgs84LatLonToSphericalMercator()
		bounds_3857 = Bbox(lowerleft.x,lowerleft.y,upperright.x,upperright.y)

		grid = Grid()
		for zoom in range(self.__md["minzoom"],self.__md["maxzoom"]+1):
			print "Building zoom %d..." % (zoom), 
			tiles = grid.getTilesInBounds(zoom,bounds_3857)

			for t in tiles:
				bounds = t.bounds()
				extent = mapnik.Box2d(bounds.xmin,bounds.ymin,bounds.xmax,bounds.ymax)
				m.zoom_to_box(extent)

				image = mapnik.Image(m.width,m.height)
				mapnik.render(m, image)
				image_buff = image.tostring(self.__md["format"])

				mb.addTile(zoom,t.x,t.y,image_buff)

			print "COMPLETED"

		# # Let's create the indexes
		mb.createIndexes()
		mb.close()