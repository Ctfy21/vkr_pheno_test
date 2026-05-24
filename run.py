import argparse
import json
import time
import os
from pathlib import Path

import cv2
import numpy as np
from plantcv import plantcv as pcv


def analyze_image(image_path: Path) -> dict:
    img = cv2.imread(str(image_path))
    if img is None:
        return {"file": image_path.name, "error": "failed_to_read"}

    pcv.params.debug = None
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Simple green segmentation tuned for greenhouse imagery
    s = pcv.rgb2gray_hsv(rgb_img=rgb, channel='s')
    sat_mask = pcv.threshold.binary(gray_img=s, threshold=45, object_type='light')

    a = pcv.rgb2gray_lab(rgb_img=rgb, channel='a')
    green_mask = pcv.threshold.binary(gray_img=a, threshold=118, object_type='dark')

    merged = pcv.logical_and(bin_img1=sat_mask, bin_img2=green_mask)
    cleaned = pcv.fill(bin_img=merged, size=150)

    contours, _ = cv2.findContours(cleaned.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {
            "file": image_path.name,
            "contour_found": False,
            "plant_area_px": 0,
            "bbox": {"x": 0, "y": 0, "w": 0, "h": 0},
        }

    largest = max(contours, key=cv2.contourArea)
    area_px = int(cv2.contourArea(largest))
    x, y, w, h = cv2.boundingRect(largest)

    return {
        "file": image_path.name,
        "contour_found": area_px > 0,
        "plant_area_px": area_px,
        "bbox": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
    }


def list_images(input_dir: Path):
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    return sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in exts])


def main():
    parser = argparse.ArgumentParser(description="PlantCV contour detector test solution")
    parser.add_argument("--input", default="/data/images", help="Input directory with images")
    parser.add_argument("--output", default="/data/results.json", help="Output JSON file")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not input_dir.exists() or not input_dir.is_dir():
        payload = {"error": "input_directory_not_found", "input": str(input_dir), "results": []}
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return

    # Demo delay to mimic heavy compute.
    time.sleep(10)
    results = [analyze_image(path) for path in list_images(input_dir)]
    payload = {
        "solution": "plantcv-contour-test",
        "input": str(input_dir),
        "count": len(results),
        "results": results,
    }

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "count": len(results)}))


if __name__ == "__main__":
    main()
