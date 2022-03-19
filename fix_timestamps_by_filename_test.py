def test_main():
    from unittest import mock
    import sys
    with mock.patch.object(sys, 'argv', ['', 'signal', '-p', './__personal_photo_utils_test_data__/DCIM/Camera']):
        from pathlib import Path
        import fix_timestamps_by_filename as fix
        fix.main()
        assert ((Path(fix.args.path) / 'signal-2022-03-12-203337_023.jpeg').stat().st_mtime == 1647113617)
