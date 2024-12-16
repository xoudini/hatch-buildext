import pathlib


def test_dirs(
    project_dir: pathlib.Path,
    build_dir: pathlib.Path,
    tmp_dir: pathlib.Path,
) -> None:
    assert project_dir.exists()
    assert build_dir.exists()
    assert tmp_dir.exists()
