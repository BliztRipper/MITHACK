"""Curated demo photos and their credits (live-demo-deployment D3). Public: licensed images, no patient data."""
import functools
import pathlib

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

DIR = pathlib.Path(__file__).resolve().parents[1] / "demo_cache"  # fixed: tests swap analysis.CACHE
router = APIRouter(tags=["demo"])


@functools.cache
def manifest() -> dict:
    """name -> {name, label, source, licence}, from the table in demo_cache/SOURCES.md (the one credits list)."""
    rows = [line.strip("| ").split(" | ") for line in (DIR / "SOURCES.md").read_text().splitlines()
            if line.startswith("| ") and line.split(" | ")[0][2:].endswith((".png", ".jpg"))]
    return {r[0]: {"name": r[0], "label": r[2], "source": r[3], "licence": r[4]} for r in rows}


@router.get("/demo-images")
def demo_images():
    return list(manifest().values())


@router.get("/demo-images/{name}")
def demo_image(name: str):
    if name not in manifest():  # exact-name allow-list: the name never becomes part of a path unchecked
        raise HTTPException(404, "not a demo image")
    path = DIR / "images" / name
    if not path.is_file():
        raise HTTPException(404, "demo image not installed")
    return FileResponse(path)
