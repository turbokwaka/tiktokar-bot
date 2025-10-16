# image_downloader.py

import subprocess
from typing import List
from pathlib import Path


def download_images(url: str) -> List[str]:
    output_dir = Path("../temp")
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "gallery-dl",
        "--directory",
        str(output_dir),
        "--filename",
        "{id}-{num}.{extension}",
        url,
    ]

    result = []
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        result_string = result.stdout.strip()
        full_paths = result_string.split("\n")

        cleaned_paths = [path.replace("# ", "") for path in full_paths]

        result = cleaned_paths
    except subprocess.CalledProcessError:
        return []
    except FileNotFoundError:
        return []

    print(result)
    return result
