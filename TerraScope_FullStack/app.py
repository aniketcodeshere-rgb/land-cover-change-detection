from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import json, csv, io, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 150 * 1024 * 1024
ROOT = Path(__file__).parent
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True)
ALLOWED_GEO = {".geojson", ".json"}
ALLOWED_RASTER = {".tif", ".tiff"}

# Explicitly labelled illustrative values for the demo dashboard.
DEMO = {
    2015: {"Agriculture":42.0,"Built-up":10.2,"Forest":28.0,"Water":7.3,"Barren":12.5},
    2020: {"Agriculture":40.1,"Built-up":13.8,"Forest":26.1,"Water":7.2,"Barren":12.8},
    2025: {"Agriculture":38.2,"Built-up":18.4,"Forest":24.8,"Water":7.1,"Barren":11.5},
    2030: {"Agriculture":36.0,"Built-up":23.0,"Forest":22.0,"Water":7.0,"Barren":12.0},
}
TRANSITIONS = [
    {"from":"Agriculture","to":"Built-up","area_km2":8.7,"meaning":"Urban expansion"},
    {"from":"Forest","to":"Built-up","area_km2":2.1,"meaning":"Settlement growth"},
    {"from":"Agriculture","to":"Barren","area_km2":3.4,"meaning":"Possible land degradation"},
    {"from":"Forest","to":"Agriculture","area_km2":2.8,"meaning":"Possible land conversion"},
    {"from":"Water","to":"Barren","area_km2":0.6,"meaning":"Possible water-edge change"},
]

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/dashboard")
def dashboard():
    try:
        year = int(request.args.get("year", "2025"))
        if year not in DEMO: year = 2025
    except ValueError:
        year = 2025
    return jsonify({
        "year": year,
        "classes": DEMO[year],
        "transitions": TRANSITIONS,
        "status": "illustrative_demo",
        "message": "Sample statistics only; replace with validated satellite-derived results."
    })

@app.post("/api/upload-boundary")
def upload_boundary():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(error="Choose a GeoJSON file first."), 400
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_GEO:
        return jsonify(error="Only .geojson or .json boundary files are supported."), 400
    safe = secure_filename(file.filename)
    path = UPLOADS / safe
    file.save(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("type") not in {"Feature", "FeatureCollection", "Polygon", "MultiPolygon"}:
            raise ValueError("Expected a GeoJSON Feature, FeatureCollection, Polygon, or MultiPolygon.")
        return jsonify(filename=safe, geojson=data, message="Boundary loaded for visualization only.")
    except Exception as exc:
        path.unlink(missing_ok=True)
        return jsonify(error=f"Invalid GeoJSON: {exc}"), 400

@app.post("/api/upload-raster")
def upload_raster():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(error="Choose a GeoTIFF first."), 400
    if Path(file.filename).suffix.lower() not in ALLOWED_RASTER:
        return jsonify(error="Please upload a .tif or .tiff GeoTIFF."), 400
    safe = secure_filename(file.filename)
    path = UPLOADS / safe
    file.save(path)
    # Validate metadata if rasterio is installed; otherwise retain upload for later processing.
    try:
        import rasterio
        with rasterio.open(path) as ds:
            metadata = {"width": ds.width, "height": ds.height, "bands": ds.count,
                        "crs": str(ds.crs), "nodata": ds.nodata}
        return jsonify(filename=safe, metadata=metadata,
                       message="GeoTIFF received. This prototype does not classify the raster automatically.")
    except ImportError:
        return jsonify(filename=safe, metadata=None,
                       message="GeoTIFF uploaded. Install rasterio to inspect metadata; classification is not run automatically.")
    except Exception as exc:
        path.unlink(missing_ok=True)
        return jsonify(error=f"Could not read GeoTIFF: {exc}. Check that it is a valid raster."), 400

@app.get("/api/export.csv")
def export_csv():
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Year","Class","Percentage","Data status"])
    for year, classes in DEMO.items():
        status = "Conceptual projection — not observed" if year == 2030 else "Illustrative demo — not satellite-derived"
        for name, pct in classes.items():
            writer.writerow([year, name, pct, status])
    mem = io.BytesIO(out.getvalue().encode("utf-8-sig"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="lulc_demo_statistics.csv")

@app.get("/api/health")
def health():
    return jsonify(status="ok", app="TerraScope", mode="educational_prototype")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
