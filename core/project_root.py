import os
import json

from pathlib import Path

LOCAL_PROJECT_ROOT_DATA = Path(os.path.dirname(__file__)) / 'project_root.json'
PROJECT_ROOT_DATA = json.loads(LOCAL_PROJECT_ROOT_DATA.read_text())


def find_project_root(path: Path, project_files_to_check=[]) -> Path:
  project_files = set(project_files_to_check)
  project_files.update(PROJECT_ROOT_DATA)

  for file in project_files:
    found = list(path.glob(file))
    if len(found) > 0:
      return path.resolve()

  if path.parent == path:
    return None

  return find_project_root(path.parent, project_files)


if __name__ == '__main__':
  print(find_project_root(Path('.'), PROJECT_ROOT_DATA))
