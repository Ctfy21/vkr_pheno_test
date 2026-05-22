# PlantCV Contour Test Solution

Test phenotyping solution for PhenoPlant.

- Uses PlantCV to segment plant regions.
- Finds the contour and bounding box for the main plant object.
- Writes JSON output with per-image metrics.

Run:

```bash
python run.py --input /data/images --output /data/results.json
```
