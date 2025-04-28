from flask import Flask, render_template, request
from mbta_helper import find_stop_near

app = Flask(__name__)


@app.route("/")
def index():
    """Show the home page with the search form."""
    return render_template("index.html")


@app.route("/nearest_mbta", methods=["POST"])
def nearest_mbta():
    """Handle the form submission and show the result page."""
    place = request.form.get("place", "").strip()
    if not place:
        return render_template("error.html", message="Please enter a place.")
    try:
        station, wheelchair = find_stop_near(place)
        return render_template(
            "mbta_station.html",
            place=place,
            station=station,
            wheelchair=wheelchair,
        )
    except Exception as exc:
        return render_template(
            "error.html",
            message=f"Sorry, could not find a station for “{place}”. ({exc})",
        )
    
if __name__ == "__main__":
    app.run(debug=True)     # auto-reloads whenever you save