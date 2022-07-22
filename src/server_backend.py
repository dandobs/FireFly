from flask import Flask
import json
from flask import request

from db_util import create_db_connection, execute_query, read_query, getFlightNum

"""
Hotspot statuses
0: not viewed
1: viewed
2: attending (going to assess the fire)
3: dismissed
"""

pw = "Fire2022!"
sqlConn = create_db_connection("localhost", "root", pw, "firefly_db")
statuses = ["not viewed", "viewed", "attending", "dismissed"]
app = Flask(__name__)
app.run()


@app.route("/getAllImages", methods=["GET"])
def getAllImages():
    print("retrieving all images")
    lastFlightNum = getFlightNum(sqlConn)

    query = """SELECT image_records.locID, 
                image_records.flightNum, 
                image_records.date_time, 
                image_records.irImagePath, 
                rgbImagePath, 
                locations.lon, 
                locations.lat,
                hotspots.size
                FROM image_records
                INNER JOIN locations 
                ON image_records.locID = locations.locID
                INNER JOIN hotspots
                ON image_records.locID = hotspots.locID
                WHERE image_records.flightNum = %s;"""
    lastFlightNum = 1
    params = [lastFlightNum]
    result = read_query(sqlConn, query, params, as_json=True)

    # convert image paths to actual byte data

    return result if result else -1


# getAllImages()
