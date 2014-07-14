=======
Equidna
===========


## About

Equidna is a Tile builder based on Mapnik. An easy way of create MBTiles using mapnik as render.

It's a multi-thread application. By default, it uses all the cores available but it could be configured.

## How to use

```
from equidna import Equidna

metadata = {
	"bounds" : "-180,-85,180,85",
	"center" : "0,0,1",
	"minzoom" : 0,
	"maxzoom" : 10,
	"name" : "Test",
	"description" : "",
	"attribution" : "",
	"template" : "",
	"version" : "1.0.0",
	"format"  : "png"
}

eq = Equidna(mapnikxml = "mapnik.xml", metadata = metadata,ncores=None)

eq.build(output="test.mbtiles",format="mbtiles")
```
