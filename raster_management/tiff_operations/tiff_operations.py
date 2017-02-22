from __future__ import print_function, division
import time
from os.path import basename, dirname, exists
import os
import rasterio
import numpy
import glob
import argparse
import pprint
from colorama import Fore, Back, Style

#
# # variables
# path = glob.glob("/Users/alicia/Downloads/bra_land_cover/*.tif")
# mypath = "/Users/alicia/Downloads/bra_land_cover/new/"
#
# thres_val = 762
# ramp = [500,800,900]
# colouring = ["3,3,3","3,4,5","5,5,6"]
# hex_colouring = ["#ffffff","#ffffff","#ffffff"]

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.mkdir(d)

def threshold(thres_val):
    """this reclass everything into the threshold"""
    for i in path:
        with rasterio.open(i,masked=None) as src:
            array = src.read()
            profile = src.profile
            profile.update(
                compress='lzw')
        array[array < thres_val] = 0
        array[array >= thres_val] = 255
        paths=mypath + basename(i)
        ensure_dir(paths)
        # Write to tif, using the same profile as the source
        with rasterio.open(mypath + basename(i), 'w', **profile) as dst:
            dst.write(array)

def print_cartocss(dir,text):
    """this one print the cartocss into a file on the same folder as the new data"""
    with open(dir, 'w') as the_file:
        the_file.write(text)

def coloring_generator(vals, text,is_hex):
    if is_hex:
        return map(lambda x: text + str(x) +", ", vals)
    else:
        return map(lambda x: text + x +",1))", vals)

def create_cartocss(vals,colors, mode, is_hex):
    body = "{raster-opacity:1; raster-scaling:near; raster-colorizer-default-mode:" + mode + "; raster-colorizer-default-color:  transparent; raster-colorizer-epsilon:0.41; raster-colorizer-stops: "
    RGBA = "rgba("
    STOP ="stop("
    if is_hex:
        colouring = map(lambda x: x +")", colors)
    else:
        colouring = coloring_generator(colors,RGBA,False)

    stops = coloring_generator(vals,STOP,True)
    former =" ".join(numpy.core.defchararray.add(stops, colouring))
    return  body + former + '}'

def interpolation(path,ramp,colouring):
    for i in path:
        paths=mypath + basename(i)
        carto_path = paths + "_cartocss.cartocss"
        with rasterio.open(i) as src:
            array = src.read()
            # print(src.min())
            masked_array=numpy.ma.masked_equal(array, src.nodatavals)
            min_val = masked_array.min()
            max_val	= masked_array.max()
            profile = src.profile
            profile.update(
                compress='lzw')

        masked_array = numpy.around((masked_array-min_val)*255/(max_val-min_val),4)
        array=numpy.ma.filled(masked_array,src.nodatavals)

        ensure_dir(paths)
        ramp_interpolate=numpy.around((ramp-min_val)*255/(max_val-min_val),4)
        cartocss = create_cartocss(ramp_interpolate,colouring, "linear", False)
        print_cartocss(carto_path,cartocss)
        print(numpy.unique(masked_array))
        # numpy.unique(array)
        # Write to tif, using the same profile as the source
        with rasterio.open(mypath + basename(i), 'w', **profile) as dst:
            dst.write(array)

def categorical():
    for i in path:
        paths=mypath + basename(i)
        carto_path = paths + "_cartocss.cartocss"
        with rasterio.open(i) as src:
            array = src.read()

            masked_array=numpy.ma.masked_equal(array, src.nodatavals)
            min_val = masked_array.min()
            max_val	= masked_array.max()
            profile = src.profile
            profile.update(
                compress='lzw')
def original():
    for i in path:
        paths=mypath + basename(i)
        ensure_dir(paths)
        carto_path = paths + "_cartocss.cartocss"
        with rasterio.drivers():
            with rasterio.open(i) as src:
                kwargs = src.meta
                kwargs.update(
                    driver='GTiff',
                    dtype=rasterio.uint16,
                    count=1,
                    compress='lzw',
                    nodata=0,
                    bigtiff='YES' # Output will be larger than 4GB
                )
                windows = src.block_windows(1)
                print(windows)
                print(kwargs)
                with rasterio.open(paths,
                        'w',
                        **kwargs) as dst:
                    for idx, window in windows:
                        src_data = src.read_band(1, window=window)

                        # Source nodata value is a very small negative number
                        # Converting in to zero for the output raster
                        #np.putmask(src_data, src_data < 0, 0)

                        dst_data = (src_data * 3).astype(rasterio.uint16)
                        dst.write_band(1, dst_data, window=window)
#interpolation(path, ramp, colouring)


def main(input_file, output_file):
    print("{0} --> {1}".format(input_file, output_file))
    # test mod
    return



if __name__ == '__main__':
    # A COMMAND LINE PARSER TO EXTRACT INPUT_PATH/INPUT_FILE AND OUTPUT_PATH/TARGET_FILE
    parser = argparse.ArgumentParser(description='When passed a geotiff file, this program will resize it.')
    parser.add_argument('input_file', type=str, help='A Tiff input file string <path/filename.tiff>')
    parser.add_argument('output_file', type=str, help='An output name for the file <path/filename.tiff>')
    args = parser.parse_args()
    assert os.path.isfile(args.input_file), Fore.RED + "Input file {input} does not exist".format(input=args.input_file)
    if os.path.isfile(args.output_file):
        print(Fore.RED + "Output target {output} already exists: it will be overwritten.".format(output=args.output_file))
    print(Style.RESET_ALL)
    print(Fore.GREEN + "Processing {0}".format(args.input_file))
    print(Style.RESET_ALL)

    main(args.input_file, args.output_file)