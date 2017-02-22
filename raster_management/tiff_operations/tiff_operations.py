from __future__ import print_function, division
import time
from os.path import basename, dirname, exists
import os
import copy
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


class ManageTiff(object):
    def __init__(self, input_file, output_file):
        assert os.path.isfile(input_file), Fore.RED + "Input file {input} does not exist".format(input=input_file)
        if os.path.isfile(output_file):
            print(Fore.RED + "Warning: {output} already exists and will be overwritten.".format(output=output_file))
        print(Style.RESET_ALL)
        self.input_file = input_file
        self.output_file = output_file
        with rasterio.open(self.input_file) as src:
            self.metadata = src.meta
            self.profile = src.profile
            self.image_array = src.read()


    def display_metadata(self):
        """example data at './tiff_operations/tests/data/RGB.byte.tif' """
        with rasterio.open(self.input_file) as src:
            print('File name: ', src.name)
            print('Source bands:', src.count)
            print("Band indexes: ", src.indexes)
            print("Array dimensions: ", src.shape)
            print("Compression type:", src.compression)
        for key in self.metadata:
            if key != 'transform':
                print('{key}: {val}'.format(key=key, val=self.metadata[key]))
            if key == 'transform':
                print('{key} : '.format(key=key))
                print(self.metadata[key])
        return

    def band_preview(self, index=0):
        """Return an image of a specified band (by index)"""
        import matplotlib.cm as cm
        import matplotlib.pyplot as plt
        """Given an index of a band (default 0), return a simple preview plot."""
        plt.imshow(self.image_array[index], cmap=cm.gist_earth)
        plt.show()

    def compress_file(self, compression='lzw', data_type='uint8', band_index=0):
        """ Save the array data with a specified compression and data type.
        Data_type could be 'unit8', 'unit16', 'unit32', 'int8','int16', or 'int32'.
        If there are multiple bands of data, you can specifcy which to extract by setting the band_index keyword.
        e.g.
        tiffobj = ManageTiff('./tiff_operations/tests/data/RGB.byte.tif','./example-total.tif')
        tiffobj.compress()
        """

        # if len(self.image_array.shape) > 2:
        #     single_band = self.image_array[band_index]
        # elif len(self.image_array == 2):
        #     single_band = self.image_array
        # else:
        #     return AttributeError("Uknown dimensions of image_array {imshape}".format(imshape=self.image_array.shape))
        # #
        # # print("SHAPE OF IMAGE ARRAY: {0}".format(self.image_array.shape))
        # # print("SHAPE OF NEW IMAGE ARRAY: {0}".format(single_band.shape))
        # #
        # print("Original profile")
        # print(self.profile)
        # local_profile = copy.deepcopy(self.profile)
        #
        # local_profile.update(dtype=data_type, count=1, compress=compression)
        #
        # print("Updated profile?")
        # print(local_profile)
        #
        # with rasterio.open(self.output_file, 'w', **local_profile) as dst:
        #     dst.write(total.astype(data_type, 1))
        #
        #
        # print(Fore.GREEN + "Success! Compressed {0} to {1}".format(self.input_file, self.output_file))
        # print(Style.RESET_ALL)
        # return


if __name__ == '__main__':
    # A COMMAND LINE PARSER TO EXTRACT INPUT_PATH/INPUT_FILE AND OUTPUT_PATH/TARGET_FILE
    parser = argparse.ArgumentParser(description='When passed a geotiff file, this program will resize it.')
    parser.add_argument('input_file', type=str, help='A Tiff input file string <path/filename.tiff>')
    parser.add_argument('output_file', type=str, help='An output name for the file <path/filename.tiff>')
    args = parser.parse_args()

    geo = ManageTiff(args.input_file, args.output_file)
    #geo.display_metadata()
    geo.compress_file()