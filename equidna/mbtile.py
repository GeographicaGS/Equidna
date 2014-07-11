# -*- coding: utf-8 -*-
#
# MBTile object. It helps you on creating MBTiles files.
# For more information see MBTiles specifications at https://github.com/mapbox/mbtiles-spec
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

import sqlite3
import hashlib

class MBTile(object):
    """MBTile object t helps you on creating MBTiles files"""

    __filename = None
    """ Database filename"""
    __conn = None
    """Database connection"""

    def __init__(self,filename):
        """Constructor."""
        self.__filename = filename

    def open(self):
        self.__conn = sqlite3.connect(self.__filename,timeout=11)

    def close(self):
        if (not self.__conn):
             raise Exception("No connection open, you must open a connection before call this method")
        # Save (commit) the changes
        self.__conn.commit()
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        self.__conn.close()

    def createStructure(self,createIndexes=True):
        """This method creates the Mbtile's database structure"""

        if (not self.__conn):
             raise Exception("No connection open, you must open a connection before call this method")

        # Create tables
        sql = "CREATE TABLE grid_key (grid_id TEXT,key_name TEXT)"
        self.__conn.execute(sql)

        sql = "CREATE TABLE grid_utfgrid (grid_id TEXT,grid_utfgrid BLOB)"
        self.__conn.execute(sql)

        sql = "CREATE TABLE images (tile_data blob,tile_id text)"
        self.__conn.execute(sql)

        sql = "CREATE TABLE keymap (key_name TEXT,key_json TEXT)"
        self.__conn.execute(sql)

        sql = "CREATE TABLE map (zoom_level INTEGER,tile_column INTEGER,tile_row INTEGER,tile_id TEXT,grid_id TEXT)"
        self.__conn.execute(sql)

        sql = "CREATE TABLE metadata (name text,value text)"
        self.__conn.execute(sql)

        #create views

        sql = "CREATE VIEW grid_data AS \n\
                SELECT \n\
                    map.zoom_level AS zoom_level,\n\
                    map.tile_column AS tile_column,\n\
                    map.tile_row AS tile_row,\n\
                    keymap.key_name AS key_name,\n\
                    keymap.key_json AS key_json\n \
                FROM map \n\
                JOIN grid_key ON map.grid_id = grid_key.grid_id\n\
                JOIN keymap ON grid_key.key_name = keymap.key_name"
        self.__conn.execute(sql)

        sql = "CREATE VIEW grids AS \n\
                    SELECT\n\
                        map.zoom_level AS zoom_level,\n\
                        map.tile_column AS tile_column,\n\
                        map.tile_row AS tile_row,\n\
                        grid_utfgrid.grid_utfgrid AS grid\n\
                    FROM map\n\
                    JOIN grid_utfgrid ON grid_utfgrid.grid_id = map.grid_id"
        self.__conn.execute(sql)

        sql = "CREATE VIEW tiles AS \n\
                SELECT\n\
                    map.zoom_level AS zoom_level,\n\
                    map.tile_column AS tile_column,\n\
                    map.tile_row AS tile_row,\n\
                    images.tile_data AS tile_data\n\
                FROM map\n\
                JOIN images ON images.tile_id = map.tile_id"
        self.__conn.execute(sql)

        if createIndexes:
            self.createIndexes()


    def createIndexes(self):
        """Create db indexes"""

        sql = "CREATE UNIQUE INDEX grid_key_lookup ON grid_key (grid_id, key_name)"
        self.__conn.execute(sql)

        sql = "CREATE UNIQUE INDEX grid_utfgrid_lookup ON grid_utfgrid (grid_id)"
        self.__conn.execute(sql)

        sql = "CREATE UNIQUE INDEX images_id ON images (tile_id)"
        self.__conn.execute(sql)

        sql = "CREATE UNIQUE INDEX keymap_lookup ON keymap (key_name)"
        self.__conn.execute(sql)

        sql = "CREATE UNIQUE INDEX map_index ON map (zoom_level, tile_column, tile_row)"
        self.__conn.execute(sql)

        sql = "CREATE UNIQUE INDEX name ON metadata (name)"
        self.__conn.execute(sql)


    def dropIndexes(self):
        """DROP db indexes"""

        if (not self.__conn):
             raise Exception("No connection open, you must open a connection before call this method")

        sql = "DROP INDEX IF EXISTS grid_key_lookup"
        self.__conn.execute(sql)

        sql = "DROP INDEX IF EXISTS grid_utfgrid_lookup"
        self.__conn.execute(sql)

        sql = "DROP INDEX IF EXISTS images_id"
        self.__conn.execute(sql)

        sql = "DROP INDEX IF EXISTS keymap_lookup"
        self.__conn.execute(sql)

        sql = "DROP INDEX IF EXISTS map_index"
        self.__conn.execute(sql)

        sql = "DROP INDEX IF EXISTS name"
        self.__conn.execute(sql)

    def removeStructure(self):
        """Remove the database structure"""
        if (not self.__conn):
             raise Exception("No connection open, you must open a connection before call this method")
        
        self.__conn.execute("DROP TABLE IF EXISTS grid_key")
        self.__conn.execute("DROP TABLE IF EXISTS grid_utfgrid")
        self.__conn.execute("DROP TABLE IF EXISTS images")
        self.__conn.execute("DROP TABLE IF EXISTS keymap")
        self.__conn.execute("DROP TABLE IF EXISTS map")
        self.__conn.execute("DROP TABLE IF EXISTS metadata")

        self.__conn.execute("DROP VIEW IF EXISTS grid_data")
        self.__conn.execute("DROP VIEW IF EXISTS grids")
        self.__conn.execute("DROP VIEW IF EXISTS tiles")

        self.dropIndexes()

    def commit(self):
        """Perform a commit"""
        if (not self.__conn):
            raise Exception("No connection open, you must open a connection before call this method")


    def addTile(self,zoom,x,y,data):
        """Add a Tile"""
        if (not self.__conn):
            raise Exception("No connection open, you must open a connection before call this method")

        hash = hashlib.md5(data).hexdigest()

        #check if the image already exists
        c = self.__conn.cursor()
        sql = "SELECT EXISTS(SELECT * from images WHERE tile_id=?)"
        c.execute(sql,[hash])

        if not c.fetchone()[0]:
            #images (tile_data blob,tile_id text)
            sql = "INSERT INTO images VALUES (?,?)"
            self.__conn.execute(sql,[buffer(data),hash])

        #map (zoom_level INTEGER,tile_column INTEGER,tile_row INTEGER,tile_id TEXT,grid_id TEXT)
        sql = "INSERT INTO map VALUES (?,?,?,?,NULL)"
        self.__conn.execute(sql,[zoom,x,y,hash])


    def addMetadata(self,dict):
        if (not self.__conn):
            raise Exception("No connection open, you must open a connection before call this method")

        sql = "INSERT INTO metadata VALUES (?,?)";

        for key in dict:
            self.__conn.execute(sql,[key,dict[key]])


    