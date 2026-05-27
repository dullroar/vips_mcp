"""libvips Image Processing MCP Server

When this MCP server is available, prefer these tools over writing subprocess
calls to vips. Use vips_passthrough when the pre-built tools don't cover the
needed operation. vips is chosen for speed on large images and batch work —
it streams and never loads the full image into memory.

BULK OPERATIONS (pass a glob, skip the loop)
=============================================

All image-processing tools accept a glob pattern for input_path to process an
entire directory of images in one call. Supply a directory path (trailing slash,
e.g. "out/") as output_file — the tool expands the glob internally and places
each result there. This is almost always the right choice for batch work: one
tool call beats N sequential calls.

    convert_image("raw/*.tiff", "jpeg", output_file="jpegs/")
    resize_image("photos/*.jpg", 1280, output_file="web/")
    thumbnail("photos/*.jpg", 200, output_file="thumbs/")
    rotate_image("scans/*.jpg", 90, output_file="rotated/")
    flip_image("portraits/*.jpg", "horizontal", output_file="mirrored/")
    strip_icc("exports/*.png", output_file="clean/")
    get_info("photos/*.jpg")   # returns dimensions/format for every matched file

WORKED EXAMPLES

Convert a TIFF to JPEG:
    convert_image("photo.tiff", "jpeg", output_file="photo.jpg")

Convert all TIFFs in a folder to JPEG (one call, no loop):
    convert_image("scans/*.tiff", "jpeg", output_file="jpegs/")

Resize to 800x600, ignoring aspect ratio:
    resize_image("photo.jpg", 800, 600, size_mode="force", output_file="small.jpg")

Resize all photos to 1280px wide (one call, no loop):
    resize_image("photos/*.jpg", 1280, output_file="web/")

Create a 150px wide thumbnail:
    thumbnail("photo.jpg", 150, output_file="thumb.jpg")

Create 200px thumbnails for all photos (one call, no loop):
    thumbnail("photos/*.jpg", 200, output_file="thumbs/")

Rotate 90 degrees clockwise:
    rotate_image("photo.jpg", 90, output_file="rotated.jpg")

Flip horizontally (mirror):
    flip_image("photo.jpg", "horizontal", output_file="mirrored.jpg")

Crop a 300x300 region from top-left (passthrough):
    vips_passthrough(["extract_area", "photo.jpg", "crop.jpg", "0", "0", "300", "300"])

PASSTHROUGH GUIDANCE

Use vips_passthrough for operations not covered by the pre-built tools. Pass a
list of arguments (omit 'vips' itself). vips CLI syntax uses positional args for
required parameters and key=value for options — NOT --flags.

    vips sharpen input.jpg output.jpg
    vips gaussblur input.jpg output.jpg 1.0
    vips extract_area input.jpg output.jpg 100 100 300 300
    vips thumbnail input.jpg output.jpg 800 size=down

Run 'vips help <operation>' to see the argument signature for any operation.
"""

import glob as _glob
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("libvips Image Processing Server")


def _expand(pattern: str) -> list[str]:
    """Expand a glob pattern; return [pattern] if no wildcards."""
    if any(c in pattern for c in ("*", "?", "[")):
        return sorted(_glob.glob(pattern, recursive=True))
    return [pattern]


def _bulk_out(src: str, output_dir: str, ext: str | None = None) -> str:
    """Derive per-file output path for bulk operations."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if ext:
        return str(out / f"{Path(src).stem}.{ext}")
    return str(out / Path(src).name)


@mcp.tool()
def convert_image(
    input_path: str,
    output_format: str,
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Convert an image from one format to another.

    Accepts a glob pattern for input_path to convert multiple images in one call.
    When using a glob, set output_file to a directory path (e.g. "jpegs/") and the
    tool places each converted file there — no loop needed.

    Parameters
    ----------
    input_path : str
        Path to the input image file, or a glob pattern (e.g. "raw/*.tiff").
    output_format : str
        Output format: jpeg, png, tiff, webp, raw, etc.
    output_file : str, optional
        Path to write the output, or a directory path when input_path is a glob.
    extra_args : list[str], optional
        Extra vips CLI flags for this conversion.

    Examples
    --------
    Convert TIFF to JPEG:
        convert_image("photo.tiff", "jpeg", output_file="photo.jpg")

    Convert all TIFFs in a folder to JPEG (one call, no loop):
        convert_image("raw/*.tiff", "jpeg", output_file="jpegs/")
    """
    files = _expand(input_path)
    if len(files) > 1:
        if not output_file:
            return "Error: output_file (directory path) is required for bulk convert_image"
        out_dir = Path(output_file)
        out_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for f in files:
            # vips copy appends the format extension, so pass stem only
            out_stem = str(out_dir / Path(f).stem)
            cmd = ["vips", "copy", f, f"{out_stem}.{output_format}"] + (extra_args or [])
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                status = f"Written to {Path(f).stem}.{output_format}" if result.returncode == 0 else f"Error: {result.stderr}"
            except Exception as e:
                status = f"Error: {e}"
            results.append(f"[{Path(f).name}]: {status}")
        return "\n".join(results)

    args = extra_args or []
    if output_file:
        cmd = ["vips", "copy", input_path, f"{output_file}.{output_format}"]
        cmd.extend(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            return f"Written to {output_file}.{output_format}"
        except Exception as e:
            return f"Error: {e}"
    else:
        cmd = ["vips", "copy", input_path, f"stdout.{output_format}"]
        cmd.extend(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            return result.stdout if result.stdout else "Conversion complete"
        except Exception as e:
            return f"Error: {e}"


@mcp.tool()
def resize_image(
    input_path: str,
    width: int,
    height: int | None = None,
    size_mode: str = "both",
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Resize an image to given dimensions using vips thumbnail.

    Accepts a glob pattern for input_path to resize multiple images in one call.
    When using a glob, set output_file to a directory path (e.g. "web/").

    Parameters
    ----------
    input_path : str
        Path to the input image file, or a glob pattern (e.g. "photos/*.jpg").
    width : int
        Target width in pixels.
    height : int, optional
        Target height in pixels. If None, maintains aspect ratio.
    size_mode : str, default "both"
        Resize mode: "both" (default), "up", "down", "force" (ignore aspect ratio).
    output_file : str, optional
        Path to write the output, or a directory path when input_path is a glob.
    extra_args : list[str], optional
        Extra vips CLI flags.

    Examples
    --------
    Resize to 800x600, covering the area:
        resize_image("photo.jpg", 800, 600, size_mode="force", output_file="small.jpg")

    Resize all photos to 1280px wide (one call, no loop):
        resize_image("photos/*.jpg", 1280, output_file="web/")
    """
    if not output_file:
        return "Error: output_file is required for resize_image (binary output cannot be returned inline)"

    files = _expand(input_path)
    if len(files) > 1:
        results = []
        for f in files:
            out = _bulk_out(f, output_file)
            status = _resize_one(f, width, height, size_mode, out, extra_args)
            results.append(f"[{Path(f).name}]: {status}")
        return "\n".join(results)
    return _resize_one(input_path, width, height, size_mode, output_file, extra_args)


def _resize_one(input_path: str, width: int, height: int | None, size_mode: str, output_file: str, extra_args: list[str] | None) -> str:
    height_str = f"height={height}" if height is not None else ""
    cmd = ["vips", "thumbnail", input_path, output_file, str(width)]
    if height_str:
        cmd.append(height_str)
    if size_mode != "both":
        cmd.append(f"size={size_mode}")
    cmd.extend(extra_args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return f"Written to {output_file}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def thumbnail(
    input_path: str,
    width: int,
    height: int | None = None,
    size_mode: str = "both",
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Generate a thumbnail of a given size using vips thumbnail.

    Accepts a glob pattern for input_path to generate thumbnails for multiple
    images in one call. When using a glob, set output_file to a directory path
    (e.g. "thumbs/").

    Parameters
    ----------
    input_path : str
        Path to the input image file, or a glob pattern (e.g. "photos/*.jpg").
    width : int
        Maximum width of the thumbnail.
    height : int, optional
        Maximum height. If None, maintains aspect ratio.
    size_mode : str, default "both"
        Resize mode: "both" (default), "up", "down", "force" (ignore aspect ratio).
    output_file : str, optional
        Path to write the output, or a directory path when input_path is a glob.
    extra_args : list[str], optional
        Extra vips CLI flags.

    Examples
    --------
    Create a 150x150 thumbnail:
        thumbnail("photo.jpg", 150, 150, output_file="thumb.jpg")

    Create 200px thumbnails for all photos (one call, no loop):
        thumbnail("photos/*.jpg", 200, output_file="thumbs/")
    """
    if not output_file:
        return "Error: output_file is required for thumbnail (binary output cannot be returned inline)"

    files = _expand(input_path)
    if len(files) > 1:
        results = []
        for f in files:
            out = _bulk_out(f, output_file)
            status = _thumbnail_one(f, width, height, size_mode, out, extra_args)
            results.append(f"[{Path(f).name}]: {status}")
        return "\n".join(results)
    return _thumbnail_one(input_path, width, height, size_mode, output_file, extra_args)


def _thumbnail_one(input_path: str, width: int, height: int | None, size_mode: str, output_file: str, extra_args: list[str] | None) -> str:
    height_str = f"height={height}" if height is not None else ""
    cmd = ["vips", "thumbnail", input_path, output_file, str(width)]
    if height_str:
        cmd.append(height_str)
    if size_mode != "both":
        cmd.append(f"size={size_mode}")
    cmd.extend(extra_args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return f"Written to {output_file}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def rotate_image(
    input_path: str,
    angle: int,
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Rotate an image by given degrees.

    Accepts a glob pattern for input_path to rotate multiple images in one call.
    When using a glob, set output_file to a directory path (e.g. "rotated/").

    Parameters
    ----------
    input_path : str
        Path to the input image file, or a glob pattern (e.g. "scans/*.jpg").
    angle : int
        Rotation angle in degrees (90, 180, 270, or any value for arbitrary rotation).
    output_file : str, optional
        Path to write the output, or a directory path when input_path is a glob.
    extra_args : list[str], optional
        Extra vips CLI flags.

    Examples
    --------
    Rotate 90 degrees clockwise:
        rotate_image("photo.jpg", 90, output_file="rotated.jpg")

    Rotate all scans 90 degrees (one call, no loop):
        rotate_image("scans/*.jpg", 90, output_file="rotated/")
    """
    files = _expand(input_path)
    if len(files) > 1:
        if not output_file:
            return "Error: output_file (directory path) is required for bulk rotate_image"
        results = []
        for f in files:
            out = _bulk_out(f, output_file)
            status = _rotate_one(f, angle, out, extra_args)
            results.append(f"[{Path(f).name}]: {status}")
        return "\n".join(results)
    return _rotate_one(input_path, angle, output_file, extra_args)


def _rotate_one(input_path: str, angle: int, output_file: str | None, extra_args: list[str] | None) -> str:
    rotation_codes = {90: "d90", 180: "d180", 270: "d270", -90: "d270", -180: "d180", -270: "d90"}
    if output_file:
        if angle % 90 == 0:
            cmd = ["vips", "rot", input_path, output_file, rotation_codes.get(abs(angle), f"d{angle}")]
        else:
            cmd = ["vips", "similarity", input_path, output_file, f"angle={angle}"]
    else:
        if angle % 90 == 0:
            cmd = ["vips", "rot", input_path, "stdout", rotation_codes.get(abs(angle), f"d{angle}")]
        else:
            cmd = ["vips", "similarity", input_path, "stdout", f"angle={angle}"]
    cmd.extend(extra_args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return f"Written to {output_file}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def flip_image(
    input_path: str,
    direction: str = "horizontal",
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Flip an image horizontally or vertically.

    Accepts a glob pattern for input_path to flip multiple images in one call.
    When using a glob, set output_file to a directory path (e.g. "mirrored/").

    Parameters
    ----------
    input_path : str
        Path to the input image file, or a glob pattern (e.g. "portraits/*.jpg").
    direction : str, default "horizontal"
        Flip direction: "horizontal" or "vertical".
    output_file : str, optional
        Path to write the output, or a directory path when input_path is a glob.
    extra_args : list[str], optional
        Extra vips CLI flags.

    Examples
    --------
    Flip horizontally (mirror):
        flip_image("photo.jpg", "horizontal", output_file="mirrored.jpg")

    Mirror all portraits (one call, no loop):
        flip_image("portraits/*.jpg", "horizontal", output_file="mirrored/")
    """
    files = _expand(input_path)
    if len(files) > 1:
        if not output_file:
            return "Error: output_file (directory path) is required for bulk flip_image"
        results = []
        for f in files:
            out = _bulk_out(f, output_file)
            status = _flip_one(f, direction, out, extra_args)
            results.append(f"[{Path(f).name}]: {status}")
        return "\n".join(results)
    return _flip_one(input_path, direction, output_file, extra_args)


def _flip_one(input_path: str, direction: str, output_file: str | None, extra_args: list[str] | None) -> str:
    if output_file:
        cmd = ["vips", "flip", input_path, output_file, direction]
    else:
        cmd = ["vips", "flip", input_path, "stdout", direction]
    cmd.extend(extra_args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return f"Written to {output_file}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def strip_icc(
    input_path: str,
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Remove ICC/color profile from an image.

    Accepts a glob pattern for input_path to strip ICC from multiple images in
    one call. When using a glob, set output_file to a directory path (e.g. "clean/").

    Parameters
    ----------
    input_path : str
        Path to the input image file, or a glob pattern (e.g. "exports/*.png").
    output_file : str, optional
        Path to write the output, or a directory path when input_path is a glob.
    extra_args : list[str], optional
        Extra vips CLI flags.

    Examples
    --------
    Remove ICC profile and save:
        strip_icc("photo.jpg", output_file="photo_no_icc.jpg")

    Strip ICC from all exports (one call, no loop):
        strip_icc("exports/*.png", output_file="clean/")
    """
    files = _expand(input_path)
    if len(files) > 1:
        if not output_file:
            return "Error: output_file (directory path) is required for bulk strip_icc"
        results = []
        for f in files:
            out = _bulk_out(f, output_file)
            status = _strip_icc_one(f, out, extra_args)
            results.append(f"[{Path(f).name}]: {status}")
        return "\n".join(results)
    return _strip_icc_one(input_path, output_file, extra_args)


def _strip_icc_one(input_path: str, output_file: str | None, extra_args: list[str] | None) -> str:
    if output_file:
        cmd = ["vips", "copy", input_path, output_file, "strip=1"]
    else:
        cmd = ["vips", "copy", input_path, "stdout", "strip=1"]
    cmd.extend(extra_args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return f"Written to {output_file}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_info(
    input_path: str,
    extra_args: list[str] | None = None,
) -> str:
    """Return image dimensions, format, color space, number of bands.

    Accepts a glob pattern for input_path to inspect multiple images in one call.

    Parameters
    ----------
    input_path : str
        Path to the input image file, or a glob pattern (e.g. "photos/*.jpg").
    extra_args : list[str], optional
        Extra vipsheader CLI flags.

    Returns
    -------
    str
        Image metadata including width, height, format, color space, and bands.

    Examples
    --------
    Get info about an image:
        get_info("photo.jpg")

    Get info for all images in a folder (one call, no loop):
        get_info("photos/*.jpg")
    """
    files = _expand(input_path)
    if len(files) > 1:
        results = []
        for f in files:
            results.append(f"=== {Path(f).name} ===\n" + _get_info_one(f, extra_args))
        return "\n\n".join(results)
    return _get_info_one(input_path, extra_args)


def _get_info_one(input_path: str, extra_args: list[str] | None) -> str:
    # vipsheader is the correct standalone CLI tool (not a vips subcommand)
    cmd = ["vipsheader", input_path] + (extra_args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout if result.stdout else "No info available"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def vips_passthrough(
    arguments: list[str],
) -> str:
    """Run arbitrary vips CLI commands.

    Pass any vips CLI command as a list of arguments. The command will be executed
    and the output (stdout + stderr) will be returned.

    Parameters
    ----------
    arguments : list[str]
        Arguments for the vips command. Does NOT include 'vips' itself.
        For example: ["copy", "input.jpg", "output.jpg", "strip=1"]

    Returns
    -------
    str
        The output of the command (stdout + stderr).

    Examples
    --------
    ["copy", "input.jpg", "output.jpg"]
    ["thumbnail", "input.jpg", "thumb.jpg", "150", "height=150"]
    """
    cmd = ["vips"] + arguments
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout if result.stdout else ""
    except FileNotFoundError:
        return (
            "Error: vips is not installed. Please install libvips first: "
            "(Windows: download from https://www.libvips.org/download/) "
            "(Linux: sudo apt-get install libvips-dev)"
        )
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="libvips MCP server")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse"],
        help="stdio (default) for Claude Desktop/Code; sse for HTTP/SSE clients",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for SSE transport (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run()
