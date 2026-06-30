import cv2
import numpy as np
from pathlib import Path


class FlareDetector:
    def __init__(self, threshold=0.3, brightness_threshold=240):
        self.threshold = threshold
        self.brightness_threshold = brightness_threshold

    def detect(self, image_path):
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {"success": False, "error": "Cannot read image"}

            h, w = img.shape[:2]
            total_pixels = h * w

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hsv_f = hsv.astype(np.float32)
            hsv_f[:, :, 0] = hsv_f[:, :, 0] * 2.0

            value = hsv_f[:, :, 2]
            saturation = hsv_f[:, :, 1]
            hue = hsv_f[:, :, 0]

            bright_mask = value > self.brightness_threshold
            bright_ratio = float(np.sum(bright_mask) / total_pixels)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            closed = cv2.morphologyEx(bright_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)

            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)
            flare_regions = []
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area < 50:
                    continue
                left = stats[i, cv2.CC_STAT_LEFT]
                top = stats[i, cv2.CC_STAT_TOP]
                bw = stats[i, cv2.CC_STAT_WIDTH]
                bh = stats[i, cv2.CC_STAT_HEIGHT]

                region = bright_mask[top:top+bh, left:left+bw]
                extent = float(np.sum(region)) / (bw * bh) if bw * bh > 0 else 0

                roi_hue = hue[top:top+bh, left:left+bw]
                mean_hue = float(np.mean(roi_hue[region]))
                is_magenta = 280 <= mean_hue <= 330

                flare_regions.append({
                    "area": int(area),
                    "extent": float(extent),
                    "mean_hue": mean_hue,
                    "is_magenta": bool(is_magenta),
                })

            large_bright_spot_count = sum(1 for r in flare_regions if r["area"] > 500)
            purple_count = sum(1 for r in flare_regions if r.get("is_magenta", False))
            flare_score = 0.0

            if bright_ratio > 0.15:
                flare_score += 0.3
            if large_bright_spot_count >= 2:
                flare_score += 0.3
            if large_bright_spot_count >= 3:
                flare_score += 0.2
            if purple_count >= 1:
                flare_score += 0.2
            if bright_ratio > 0.05 and large_bright_spot_count >= 1:
                flare_score += 0.2

            mean_val = float(np.mean(value))
            if mean_val > 200 and bright_ratio > 0.1:
                flare_score += 0.2

            flare_score = min(flare_score, 1.0)
            has_flare = flare_score >= self.threshold

            return {
                "success": True,
                "has_flare": has_flare,
                "flare_score": round(flare_score, 3),
                "bright_ratio": round(bright_ratio, 3),
                "bright_regions": large_bright_spot_count,
                "purple_regions": purple_count,
                "details": flare_regions[:5],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
