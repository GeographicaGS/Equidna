=======
Equidna
===========


## About

Equidna is a Tile builder based on Mapnik

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

eq = Equidna(mapnikxml = "mapnik.xml", metadata = metadata)

eq.build(output="test.mbtiles",format="mbtiles")
```