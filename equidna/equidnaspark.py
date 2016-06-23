# -*- coding: utf-8 -*-
#
# Equidna is a Tile builder which is based on Mapnik.
# For more information see Mapnik project at https://github.com/mapnik/mapnik or http://mapnik.org/
# Copyright (C) 2014  Geographica
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

from __future__ import print_function

import mapnik,os,sys
import math
import time
import hashlib
import mapnik

from tms import Tile,Grid,Coordinate,Bbox
from pyspark import SparkContext
import logging
logger = logging.getLogger('py4j')


from boto.s3.connection import S3Connection
from boto.s3.key import Key
from config import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_BUCKET

def rendertile(x):

  logger.info("My test info statement")
  z,x,y = x
  # basepath = '/Users/alasarr/dev/Equidna/equidna/output'
  # basefolder = os.path.join(basepath,'%d/%d' % (z,x))
  # if not os.path.exists(basefolder):
  #   os.makedirs(basefolder)
  # fname = os.path.join(basefolder,'%d.png' % (y))

  m = mapnik.Map(256,256)
  m.buffer_size = 128
  # # Load Mapnik stylesheet
  mapnik.load_map(m, '/root/equidna/mapnik.xml')

  t = Tile(z,x,y)
  bounds = t.bounds()

  extent = mapnik.Box2d(bounds.xmin,bounds.ymin,bounds.xmax,bounds.ymax)
  m.zoom_to_box(extent)

  image = mapnik.Image(256,256)
  mapnik.render(m, image)
  imagebuff = image.tostring('png')

  s3conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  s3bucket = s3conn.get_bucket(AWS_BUCKET, validate=False)

  k = Key(s3bucket)
  k.key = '%d/%d/%d.png' % (z,x,y)
  k.set_contents_from_string(imagebuff)

  #conn = psycopg2.connect('host=192.168.99.100 dbname=tiles user=postgres password=postgres')
  # conn = psycopg2.connect('host=54.86.27.234 dbname=tiles user=postgres password=spark')
  #
  # cur = conn.cursor()
  #
  # cur.execute('INSERT INTO tiles VALUES (%d,%d,%d, %s)' % (z,x,y,psycopg2.Binary(imagebuff)))
  # conn.commit()
  # cur.close()
  # conn.close()


class EquidnaSpark(object):
  """Equidna is a Tile builder which is based on Mapnik"""
  __xml = None
  """ Mapnik xml"""
  __md = None
  """Metadata"""
  __appName = None
  """Spark App Name"""

  def __init__(self,mapnikxml,metadata,appName):
    """Constructor.
      Keyword arguments:
      mapnikxml -- String - Path to Mapnik XML file
      metadata -- Dictionary metadata
    """
    self.__xml = mapnikxml
    self.__md = metadata
    self.__appName = appName

  def __getTiles(self):

    grid = Grid()
    boundsarray = self.__md["bounds"].split(",")
    lowerleft = Coordinate("4326",boundsarray[0],boundsarray[1]).wgs84LatLonToSphericalMercator()
    upperright = Coordinate("4326",boundsarray[2],boundsarray[3]).wgs84LatLonToSphericalMercator()
    bounds_3857 = Bbox(lowerleft.x,lowerleft.y,upperright.x,upperright.y)

    allTiles = []

    for zoom in range(self.__md["minzoom"],self.__md["maxzoom"]+1):
      for g in grid.getTilesInBounds(zoom,bounds_3857):
        allTiles.append((g.zoom,g.x,g.y))

    return allTiles

  def build(self):
    start_time = time.time()

    sc = SparkContext(appName=self.__appName)

    cores_per_slave = 4
    n_slaves  = 4
    tiles = self.__getTiles()

    tiles = sc.parallelize(tiles,cores_per_slave*n_slaves).map(rendertile)

    print(tiles.count())

    sc.stop()
