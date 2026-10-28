# TerraScope — Full-stack LULC Change Detection prototype

## Run on Windows
1. Install Python 3.10 or newer from python.org.
2. Extract this ZIP folder.
3. Double-click `run_windows.bat` (or follow the manual steps below).
4. Wait for dependencies to install. Open `http://127.0.0.1:5000` in your browser.
5. Keep the terminal window open while using the site. Press Ctrl+C in the terminal to stop the server.

## Manual run (Windows / macOS / Linux)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000

## Included
- Flask backend and JSON API (`/api/dashboard`, `/api/health`)
- Interactive Leaflet map with street/satellite/terrain basemaps
- Year selector: 2015, 2020, 2025, 2030
- Land-cover chart and class percentage cards
- Illustrative change matrix and CSV/text exports
- GeoJSON study-boundary upload and map display
- GeoTIFF upload endpoint and metadata inspection when Rasterio is installed
- Responsive front-end

## Important scientific limitations
This is a runnable full-stack educational prototype, not a completed satellite-analysis engine. Current percentages, polygon overlays, and change-matrix areas are explicitly illustrative and are not derived from satellite imagery. The 2030 layer is a conceptual scenario. GeoJSON is displayed as a boundary. GeoTIFF upload only validates/inspects the file; it does not classify pixels.

To produce defensible results, use Google Earth Engine or a Python geospatial pipeline to preprocess Landsat/Sentinel imagery, classify training data, assess accuracy with independent reference samples, compute raster transitions, and connect the resulting validated rasters/statistics to the API. Do not present the sample figures as research findings.

## Troubleshooting
- Basemaps and charts require internet access.
- If `py` is not recognized, install Python and enable "Add Python to PATH".
- If rasterio fails to install on your computer, remove/comment out the optional rasterio line from requirements.txt; GeoJSON and other dashboard features will still run.
