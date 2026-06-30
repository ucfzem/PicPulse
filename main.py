#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.processor import ImageProcessor
from ui.app import ImageAnalyzerUI


def main():
    processor = ImageProcessor(flare_threshold=0.3, add_flare_tag=True, dry_run=True)
    app = ImageAnalyzerUI(processor)
    app.mainloop()


if __name__ == "__main__":
    main()
