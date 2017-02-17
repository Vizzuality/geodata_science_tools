import time
from os.path import basename, dirname, exists
import os
import rasterio
import numpy
import glob

# variables
path = glob.glob("/Users/alicia/Downloads/bra_land_cover/*.tif")
mypath = "/Users/alicia/Downloads/bra_land_cover/new/"

thres_val = 762
ramp = [500,800,900]
colouring = ["3,3,3","3,4,5","5,5,6"]
hex_colouring = ["#ffffff","#ffffff","#ffffff"]

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.mkdir(d)

#this reclass everything into the threshold
def threshold(thres_val):
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

#this one print the cartocss into a file on the same folder as the new data
def print_cartocss(dir,text):
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
		    # print src.min()
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
		print numpy.unique(masked_array)
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
	        print windows
	        print kwargs
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