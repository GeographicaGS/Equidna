import mapnik
m = mapnik.Map(256,256)
m.buffer_size = 128
# Load Mapnik stylesheet
mapnik.load_map(m, 'mapnik.xml')

m.zoom_all()
mapnik.render_to_file(m,'world.png', 'png')

import hashlib
m = hashlib.md5()
m.update('aaa')
print m.hexdigest()

