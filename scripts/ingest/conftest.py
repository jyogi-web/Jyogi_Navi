import sys
from pathlib import Path


def pytest_collect_file(parent, file_path):
    """テストファイル収集直前に正しいパッケージルートを sys.path の先頭に配置する。

    discord/ と notion/ に同名の normalize.py が存在するため、
    各テストファイルが import される前に sys.modules のキャッシュを無効化し、
    そのファイルが属するパッケージのルートを sys.path[0] に配置する。
    """
    if file_path.name.startswith("test_") and file_path.suffix == ".py":
        package_root = str(file_path.parent.parent)
        # normalize モジュールとテストモジュール自身のキャッシュを除去する
        sys.modules.pop("normalize", None)
        sys.modules.pop(file_path.stem, None)  # e.g. "test_normalize"
        if package_root in sys.path:
            sys.path.remove(package_root)
        sys.path.insert(0, package_root)
    return None
