#coding: utf-8

import os
from multiprocessing import Pool 
from pngquant import tiny



def compressPNG_01(input_params):
    
    orig_pngfile, dest_pngfile, origin_img_width, origin_img_height = input_params
    
    with open(orig_pngfile, 'rb') as origin:
        rv = tiny(origin.read(), origin_img_width, origin_img_height)
        
        with open(dest_pngfile, 'wb') as compressed:
            compressed.write(rv)
            pid = os.getpid()
            print "PID: {0} - Compressed file: {1}".format(pid, dest_pngfile)


def compressPNG_02(input_params):
    
    orig_pngfile, dest_pngfile, origin_img_width, origin_img_height = input_params
    
    cmd = "pngquant {0} -o {1}".format(orig_pngfile, dest_pngfile)
    os.system(cmd)
    pid = os.getpid()
    print "PID: {0} - Compressed file: {1}".format(pid, dest_pngfile)


def makeDir(dir_path):
        if os.path.exists(dir_path):
            return
        os.makedirs(dir_path)


def getPathList(png_folder, origin_img_width, origin_img_height):
    
    paths_lst = []
    
    for subdir, dirs, files in os.walk(png_folder):
        # Walking through folders
        for fl in files:
            orig_pngfile = "{0}/{1}".format(subdir, fl)
            dest_pngfile = "/tmp/compressed{0}".format(orig_pngfile)
            makeDir(os.path.dirname(dest_pngfile))
            paths_lst.append((orig_pngfile, dest_pngfile, origin_img_width, origin_img_height))
    
    return paths_lst


if __name__ == '__main__':
    
    # png_folder = '/tmp/87509_WIND_20151008101438_8788_YVXI40EGRR080600_20151008101437_8771_YUXI40EGRR080600'
    #png_folder = '/tmp/4939_TEMP_20150718220025_1291_YTXH40EGRR181800'
    png_folder = '/data/tmp/29793_TEMP_20150722040016_2773_YTXI85EGRR220000'
    
    origin_img_width = 256
    origin_img_height = 256
    
    arrs_input = getPathList(png_folder, origin_img_width, origin_img_height)

    pool = Pool(processes=None)
    #pool.map(compressPNG_01, arrs_input)
    pool.map(compressPNG_02, arrs_input)
    pool.close() 
    pool.join()
    
