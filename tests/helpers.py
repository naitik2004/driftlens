from pathlib import Path
import subprocess
import tempfile


class Repository:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'DriftLens Test')
        self.git('config', 'user.email', 'test@example.invalid')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.path), *args], stderr=subprocess.PIPE).decode().strip()

    def commit(self, files):
        for path, content in files.items():
            target = self.path / path
            if content is None:
                target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
        self.git('add', '-A')
        self.git('commit', '-qm', 'fixture', '--allow-empty')
        return self.git('rev-parse', 'HEAD')

    def close(self):
        self.tmp.cleanup()
