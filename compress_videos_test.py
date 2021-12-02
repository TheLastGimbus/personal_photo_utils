def test_get_ffmpeg_dimens():
    from compress_videos import get_ffmpeg_dimens
    assert get_ffmpeg_dimens((2137, 6969), 720) == "scale=720:-2"
    assert get_ffmpeg_dimens((1080, 720), 720) == "scale=-2:720"
    assert get_ffmpeg_dimens((1080, 720), 1080) == "scale=-2:720"
    assert get_ffmpeg_dimens((10, 30), 720) == "scale=10:-2"


def test_is_ignored():
    from pathlib import Path
    from compress_videos import is_ignored
    globs = [
        "final.mp4",
        "video*.mp4",
        "*.webm",
    ]
    _ignored = lambda fname: is_ignored(Path(fname), globs)
    assert _ignored("test.mp4") == False
    assert _ignored("final.mp4") == True
    assert _ignored("video_2137.mp4") == True
    assert _ignored("video_2137.webm") == True
    assert _ignored("video_2137.mkv") == False


def test_main():
    import compress_videos as cv
    from pathlib import Path

    from __personal_photo_utils_test_data__.set_datetimes import set_datetimes
    with open('__personal_photo_utils_test_data__/datetimes.json', 'r') as f:
        import json
        datetimes = json.load(f)
        set_datetimes(datetimes, Path('__personal_photo_utils_test_data__/DCIM/Camera'))

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
    assert cv.stats['uncompressed_space'] - cv.stats['compressed_space'] > 0
    assert cv.stats['total_videos_ignored'] == 1

    assert set(map(lambda x: x.name, cv.OUTPUT_DIR.glob('*'))) == {
        'video-1533589738.cmp1.mp4', '.cmpignore', 'editing_multiple_lines_router_admin_pt2.webm',
        'VID_20210407_014635.cmp1.mp4', 'VID_20191230_215442.mp4', '89122489_891195301331652_5070170126553186304_n.jpg',
        'some_random_empty.txt', '2ANsayp.png'
    }
    assert set(map(lambda x: x.name, cv.ORIGINALS_DIR.glob('*'))) == {
        'video-1533589738.mp4', 'VID_20210407_014635.mp4'
    }
    for filename in datetimes:
        file = cv.OUTPUT_DIR / filename
        if not file.exists():
            # If it doesn't exist then it was compressed. Very good! But check it!
            file = file.with_stem(file.stem + "." + cv.EXTENSION_NAMESPACES["h265_720p_30fps"])
        assert file.stat().st_mtime == datetimes[filename]
