#coding: utf-8

import os
from pngquant import tiny



def compressPNG_01(orig_pngfile, dest_pngfile, origin_img_width, origin_img_height):
    
    with open(orig_pngfile, 'rb') as origin:
        rv = tiny(origin.read(), origin_img_width, origin_img_height)
        
        with open(dest_pngfile, 'wb') as compressed:
            compressed.write(rv)
            # print "Compressed file: {}".format(dest_pngfile)

def compressPNG_02(orig_pngfile, dest_pngfile):
    cmd = "pngquant {0} -o {1}".format(orig_pngfile, dest_pngfile)
    os.system(cmd)
    print "Compressed file: {}".format(dest_pngfile)

def makeDir(dir_path):
        if os.path.exists(dir_path):
            return
        os.makedirs(dir_path)

#png_folder = '/tmp/535_WIND_20150315155318_4845_YUXH60EGRR151200_20150315155318_4859_YVXH60EGRR151200'
# png_folder = '/tmp/200762_TEMP_20150614155422_7743_YTXI85EGRR141200'
png_folder = '/data/tmp/29793_TEMP_20150722040016_2773_YTXI85EGRR220000'


origin_img_width = 256
origin_img_height = 256


for subdir, dirs, files in os.walk(png_folder):
    # Walking through folders
    for fl in files:
        orig_pngfile = "{0}/{1}".format(subdir, fl)
        # dest_pngfile = "/tmp/compressed{0}".format(orig_pngfile)
        dest_pngfile = "/data/tmp/compressed{0}".format(orig_pngfile)
        makeDir(os.path.dirname(dest_pngfile))
        compressPNG_01(orig_pngfile, dest_pngfile, origin_img_width, origin_img_height)
        # compressPNG_02(orig_pngfile, dest_pngfile)
    
