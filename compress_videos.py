#!/usr/bin/python3
"""
Compress videos using ffmpeg

Default config for now is: 720p at max, 30fps, H.264
Renames files from "name.mp4" to "name.cmp1.mp4", and moves original pure .mp4 file to given folder
Thanks to this naming scheme, it automatically skips all files with ".cmp" in the name

Also, you can put a .cmpignore file in the input folder, and it will skip files that match globs in it.
But don't be too fast - it's not as advanced as the .gitignore, stuff like "!" will not work :c
"""
import argparse as ap
import shutil
import subprocess
from pathlib import Path

from humanize import filesize
from tqdm import tqdm

# Statistics to see how much I actually get from this :D
stats = {
    "total_videos_found": 0,
    "total_videos_compressed": 0,
    "uncompressed_space": 0,
    "compressed_space": 0
}

# Namespaces that are added to file extension after compression
EXTENSION_NAMESPACES = {
    # Stands for "compression v1"
    "h265_720p_30fps": "cmp1"
}


def file_was_compressed(file: Path) -> bool:
    for suff in file.suffixes:
        if suff.replace('.', '') in EXTENSION_NAMESPACES.values():
            return True
    return False


COMPRESSED_EXTENSIONS = ["mp4"]

parser = ap.ArgumentParser()
parser.add_argument("--input", "-i", help="Input dir with uncompressed", required=False, default=".")
parser.add_argument("--originals", help="Output dir for originals", required=False)
parser.add_argument("--output", "-o", help="Output dir for compressed", required=False)
parser.add_argument("--cmpignore", help="Location of .cmpignore file which contains files to ignore", required=False)
args = parser.parse_args()

INPUT_DIR = Path(args.input)
ORIGINALS_DIR = Path(args.originals if args.originals else "../../_camera_originals")
OUTPUT_DIR = Path(args.output if args.output else args.input)
CMPIGNORE_FILE = Path(args.cmpignore if args.cmpignore else INPUT_DIR / ".cmpignore")
CMPIGNORE_GLOBS: list[str] = []


def get_video_size(file: Path) -> tuple[int, int]:
    """
    :return: Tuple of (width, height) of the video
    """
    res_str = subprocess.run(
        f"ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x ".split() + [str(file)],
        check=True, capture_output=True
    )
    w, h = res_str.stdout.decode('utf-8').split("x")
    return int(w), int(h)


def get_ffmpeg_dimens(input_size: tuple[int, int], max_res: int) -> str:
    """
    :param input_size: Tuple of (width, height)
    :param max_res: Maximum resolution (as in 1080p, 720p, 360p, etc)
    :return: String that can be used in ffmpeg -vf
    """
    w, h = input_size
    return f"scale={min(max_res, w)}:-2" if w < h else f"scale=-2:{min(max_res, h)}"


def compress_file_h265_720p_30fps(file: Path):
    print(f"Compressing {file}")
    # Add ".cmp" before ".mp4"
    output_file = file.with_stem(file.stem + "." + EXTENSION_NAMESPACES["h265_720p_30fps"])
    out_path = OUTPUT_DIR / output_file.name
    if out_path.exists():
        raise Exception(f"Output file {out_path} already exists")
    print(f"Output file {out_path}")

    # Compress with ffmpeg - set max resolution to 720p, 30fps and H.265 encoding
    subprocess.run(
        ["ffmpeg", "-i", str(file)] +  # Watch out for splitting the file name :P
        f"-map_metadata 0 -vf {get_ffmpeg_dimens(get_video_size(file), 720)},fps=30 -c:v libx265 ".split()
        + [str(out_path)],
        check=True, capture_output=True
    )
    shutil.copystat(file, out_path)
    # Save sizes to see how much we save later
    stats["uncompressed_space"] += file.stat().st_size
    stats["compressed_space"] = out_path.stat().st_size
    shutil.move(file, ORIGINALS_DIR)


if CMPIGNORE_FILE.exists():
    with CMPIGNORE_FILE.open() as f:
        CMPIGNORE_GLOBS = [line.strip() for line in f]


def is_ignored(file: Path) -> bool:
    """
    :return: if file should be ignored (matches any glob in .cmpignore)
    """
    for glob in CMPIGNORE_GLOBS:
        if file.match(glob):
            return True
    return False


# *The* main part :sparkles:
# Iterate through all video files
target_videos: list[Path] = []
for _ext in COMPRESSED_EXTENSIONS + list(map(lambda x: x.upper(), COMPRESSED_EXTENSIONS)):
    for file in INPUT_DIR.glob(f"*.{_ext}"):
        stats["total_videos_found"] += 1
        if is_ignored(file):
            print(f"Ignoring {file} - .cmpignore")
            continue
        if file_was_compressed(file):
            print(f"Skipping {file} - already compressed")
            continue
        target_videos.append(file)

for file in tqdm(target_videos):
    compress_file_h265_720p_30fps(file)
    stats["total_videos_compressed"] += 1

# Done - print all stats
print(f"Videos found: {stats['total_videos_found']}")
print(f"Videos compressed: {stats['total_videos_compressed']}")
print(f"Uncompressed space: {filesize.naturalsize(stats['uncompressed_space'])}")
print(f"Compressed space: {filesize.naturalsize(stats['compressed_space'])}")
print(f"Saved space: {filesize.naturalsize(stats['uncompressed_space'] - stats['compressed_space'])}")
