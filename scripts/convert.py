"""Script to convert a folder of autograders from .1 format to .2 format."""
import shutil
from pathlib import Path
import os

def convert_autograder(folder, backup=True):
    path = Path(folder)
    if backup:
        shutil.copytree(folder, os.path.normpath(folder) + '_backup')
        
    (path / 'configurations').mkdir()
    (path / 'scaffolding').mkdir()
    (path / 'tests').mkdir()
    
    for item in (path / 'autograder'/ 'tests').glob('*'):
        if item.name != '__init__.py': # no need for this
            shutil.copy(item, path / 'tests')

    config_files = ['docstring.cfg', 'flake8.cfg', 'requirements.txt']
    for f in config_files:
        shutil.copy(path / 'autograder' / f, path /'configurations' /f)

    for item in (path / 'autograder').glob('*.py'):
        if item.name != 'run_tests.py': # no need for this
            shutil.copy(item, path / 'scaffolding')

    with open(path / 'config.ini', 'w') as f:
        f.write('[SUBMIT]\n')
        f.write('code: ')
        for item in (path / 'sample').glob('*.py'):
            if not item.name.startswith('test'):
                f.write(item.name + ' ')
        f.write('\ntests: ')
        for item in (path / 'sample').glob('*.py'):
            if item.name.startswith('test'):
                f.write(item.name + ' ')
        f.write('\n')
            

    shutil.rmtree(path / 'autograder')
    
    
        
        
if __name__ == "__main__":
    import sys
    for p in sorted(list(Path(sys.argv[1]).iterdir())):
        if p.is_dir():
             ok = input(f"About to convert {p.name} OK? (Y/n): ")
             if len(ok) == 0 or ok.lower().startswith("y"):
                 convert_autograder(str(p))                 

