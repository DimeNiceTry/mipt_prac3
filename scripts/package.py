import gzip
import hashlib
import io
import tarfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
paths = [root / "requirements.txt", *sorted((root / "app").rglob("*.py"))]
stream = io.BytesIO()
with gzip.GzipFile(fileobj=stream, mode="wb", mtime=0) as compressed:
    with tarfile.open(fileobj=compressed, mode="w") as archive:
        for path in paths:
            data = path.read_bytes()
            info = tarfile.TarInfo(path.relative_to(root).as_posix())
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            archive.addfile(info, io.BytesIO(data))
payload = stream.getvalue()
digest = hashlib.sha256(payload).hexdigest()
output = Path("/tmp/notes.tar.gz")
if not output.exists() or output.read_bytes() != payload:
    output.write_bytes(payload)
print(digest)
