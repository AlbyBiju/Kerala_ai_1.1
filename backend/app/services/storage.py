import os
import uuid
from typing import Optional

from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

ALLOWED_MIME_TYPES = {
    "application/pdf", "image/png", "image/jpeg", "image/tiff",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msword", "application/vnd.ms-excel", "application/octet-stream"
}
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".docx", ".xlsx"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024
MAGIC_SIGNATURES: list[tuple[bytes, str]] = [
    (b"%PDF", "application/pdf"), (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"), (b"II*\x00", "image/tiff"),
    (b"MM\x00*", "image/tiff"), (b"PK\x03\x04", "zip_archive")
]


def detect_content_type(content: bytes) -> Optional[str]:
    for signature, label in MAGIC_SIGNATURES:
        if content.startswith(signature):
            return label
    return None


class StorageService:
    def __init__(self, base_dir: str = settings.UPLOAD_DIR):
        self.base_dir = base_dir
        if settings.STORAGE_BACKEND.lower() == "local":
            os.makedirs(self.base_dir, exist_ok=True)

    def _validate(self, filename: str, content: bytes, content_type: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="File exceeds maximum allowed size of 20 MB")
        if content_type not in ALLOWED_MIME_TYPES and ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Invalid MIME type or file format: {content_type}")
        detected = detect_content_type(content)
        is_office = ext in {".docx", ".xlsx"} or "openxmlformats" in content_type
        if content and ((is_office and detected != "zip_archive") or (not is_office and detected is None)):
            raise HTTPException(status_code=400, detail="File content does not match a supported document format")
        if content and (ext == ".pdf" or content_type == "application/pdf") and detected != "application/pdf":
            raise HTTPException(status_code=400, detail="File content is not a valid PDF")
        return ext

    async def save_file(self, file: UploadFile) -> tuple[str, str, int]:
        filename = file.filename or "unknown"
        content = await file.read()
        content_type = file.content_type or "application/octet-stream"
        ext = self._validate(filename, content, content_type)
        unique_filename = f"{uuid.uuid4()}{ext}"

        if settings.STORAGE_BACKEND.lower() == "supabase":
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                raise HTTPException(status_code=503, detail="Supabase Storage is not configured")
            try:
                from supabase import create_client
                client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
                client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
                    unique_filename, content, {"content-type": content_type, "upsert": "false"}
                )
                return f"supabase://{settings.SUPABASE_STORAGE_BUCKET}/{unique_filename}", content_type, len(content)
            except Exception as exc:
                raise HTTPException(status_code=502, detail=f"Supabase Storage upload failed: {exc}") from exc

        target_path = os.path.join(self.base_dir, unique_filename)
        with open(target_path, "wb") as output:
            output.write(content)
        return target_path, content_type, len(content)

    def materialize(self, file_path: str) -> str:
        """Return a local path for parsers, downloading Supabase objects when needed."""
        if not file_path.startswith("supabase://"):
            return file_path
        _, bucket, object_path = file_path.split("/", 2)
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError("Supabase Storage is not configured")
        from supabase import create_client
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        content = client.storage.from_(bucket).download(object_path)
        local_path = os.path.join(self.base_dir, f"processing-{uuid.uuid4()}{os.path.splitext(object_path)[1]}")
        with open(local_path, "wb") as output:
            output.write(content)
        return local_path

        if file_path.startswith("supabase://"):
            return False
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError:
                return False
        return False


storage_service = StorageService()
