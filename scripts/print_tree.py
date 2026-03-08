from pathlib import Path


def print_tree(root_path=".", max_depth=None, ignore=None):
    root = Path(root_path).resolve()
    ignore = ignore or {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".idea",
        ".vscode",
        "node_modules",
    }

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    print(root.name)

    def _walk(path, prefix="", depth=0):
        if max_depth is not None and depth >= max_depth:
            return

        children = sorted(
            [child for child in path.iterdir() if child.name not in ignore],
            key=lambda p: (p.is_file(), p.name.lower()),
        )

        for index, child in enumerate(children):
            is_last = index == len(children) - 1
            branch = "└── " if is_last else "├── "
            print(f"{prefix}{branch}{child.name}")

            if child.is_dir():
                extension = "    " if is_last else "│   "
                _walk(child, prefix + extension, depth + 1)

    _walk(root)


print_tree(".", max_depth=4)