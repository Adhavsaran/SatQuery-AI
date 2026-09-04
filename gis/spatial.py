"""CRS-safe coordinate and measurement helpers."""
from pyproj import CRS, Transformer
from shapely.ops import transform
def pixel_to_world(affine, col, row): return tuple(affine * (col,row))
def world_to_pixel(affine,x,y): return tuple((~affine) * (x,y))
def transform_geometry(geometry, source_crs, destination_crs):
    return transform(Transformer.from_crs(source_crs,destination_crs,always_xy=True).transform,geometry)
def metric_crs_for(geometry, crs):
    source=CRS.from_user_input(crs)
    if source.is_projected: return source
    centroid=transform_geometry(geometry,source,"EPSG:4326").centroid; zone=int((centroid.x+180)//6)+1
    return CRS.from_epsg((32600 if centroid.y>=0 else 32700)+zone)
def area_m2(geometry, crs):
    target=metric_crs_for(geometry,crs); return transform_geometry(geometry,crs,target).area
def distance_m(a,b,crs):
    target=metric_crs_for(a.union(b),crs); return transform_geometry(a,crs,target).distance(transform_geometry(b,crs,target))
