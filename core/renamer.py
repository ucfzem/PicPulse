import os
import shutil
from pathlib import Path
from collections import defaultdict


IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}


class ImageRenamer:
    def __init__(self, add_flare_tag=True, dry_run=False):
        self.add_flare_tag = add_flare_tag
        self.dry_run = dry_run
        self.counters = defaultdict(int)

    def is_image(self, filename):
        return Path(filename).suffix.lower() in IMAGE_EXTENSIONS

    def get_new_name(self, keyword, suffix, has_flare=False):
        self.counters[keyword] += 1
        counter = self.counters[keyword]
        base_name = f"{keyword}_{counter:03d}{suffix}"
        if has_flare and self.add_flare_tag:
            base_name = f"flare_{base_name}"
        return base_name

    def process_directory(self, source_dir, progress_callback=None, file_callback=None):
        source = Path(source_dir)
        if not source.is_dir():
            raise ValueError(f"Directory not found: {source_dir}")

        image_files = []
        for root, dirs, files in os.walk(source):
            root_path = Path(root)
            for f in sorted(files):
                if self.is_image(f):
                    image_files.append(root_path / f)

        total = len(image_files)
        results = []

        for idx, img_path in enumerate(image_files):
            try:
                if file_callback:
                    file_callback(img_path, idx, total)

                suffix = img_path.suffix.lower()
                parent_dir = img_path.parent

                flare_data = None
                analysis = None

                yield {
                    "type": "progress",
                    "current": idx + 1,
                    "total": total,
                    "image_path": str(img_path),
                    "status": "analyzing",
                }

                if hasattr(self, 'analyzer_callback'):
                    analysis = self.analyzer_callback(img_path)
                if hasattr(self, 'flare_callback'):
                    flare_data = self.flare_callback(img_path)

                keyword = "unknown"
                if analysis and analysis.get("success"):
                    keyword = analysis["top_label"]

                has_flare = False
                if flare_data and flare_data.get("success"):
                    has_flare = flare_data["has_flare"]

                new_name = self.get_new_name(keyword, suffix, has_flare=has_flare)
                new_path = parent_dir / new_name

                renamed = False
                if str(img_path) != str(new_path):
                    if not self.dry_run:
                        os.rename(str(img_path), str(new_path))
                    renamed = True

                result = {
                    "type": "result",
                    "current": idx + 1,
                    "total": total,
                    "original_path": str(img_path),
                    "new_path": str(new_path),
                    "keyword": keyword,
                    "has_flare": has_flare,
                    "flare_score": flare_data.get("flare_score", 0) if flare_data else 0,
                    "confidence": analysis.get("confidence", 0) if analysis else 0,
                    "renamed": renamed,
                    "status": "renamed" if renamed else "skipped",
                }
                results.append(result)
                yield result

            except Exception as e:
                error_result = {
                    "type": "error",
                    "current": idx + 1,
                    "total": total,
                    "image_path": str(img_path),
                    "error": str(e),
                    "status": "error",
                }
                results.append(error_result)
                yield error_result

        yield {"type": "complete", "total": total, "processed": len(results), "results": results}

    def preview(self, source_dir):
        source = Path(source_dir)
        if not source.is_dir():
            raise ValueError(f"Directory not found: {source_dir}")

        image_files = []
        for root, dirs, files in os.walk(source):
            root_path = Path(root)
            for f in sorted(files):
                if self.is_image(f):
                    image_files.append(root_path / f)

        return image_files
