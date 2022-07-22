from flask import Flask
import json
from flask import request

from db_util import create_db_connection, execute_query, read_query

"""
Hotspot statuses
0: not viewed
1: viewed
2: attending (going to assess the fire)
3: dismissed
"""

pw = "MySQL1738!"
sqlConn = create_db_connection("localhost", "root", pw, "firefly")
statuses = ["not viewed", "viewed", "attending", "dismissed"]
app = Flask(__name__)
app.run()


@app.route("/updateStatus", methods=["POST"])
def updateHotspotStatus():
    status = request.json.get("status")
    id = request.json.get("id")

    if status < 0 or status > 3:
        print("ERROR: INVALID STATUS PROVIDED!!!")
        return -1

    query_setViewed = f"UPDATE hotspots SET 'status'={status} WHERE hotspotID={id};"
    execute_query(sqlConn, query_setViewed)

    print(f"set hotspot {id} status to '{statuses[status]}'")
    return 0


@app.route("/getAllImages", methods=["GET"])
def getAllImages():
    print("retrieving all images")
    query_getAllHSdata = f"SELECT *, locations.long, locations.lat FROM hotspots INNER JOIN locations ON hotspots.locID = locations.locID WHERE hotspots.status != 3;"
    result = read_query(sqlConn, query_getAllHSdata)

    if not result:
        return -1

    # make result readable
    return result


@app.route("/getAllHotspots", methods=["GET"])
def getAllHotspots():
    print("retrieving all hotspots data")
    query_getAllHSdata = f"SELECT *, locations.long, locations.lat FROM hotspots INNER JOIN locations ON hotspots.locID = locations.locID WHERE hotspots.status != 3;"
    result = read_query(sqlConn, query_getAllHSdata)

    if not result:
        return -1

    # make result readable
    return result
