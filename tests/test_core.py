import numpy as np
from pathlib import Path
import rasterio
from rasterio.transform import from_origin
from data.validator import DataValidator
from models.change_detection.core import detect_change
from gis.indices import SpectralIndices
def raster(path,value):
    with rasterio.open(path,'w',driver='GTiff',width=8,height=8,count=3,dtype='uint8',crs='EPSG:32643',transform=from_origin(0,80,10,10),nodata=255) as ds: ds.write(np.full((3,8,8),value,dtype='uint8'))
def test_metadata_and_change(tmp_path):
    a,b=tmp_path/'a_2024.tif',tmp_path/'b_2026.tif'; raster(a,1);raster(b,30)
    v=DataValidator().validate([str(a),str(b)]); assert v.valid and v.images[0].crs=='EPSG:32643'
    result=detect_change(str(a),str(b)); assert result['status']=='SUCCESS' and result['changed_pixel_fraction']==0.0
def test_index_band_contract():
    arr=np.ones((2,2)); assert np.allclose(SpectralIndices().compute_index({'N':arr*3,'R':arr},'NDVI'),.5)
    try: SpectralIndices().compute_index({'N':arr},'NDVI')
    except ValueError: pass
    else: assert False
