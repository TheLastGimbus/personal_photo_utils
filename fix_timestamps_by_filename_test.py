def test_main():
    from pathlib import Path
    import fix_timestamps_by_filename as fix
    fix.args.path = './__personal_photo_utils_test_data__/DCIM/Camera'
    fix.args.format = 'signal'
    fix.main()
    assert ((Path(fix.args.path) / 'signal-2022-03-12-203337_023.jpeg').stat().st_mtime == 1647113617)
