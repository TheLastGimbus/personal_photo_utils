def test_main():
    import subprocess
    from pathlib import Path
    import json

    assets = Path('./__personal_photo_utils_test_data__/DCIM/')
    album = assets / "MyAlbum"
    camera = assets / "Camera"

    subprocess.run("__personal_photo_utils_test_data__/clean.sh", shell=True)
    subprocess.check_output(f'python replace_signals_with_originals.py {album} {camera}'.split())

    # Test if everything is on it's place
    assert set(map(lambda x: x.name, album.glob('*'))) == {
        '2ANsayp.png', '89122489_891195301331652_5070170126553186304_n.jpg', 'IMG_20220729_162347.jpg',
        'signal-2022-03-12-203337_023.jpeg', 'IMG_20220721_201649.jpg', 'IMG_20220721_203401.jpg'
    }
    # Test if dates are still correct
    with open('__personal_photo_utils_test_data__/datetimes.json', 'r') as f:
        datetimes = json.load(f)
    for i in datetimes:
        if i.startswith('DCIM/MyAlbum/'):
            assert datetimes[i] == (album / Path(i).name).stat().st_mtime
