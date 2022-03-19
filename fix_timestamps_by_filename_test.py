def test_main():
    from unittest import mock
    import sys
    from datetime import datetime
    with mock.patch.object(sys, 'argv', ['', 'signal', '-p', './__personal_photo_utils_test_data__/DCIM/Camera']):
        from pathlib import Path
        import fix_timestamps_by_filename as fix
        fix.main()
        assert ((Path(fix.args.path) / 'signal-2022-03-12-203337_023.jpeg').stat().st_mtime ==
                datetime(2022, 3, 12, 20, 33, 37).timestamp())
