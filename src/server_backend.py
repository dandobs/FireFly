import json
from flask import Flask
from flask import request
import base64
from io import BytesIO
import io
from PIL import Image


from db_util import (
    create_db_connection,
    execute_query,
    read_query,
    getFlightNum,
    json_serial,
)

pw = "superwoofer123"
sqlConn = create_db_connection("localhost", "root", pw, "firefly_db")
statuses = ["not viewed", "viewed", "attending", "dismissed"]
app = Flask(__name__)


@app.route("/")
def main():
    return "BACKEND SERVER STARTED"


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
                LEFT JOIN hotspots
                ON image_records.locID = hotspots.locID
                WHERE image_records.flightNum = %s;"""
    lastFlightNum = 1
    params = [lastFlightNum]
    data = read_query(sqlConn, query, params, as_json=True)

    print(data)
    if not data:
        print("INSUFFICIENT DATA AVAILABLE IN DATABASE")
        return "INSUFFICIENT DATA AVAILABLE IN DATABASE"

    # convert image paths to actual byte data
    for i, record in enumerate(data):
        irPath = record.pop("irImagePath")
        rgbPath = record.pop("rgbImagePath")

        with open(irPath, "rb") as f:
            ir_bytes = f.read()
            ir_b64 = base64.b64encode(ir_bytes).decode("utf8")

        with open(rgbPath, "rb") as f:
            rgb_bytes = f.read()
            rgb_b64 = base64.b64encode(rgb_bytes).decode("utf8")

        data[i]["irData"] = ir_b64
        data[i]["rgbData"] = rgb_b64

    json_data = json.dumps(data, default=json_serial)
    return json_data if data else "ERROR"


app.run()


# DEBUGGGGGING
def encodedecodeImageTest():
    irPath = r"C:\a_UNI\4A\Capstone\FireFly\server_hd\rgb_images\rgb_-0.9497796415476341_-0.26070763235767735__22-07-2022.png"

    # encode
    with open(irPath, "rb") as f:
        ir_bytes = f.read()
        ir_b64 = base64.b64encode(ir_bytes).decode("utf8")

    # decode
    img_bytes = base64.b64decode(ir_b64.encode("utf-8"))  # the line umar needs
    img = Image.open(io.BytesIO(img_bytes))
    img.save("newImage.png")


# encodedecodeImageTest()