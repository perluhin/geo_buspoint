# -*- coding: utf-8 -*-

import json
import math
from pymongo import MongoClient


def get_buspoint(**kwargs):
    for buspoint in db.buspoint.find(kwargs):
        yield buspoint


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371*c
    return km


dist = 0.5
koef_lat = 111.32137 # 1 градус широты ~111.3 км
exit_subway_dict = {"len": 0, "info": [], "buspoint": []} # выход из метро
# без учета цвета
subway_result_dict = {}
max_point_dict = {"name": "", "len": 0}
#с учетом цвета
subway_result_color_dict = {}
max_point_color_dict = {"name": "", "len": 0}

subwaypoint_file = 'data-397-2017-10-31.json'

with open(subwaypoint_file) as data_file:
    decode_data = data_file.read().decode('cp1251').encode('utf-8')
    subwaypoint_json = json.loads(decode_data)

client = MongoClient()
db = client.geo_buspoint

for point in subwaypoint_json:
    lon_subway = float(point["Longitude_WGS84"])
    lat_subway = float(point['Latitude_WGS84'])
    delta_lon = dist / abs(math.cos(math.radians(float(point['Latitude_WGS84']))) * koef_lat)
    # ищем остановки в квадрате
    lon1 = lon_subway - delta_lon
    lon2 = lon_subway + delta_lon
    lat1 = lat_subway - (dist / koef_lat)
    lat2 = lat_subway + (dist / koef_lat)
    buspoint_list = [x for x in get_buspoint(lat={"$lt": lat2, "$gt": lat1}, lon={"$lt": lon2, "$gt": lon1})]

    # выбираем в радиусе
    buspoint_result_list = [x for x in buspoint_list if haversine(lon_subway, lat_subway, x['lon'], x['lat']) <= dist]

    # выясняем, у какого выхода больше всего остановок в радиусе
    if len(buspoint_list) >= exit_subway_dict["len"]:
        exit_subway_dict.update({
            "len": len(buspoint_result_list),
            "info": point,
            "buspoint": buspoint_result_list
        })

    len_buspoint = len(buspoint_result_list)
    key = point["NameOfStation"]

    # выясняем, у какой станции метро больше всего остановок (игнорируем цвет линий)
    if key in subway_result_dict:
        subway_result_dict[key] += len_buspoint
    else:
        subway_result_dict[key] = len_buspoint
        if len_buspoint >= max_point_dict["len"]: max_point_dict.update({"name": key, "len": len_buspoint})

    # выясняем, у какой станции метро больше всего остановок (учитывая цвет линий)
    line = point["Line"]
    key = key + ' ' + line
    if key in subway_result_color_dict:
        subway_result_color_dict[key] += len_buspoint
    else:
        subway_result_color_dict[key] = len_buspoint
        if len_buspoint >= max_point_color_dict["len"]: max_point_color_dict.update({"name": key, "len": len_buspoint})


print exit_subway_dict["info"]["Name"], exit_subway_dict["len"]
print "%(name)s: %(len)d" %max_point_dict
print "%(name)s: %(len)d" %max_point_color_dict
