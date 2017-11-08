# -*- coding: utf-8 -*-

import json
from pymongo import MongoClient

client = MongoClient()
db = client.geo_buspoint

buspoint_file = 'data-398-2017-11-02.json'

with open(buspoint_file) as data_file:
    decode_data = data_file.read().decode('cp1251').encode('utf-8')
    buspoint_json = json.loads(decode_data)

for point in buspoint_json:
    db.buspoint.insert({"lat": float(point['Latitude_WGS84']), "lon": float(point["Longitude_WGS84"]), "name": point["Name"]})