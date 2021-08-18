from pathlib import Path
from sys import argv


def traverse(path: Path):
    try:
        if path.is_dir():
            for obj in path.iterdir():
                traverse(obj)
            if len(list(path.iterdir())) == 0:
                print(f'Removing: {path}')
                path.rmdir()
        elif path.stat().st_size == 0:
            print(f'Deleting: {path}')
            path.unlink()
    except PermissionError:
        print(f'Could not access: {path}')


print(argv)

[_, root_path] = argv

traverse(Path(root_path))
