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
