"""libvips Image Processing MCP Server

When this MCP server is available, prefer these tools over writing subprocess
calls to vips. Use vips_passthrough when the pre-built tools don't cover the
needed operation. vips is chosen for speed on large images and batch work —
it streams and never loads the full image into memory.

WORKED EXAMPLES

Convert a TIFF to JPEG:
    convert_image("photo.tiff", "jpeg", output_file="photo.jpg")

Resize to 800x600, ignoring aspect ratio:
    resize_image("photo.jpg", 800, 600, size_mode="force", output_file="small.jpg")

Create a 150px wide thumbnail:
    thumbnail("photo.jpg", 150, output_file="thumb.jpg")

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

import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("libvips Image Processing Server")


@mcp.tool()
def convert_image(
    input_path: str,
    output_format: str,
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Convert an image from one format to another.
    
    Converts images between various formats (TIFF, JPEG, PNG, RAW, WebP, etc.)
    using libvips.
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    output_format : str
        Output format (e.g., 'jpeg', 'png', 'tiff', 'webp', 'raw', etc.).
    output_file : str, optional
        Path to write the output. If omitted, returns the content.
    extra_args : list[str], optional
        Extra vips CLI flags for this conversion. See vips help for options.
    
    Examples
    --------
    Convert TIFF to JPEG:
        convert_image("photo.tiff", "jpeg", output_file="photo.jpg")
    
    Convert RAW to PNG:
        convert_image("photo.raw", "png", output_file="photo.png")
    """
    args = extra_args or []
    
    if output_file:
        # Format conversion done by file extension on output path
        cmd = ["vips", "copy", input_path, f"{output_file}.{output_format}"]
        
        cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            return f"Written to {output_file}.{output_format}"
        except Exception as e:
            return f"Error: {e}"
    else:
        cmd = ["vips", "copy", input_path, f"stdout.{output_format}"]
        cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
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
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    width : int
        Target width in pixels.
    height : int, optional
        Target height in pixels. If None, maintains aspect ratio.
    size_mode : str, default "both"
        Resize mode: "both" (default), "up", "down", "force" (ignore aspect ratio).
    output_file : str, optional
        Path to write the output. If omitted, returns the content.
    extra_args : list[str], optional
        Extra vips CLI flags.
    
    Examples
    --------
    Resize to 800x600, covering the area:
        resize_image("photo.jpg", 800, 600, size_mode="force", output_file="small.jpg")
    
    Resize maintaining aspect ratio:
        resize_image("photo.jpg", 800, size_mode="both", output_file="small.jpg")
    """
    if height is None:
        height_str = ""
    else:
        height_str = f"height={height}"
    
    if not output_file:
        return "Error: output_file is required for resize_image (binary output cannot be returned inline)"

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
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    width : int
        Maximum width of the thumbnail.
    height : int, optional
        Maximum height of the thumbnail. If None, maintains aspect ratio.
    size_mode : str, default "both"
        Resize mode: "both" (default), "up", "down", "force" (ignore aspect ratio).
    output_file : str, optional
        Path to write the output. If omitted, returns the content.
    extra_args : list[str], optional
        Extra vips CLI flags.
    
    Examples
    --------
    Create a 150x150 thumbnail:
        thumbnail("photo.jpg", 150, 150, output_file="thumb.jpg")
    
    Create a 200px wide thumbnail maintaining aspect ratio:
        thumbnail("photo.jpg", 200, output_file="thumb.jpg")
    """
    if height is None:
        height_str = ""
    else:
        height_str = f"height={height}"
    
    if not output_file:
        return "Error: output_file is required for thumbnail (binary output cannot be returned inline)"

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
    
    For multiples of 90, use vips rot with d90, d180, d270.
    For arbitrary angles, use vips similarity with angle=X.
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    angle : int
        Rotation angle in degrees (90, 180, 270, or any value for arbitrary rotation).
    output_file : str, optional
        Path to write the output. If omitted, returns the content.
    extra_args : list[str], optional
        Extra vips CLI flags.
    
    Examples
    --------
    Rotate 90 degrees clockwise:
        rotate_image("photo.jpg", 90, output_file="rotated.jpg")
    
    Rotate 180 degrees:
        rotate_image("photo.jpg", 180, output_file="rotated.jpg")
    
    Rotate arbitrary angle (45 degrees):
        rotate_image("photo.jpg", 45, output_file="rotated.jpg")
    """
    if output_file:
        # Multiples of 90 use vips rot: vips rot input.jpg output.jpg d90/d180/d270
        # Arbitrary angles use vips similarity: vips similarity input.jpg output.jpg angle=45
        if angle % 90 == 0:
            # Use rot for multiples of 90
            rotation_codes = {90: "d90", 180: "d180", 270: "d270", -90: "d270", -180: "d180", -270: "d90"}
            cmd = ["vips", "rot", input_path, output_file, rotation_codes.get(abs(angle), f"d{angle}")]
        else:
            # Use similarity for arbitrary angles
            cmd = ["vips", "similarity", input_path, output_file, f"angle={angle}"]
    else:
        if angle % 90 == 0:
            rotation_codes = {90: "d90", 180: "d180", 270: "d270", -90: "d270", -180: "d180", -270: "d90"}
            cmd = ["vips", "rot", input_path, "stdout", rotation_codes.get(abs(angle), f"d{angle}")]
        else:
            cmd = ["vips", "similarity", input_path, "stdout", f"angle={angle}"]
    
    cmd.extend(extra_args or [])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
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
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    direction : str, default "horizontal"
        Flip direction: "horizontal" or "vertical".
    output_file : str, optional
        Path to write the output. If omitted, returns the content.
    extra_args : list[str], optional
        Extra vips CLI flags.
    
    Examples
    --------
    Flip horizontally (mirror):
        flip_image("photo.jpg", "horizontal", output_file="mirrored.jpg")
    
    Flip vertically:
        flip_image("photo.jpg", "vertical", output_file="flipped.jpg")
    """
    # vips flip input.jpg output.jpg horizontal/vertical
    if output_file:
        cmd = ["vips", "flip", input_path, output_file, direction]
    else:
        cmd = ["vips", "flip", input_path, "stdout", direction]
    
    cmd.extend(extra_args or [])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
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
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    output_file : str, optional
        Path to write the output. If omitted, returns the content.
    extra_args : list[str], optional
        Extra vips CLI flags.
    
    Examples
    --------
    Remove ICC profile and save:
        strip_icc("photo.jpg", output_file="photo_no_icc.jpg")
    """
    # vips copy input.jpg output.jpg strip=1
    if output_file:
        cmd = ["vips", "copy", input_path, output_file, "strip=1"]
    else:
        cmd = ["vips", "copy", input_path, "stdout", "strip=1"]
    
    cmd.extend(extra_args or [])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
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
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    extra_args : list[str], optional
        Extra vips CLI flags (e.g., for loading from specific file formats).
    
    Returns
    -------
    str
        Image metadata including width, height, format, color space, and bands.
    
    Examples
    --------
    Get info about an image:
        get_info("photo.jpg")
    """
    # vips header input.jpg
    cmd = ["vips", "header", input_path]
    cmd.extend(extra_args or [])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
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
    ["thumbnail", "input.jpg", "thumb.jpg", 150, "height=150"]
    """
    # Accept list[str] NOT a plain string (to handle paths with spaces)
    cmd = ["vips"] + arguments
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout if result.stdout else ""
    except FileNotFoundError:
        return "Error: vips is not installed. Please install libvips first: " + \
               "(Windows: download from https://www.libvips.org/download/) " + \
               "(Linux: sudo apt-get install libvips-dev)"
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
