from .analyzer import ImageAnalyzer
from .flare_detector import FlareDetector
from .renamer import ImageRenamer


class ImageProcessor:
    def __init__(self, flare_threshold=0.3, add_flare_tag=True, dry_run=False):
        self.analyzer = ImageAnalyzer()
        self.flare_detector = FlareDetector(threshold=flare_threshold)
        self.renamer = ImageRenamer(add_flare_tag=add_flare_tag, dry_run=dry_run)

    def process(self, source_dir):
        self.renamer.counters.clear()

        def analyzer_callback(img_path):
            return self.analyzer.analyze(str(img_path))

        def flare_callback(img_path):
            return self.flare_detector.detect(str(img_path))

        self.renamer.analyzer_callback = analyzer_callback
        self.renamer.flare_callback = flare_callback

        yield from self.renamer.process_directory(source_dir)

    def preview(self, source_dir):
        return self.renamer.preview(source_dir)
