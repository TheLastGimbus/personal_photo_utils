def test_get_ffmpeg_dimens():
    from compress_videos import get_ffmpeg_dimens
    assert get_ffmpeg_dimens((2137, 6969), 720) == "scale=720:-2"
    assert get_ffmpeg_dimens((1080, 720), 720) == "scale=-2:720"
    assert get_ffmpeg_dimens((1080, 720), 1080) == "scale=-2:720"
    assert get_ffmpeg_dimens((10, 30), 720) == "scale=10:-2"


def test_parse_cmpignore():
    from compress_videos import parse_cmpignore
    with open('__personal_photo_utils_test_data__/DCIM/Camera/.cmpignore', 'r') as f:
        assert set(parse_cmpignore(f.read())) == {'VID_20191230_215442.mp4', '*.webm'}


def test_is_ignored():
    from pathlib import Path
    from compress_videos import is_ignored
    globs = [
        "final.mp4",
        "video*.mp4",
        "video name with *",
        "*.webm",
    ]
    _ignored = lambda fname: is_ignored(Path(fname), globs)
    assert _ignored("test.mp4") == False
    assert _ignored("final.mp4") == True
    assert _ignored("video_2137.mp4") == True
    assert _ignored("video_2137.webm") == True
    assert _ignored("video_2137.mkv") == False
    assert _ignored("video name with spaces omg.mkv") == True


def test_main():
    import compress_videos as cv
    from pathlib import Path
    import subprocess
    import json

    with open('__personal_photo_utils_test_data__/datetimes.json', 'r') as f:
        datetimes = json.load(f)
    subprocess.run("__personal_photo_utils_test_data__/clean.sh", shell=True)

    assets = Path('./__personal_photo_utils_test_data__/DCIM/')
    orig = assets / "orig"
    orig.mkdir(exist_ok=True)

    cv.INPUT_DIR = assets / "Camera"
    cv.OUTPUT_DIR = cv.INPUT_DIR
    cv.ORIGINALS_DIR = orig
    cv.CMPIGNORE_FILE = cv.INPUT_DIR / ".cmpignore"

    cv.main()

    # That would mean .cmpignore is not working!
    assert cv.stats['total_videos_found'] > cv.stats['total_videos_compressed']
    # That would mean we are actually losing space!
    assert cv.stats['uncompressed_space'] > cv.stats['compressed_space']
    assert cv.stats['total_videos_ignored'] == 1
    # Size below that is pretty much impossible - means there is something wrong!
    assert cv.stats['compressed_space'] > (cv.stats['uncompressed_space'] * 0.03)

    assert set(map(lambda x: x.name, cv.OUTPUT_DIR.glob('*'))) == {
        'video-1533589738.cmp1.mp4', '.cmpignore', 'editing_multiple_lines_router_admin_pt2.webm',
        'VID_20210407_014635.cmp1.mp4', 'VID_20191230_215442.mp4', '89122489_891195301331652_5070170126553186304_n.jpg',
        'some_random_empty.txt', '2ANsayp.png', 'signal-2022-03-12-203337_023.jpeg', 'IMG_20220729_162347.jpg'
    }
    assert set(map(lambda x: x.name, cv.ORIGINALS_DIR.glob('*'))) == {
        'video-1533589738.mp4', 'VID_20210407_014635.mp4'
    }
    for filename in datetimes:
        file = cv.OUTPUT_DIR / Path(filename).name
        if not file.exists():
            # If it doesn't exist then it was compressed. Very good! But check it!
            file = file.with_stem(file.stem + "." + cv.EXTENSION_NAMESPACES["h265_720p_30fps"])
        assert file.stat().st_mtime == datetimes[filename]
