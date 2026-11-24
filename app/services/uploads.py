"""Safe file uploads for the admin panel."""
import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

KINDS = {
    "model": {"dir": "models", "ext": {".glb", ".gltf"}, "max": 50 * 1024 * 1024},
    "image": {"dir": "images", "ext": {".jpg", ".jpeg", ".png", ".webp"}, "max": 5 * 1024 * 1024},
    "audio": {"dir": "audio", "ext": {".mp3", ".ogg", ".wav", ".m4a"}, "max": 20 * 1024 * 1024},
}


class UploadError(ValueError):
    pass


def _static_root():
    return os.path.join(current_app.root_path, "static")


def save_upload(file, kind):
    """Save an uploaded FileStorage; return the path relative to static/ (or None if no file was chosen)."""
    if file is None or not file.filename:
        return None
    spec = KINDS[kind]
    name = secure_filename(file.filename)
    ext = os.path.splitext(name)[1].lower()
    if ext not in spec["ext"]:
        raise UploadError(f"{name}: allowed types are {', '.join(sorted(spec['ext']))}")
    stem = os.path.splitext(name)[0][:60] or "file"
    rel = f"{spec['dir']}/{uuid.uuid4().hex[:8]}_{stem}{ext}"
    dest = os.path.join(_static_root(), rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    file.save(dest)
    if os.path.getsize(dest) > spec["max"]:
        os.remove(dest)
        raise UploadError(f"{name} is larger than {spec['max'] // (1024 * 1024)} MB")
    return rel


def delete_upload(rel_path):
    """Delete a previously uploaded file if no destination or hotspot still uses it."""
    from ..models import Destination, Hotspot
    if not rel_path:
        return
    used = (Destination.query.filter((Destination.thumbnail == rel_path) | (Destination.hero_image == rel_path)
                                      | (Destination.model_path == rel_path)).count()
            + Hotspot.query.filter((Hotspot.image_path == rel_path) | (Hotspot.audio_path == rel_path)).count())
    if used:
        return
    full = os.path.abspath(os.path.join(_static_root(), rel_path))
    if full.startswith(os.path.abspath(_static_root())) and os.path.isfile(full):
        # only remove admin uploads (uuid-prefixed), never the bundled seed assets
        base = os.path.basename(full)
        if len(base) > 9 and base[8] == "_":
            os.remove(full)
