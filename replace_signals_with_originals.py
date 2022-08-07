"""
Made by @TheLastGimbus at ~06.08.2022

It's main purpouse is to help orgainise album of photos that I make with my s/o
One of problems I had is that I often send photos to my s/o through Signal, they
save it, and put in the folder (that is synced with Syncthing). Then, if I would
put original photo from my phone camera, we would have a duplicate. This script
searches for such "signal photos" and replaces them :)
"""

import sys

if len(sys.argv) < 3:
    print("""This script takes album folder from first arg, and main "Camera folder" from
second arg. Then, it searches for any similar (after compression etc) photos,
copies the original ones from "Camera folder", and moves the "probably
compressed ones" out, to "$ALBUM_FOLDER/../_$ALBUM_FOLDER_replaced".

Note that all of this can take some time - it compares the look of photos,
not just hashes etc.

So, run it like:
  python replace_signals_with_originals.py "/home/user/Pictures/MyAlbum" "/home/user/Pictures/Camera"
""")
    exit(0)

from pathlib import Path


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


ALBUM_FOLDER = Path(sys.argv[1])
if not ALBUM_FOLDER.exists():
    eprint("Album folder doesn't exist!")
    exit(1)
CAMERA_FOLDER = Path(sys.argv[2])
if not CAMERA_FOLDER.exists():
    eprint("Camera folder doesn't exist!")
    exit(1)

extra_args = sys.argv[3:]
opt_dry_run = ('--dry-run' in extra_args)
if opt_dry_run:
    print("Running dry (don't actually move any files)")

import shutil
from os.path import getsize
import difPy
from tqdm import tqdm

print('Searching...')
search = difPy.dif(ALBUM_FOLDER, CAMERA_FOLDER)
print('Search finished!')
dup = {}
for i in search.result:
    d = Path(search.result[i]['duplicates'][0])
    i = (ALBUM_FOLDER / i)
    if i.exists() and d.exists() and getsize(i) != getsize(d):
        dup[i] = d

print(f'Found {len(dup)} "signals"')
replaced_count = 0
for i in dup:
    print(i, dup[i])
    if (ALBUM_FOLDER / dup[i].name).exists():
        print(f'{i.name} (signal-ish) and {dup[i].name} (original) both exist in album folder - only original will be '
              f'left')
        replaced_count += 1

if not opt_dry_run:
    MOVE_FOLDER = ALBUM_FOLDER.parent / f'_{ALBUM_FOLDER.name}_replaced'
    MOVE_FOLDER_REPLACED = MOVE_FOLDER / 'replaced'
    MOVE_FOLDER_ORIGINAL = MOVE_FOLDER / 'original'
    MOVE_FOLDER_REPLACED.mkdir(parents=True, exist_ok=True)
    MOVE_FOLDER_ORIGINAL.mkdir(parents=True, exist_ok=True)
    print(f'Moving them to "{MOVE_FOLDER}" folder and coping originals from "{CAMERA_FOLDER}"')

    for i in tqdm(dup):
        shutil.move(i, MOVE_FOLDER_REPLACED)
        shutil.copy2(dup[i], ALBUM_FOLDER)
        shutil.copy2(dup[i], MOVE_FOLDER_ORIGINAL)
    if replaced_count > 0:
        print(f'{replaced_count} photos were already present in album folder and were replaced.')
        print('You will see this as less items count in the album folder (because you had duplicates - both signal and '
              'camera photos)')
    with open(MOVE_FOLDER / 'list.txt', 'w') as f:
        for i in dup:
            f.write(f'{i}:{dup[i]}\n')
