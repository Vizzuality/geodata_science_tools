from ..tiff_operations import ManageTiff
import rasterio

def test_extract_meta():
    meta = {'count': 3,
             'crs': rasterio.crs.CRS({'init': 'epsg:32618'}),
             'driver': 'GTiff',
             'dtype': 'uint8',
             'height': 718,
             'nodata': 0.0,
             'width': 791}
    geo = ManageTiff('./data/RGB.byte.tif', './blah.tif')
    assert geo.metadata['count'] == meta['count'], "Metadata not equal!"
    assert geo.metadata['crs'] == meta['crs'], "Metadata not equal!"
    assert geo.metadata['dtype'] == meta['dtype'], "Metadata not equal!"
    return
