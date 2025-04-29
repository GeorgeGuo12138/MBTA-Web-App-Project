from flask import Flask
from flask import Flask, render_template, request
import mbta_helper as mbta_helper

app = Flask(__name__)

# Index
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")
# MBTA_Station.HTML
@app.route("/station", methods=["POST"])
def station():
    place_name = request.form.get("place_name")
    try:
        stop_name, wheelchair_access = mbta_helper.find_stop_near(place_name)
        return render_template(
            "mbta_station.html",
            place_name=place_name,
            stop_name=stop_name,
            wheelchair_access=wheelchair_access,
            error=None
        )
    except Exception as e:
        return render_template(
            "mbta_station.html",
            place_name=place_name,
            stop_name=None,
            wheelchair_access=None,
            error=str(e)
        )

if __name__ == "__main__":
    app.run(debug=True)