# coding=UTF8

"""

This is the TMS library.

Only accepts coordinates in WGS84 or Spherical Mercator. Do not attempt
to do anything with other coordinate systems.

"""

import math

srid = {
    4326: "EPSG:4326 WGS84 Geographics",
    3857: "EPSG:3857 Google Mercator"
}

tileSize = 256.0
"""Size of the tiles."""
originShift = math.pi*6378137.0
initialResolution = 2*math.pi*6378137.0/tileSize

class Coordinate(object):
    """Coordinate class. This object holds x,y coordinates in the given SRID."""
    srid = None
    """The Spatial Reference ID of the coordinate (3857 for Spherical Mercator, 4326 for WGS84 Geographics)."""
    x = None
    """x coordinate."""
    y = None
    """y coordinate."""

    def __init__(self, srid, x, y):
        """Constructor."""
        self.srid = srid
        self.x = x
        self.y = y

    def wgs84LatLonToSphericalMercator(self):
        """Converts from WGS84 Lat/Lon to Spherical Mercator."""
        if self.srid==3857:
            return(self)
        else:
            x = self.x*originShift/180.0
            y = math.log(math.tan((90.0+self.y)*math.pi/360.0)) / (math.pi/180.0)*originShift/180.0
            return(Coordinate(3857,x,y))

    def sphericalMercatorToWgs84LatLon(self):
        """Converts from Spherical Mercator to WGS84 Lat/Lon."""
        if self.srid==4326:
            return(self)
        else:
            lon = self.x/originShift*180.0
            lat = 180.0/math.pi*(2*math.atan(math.exp((self.y/originShift*180.0)*math.pi/180.0))-math.pi/2.0)
            return(Coordinate(4326,lon,lat))

    def __str__(self):
        """To string."""
        return("(EPSG:"+str(self.srid)+" "+str(self.x)+" "+str(self.y)+")")


class Tile(object):
    """Tile class in a TMS schema."""
    zoom = None
    """Tile zoom level."""
    x = None
    """Tile's x coordinate."""
    y = None
    """Tile's y coordinate."""

    def __init__(self, zoom, x, y):
        """Constructor."""
        self.zoom = zoom
        self.x = x
        self.y = y

    def __str__(self):
        """To string."""
        return("("+self.zoom+" "+self.x+" "+self.y+")")

    def pixelResolution(self):
        """Returns the resolution of a pixel in the given zoom."""
        return(initialResolution/math.pow(2.0,self.zoom))

    def length(self):
        """Returns the length of the side of the tile, in meters."""
        return(2*math.pi*6378137/pow(2, self.zoom))

    def toGoogle(self):
        """Returns the equivalent Google tile position."""
        return(Tile(self.zoom, self.x, pow(2, self.zoom-1)-self.y))

    def childTiles(self, zoom):
        """Returns child tiles in a given zoom."""
        tiles = []
        if self.zoom>zoom:
            return(None)

        grid = Grid()
        s = grid.size(zoom-self.zoom)
        for a in range(self.x*s, (self.x*s)+s-1):
            for b in range (self.y*s, (self.y*s)+s-1):
                tiles.append(zoom, a, b)

        return(tiles)

    def bounds(self):
        """Returns tile bounds in 3857."""
        length = self.length()
        minxy = Coordinate(3857, (self.x*length)-originShift, (self.y*length)-originShift)
        maxxy = Coordinate(3857, (self.x*length)+length-originShift, (self.y*length)+length-originShift)
        return(Bbox(minxy.x, minxy.y, maxxy.x, maxxy.y))


class PixelGrid(object):
    """A pixel referenced to the grid."""
    zoom = None
    """Zoom this pixel belongs to."""
    x = None
    """x coordinate."""
    y = None
    """y coordinate."""

    def __init__(self, zoom, x, y):
        """Constructor."""
        self.zoom = int(zoom)
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        """To string."""
        return("("+str(self.zoom)+" "+str(self.x)+" "+str(self.y)+")")

    def bottomLeft(self):
        """Returns bottom left corner of the pixel in 3857."""
        x = (self.x*self.pixelResolution())-originShift
        y = (self.y*self.pixelResolution())-originShift
        return(Coordinate(3857, x, y))

    def topRight(self):
        """Returns the top right corner of the pixel in 3857."""
        x = (self.x*self.pixelResolution())+self.pixelResolution()-originShift
        y = (self.y*self.pixelResolution())+self.pixelResolution()-originShift
        return(Coordinate(3857, x, y))

    def bbox(self):
        """Returns the bounding box delimited by the pixel in 3857."""
        origin = self.bottomLeft()
        corner = self.topRight()
        return(Bbox(origin.x, origin.y, corner.x, corner.y))

    def center(self):
        """Returns the center of the pixel in 3857."""
        origin = self.bottomLeft()
        x = origin.x+(self.pixelResolution()/2.0)
        y = origin.y+(self.pixelResolution()/2.0)
        return(Coordinate(3857, x, y))

    def pixelResolution(self):
        """Returns the resolution of a pixel for a given zoom level."""
        return(initialResolution/math.pow(2.0,self.zoom))

    def invertOrigin(self):
        """Inverts the origin of the grid for the pixel, from bottom left to top left."""
        mapsize = pow(2,self.zoom)*tileSize
        return PixelGrid(self.zoom, self.x, mapsize-self.y-1)

    def toPixelTile(self, tile):
        """Returns a PixelTile for a given tile."""
        x = self.x-(tile.x*tileSize)
        y = self.y-(tile.y*tileSize)
        x = 255 if x>255 else x
        y = 255 if y>255 else y
        x = 0 if x<0 else x
        y = 0 if y<0 else y
        return(PixelTile(tile,x,y))


class Grid(object):
    """Tile grid object."""
    def __init__(self):
        """Constructor."""

    def sphericalMercatorToGridPixels(self, coordinate, zoom):
        """Given a coordinate in 3857, returns a PixelGrid for the given zoom."""
        res = self.pixelResolution(zoom)
        x = math.floor((coordinate.x+originShift/res))
        y = math.floor((coordinate.y+originShift/res))
        return(PixelGrid(zoom, x, y))

    def pixelResolution(self, zoom):
        """Returns the resolution of a pixel in the given zoom."""
        return(initialResolution/math.pow(2.0, zoom))

    def sphericalMercatorInTile(self, coordinate, zoom):
        """Returns the tile this coordinate falls in for a given zoom level."""
        tile = Tile(zoom, 0, 0)
        tile.x = math.floor((coordinate.x+originShift)/tile.length())
        tile.y = math.floor((coordinate.y+originShift)/tile.length())
        return(tile)

    def size(self, zoom):
        """Returns the grid size in tiles for a given zoom."""
        return(pow(2, zoom))

    def getTiles(self, zoom):
        """Returns all tiles in a zoom."""
        tiles = []
        for a in range(0, self.size(zoom)):
            for b in range(0, self.size(zoom)):
                tiles.append(Tile(zoom, a, b))
        return(tiles)
        
    def zoomForPixelSize(self, size):
        """Returns the maximum zoom at which the given pixel size is guaranteed."""
        for i in range(0, 30):
            if size>self.pixelResolution(i):
                if i==0:
                    return(0)
                else:
                    return(i-1)

    def pixelTileFromCoordinate(self, coordinate, zoom):
        """This is a convenience function that takes a coordinate in 3857 or 4326 and a zoom level
        and returns a PixelTile."""
        c = coordinate.wgs84LatLonToSphericalMercator() if coordinate.srid==4326 else coordinate
        g = Grid()
        pgrid = g.sphericalMercatorToGridPixels(c, zoom)
        tile = g.sphericalMercatorInTile(c, zoom)
        return(pgrid.toPixelTile(tile))


class Bbox(object):
    """A bounding box."""
    xmin = None
    ymin = None
    xmax = None
    ymax = None

    def __init__(self, xmin, ymin, xmax, ymax):
        """Constructor."""
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def __str__(self):
        """To string."""
        return(str(self.bbox))

        
class PixelTile(object):
    """A pixel referenced to a tile."""
    tile = None
    x = None
    y = None

    def __init__(self, tile, x, y):
        """Constructor."""
        self.tile = tile
        self.x = x
        self.y = y

    def __str__(self):
        """To string."""
        return(str(self.tile)+" "+str(self.x)+" "+str(self.y))

    def toPixelGrid(self):
        """Returns the PixelGrid of this PixelTile."""
        x = self.tile.x+(self.tile.x*tileSize)
        y = self.tile.y+(self.tile.y*tileSize)
        return(PixelGrid(self.tile.zoom, x, y))



