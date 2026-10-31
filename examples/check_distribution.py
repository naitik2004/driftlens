"""Install a wheel into a clean temporary venv and test it on any supported OS."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import venv


def check(directory):
    wheels = list(directory.resolve().glob('*.whl'))
    if len(wheels) != 1:
        raise ValueError('Expected exactly one wheel in the distribution directory')
    verifier = Path(__file__).resolve().with_name('verify_install.py')
    with tempfile.TemporaryDirectory(prefix='driftlens-wheel-check-') as tmp:
        root = Path(tmp)
        environment = root / 'venv'
        venv.EnvBuilder(with_pip=True).create(environment)
        scripts = environment / ('Scripts' if os.name == 'nt' else 'bin')
        python = scripts / ('python.exe' if os.name == 'nt' else 'python')
        executable = scripts / ('driftlens.exe' if os.name == 'nt' else 'driftlens')

        def run(*args):
            subprocess.run([str(arg) for arg in args], cwd=root, check=True, timeout=180)

        run(python, '-m', 'pip', 'install', '--no-index', '--no-deps', wheels[0])
        run(python, '-m', 'pip', 'check')
        run(executable, '--help')
        run(python, '-I', verifier)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    check(args.dist)
