from pathlib import Path

def find_modules(base_path='app'):
    modules = []
    for py_file in Path(base_path).rglob('*.py'):
        if py_file.name == '__init__.py':
            module = str(py_file.parent).replace('/', '.')
        else:
            module = str(py_file.with_suffix('')).replace('/', '.')
        modules.append(module)
    return sorted(set(modules))

if __name__ == '__main__':
    for mod in find_modules():
        print(f"        '{mod}',")