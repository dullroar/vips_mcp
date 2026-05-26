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
        input_path="photo.tiff", output_format="jpeg", output_file="photo.jpg"
    
    Convert RAW to PNG:
        input_path="photo.raw", output_format="png", output_file="photo.png"
    """
    args = extra_args or []
    
    if output_file:
        cmd = ["vips", "resize", input_path, output_file, "--without-giop"]
        # Override output format if needed
        if output_format:
            cmd.extend(["-o", f"{output_file}.{output_format}"])
            cmd = ["vips", "save", input_path, f"{output_file}.{output_format}"]
        else:
            cmd = ["vips", "save", input_path, output_file]
        
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
            return f"Written to {output_file}"
        except Exception as e:
            return f"Error: {e}"
    else:
        cmd = ["vips", "save", input_path, f"stdout.{output_format}"]
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
    fit_mode: str = "cover",
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Resize an image to given dimensions.
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    width : int
        Target width in pixels.
    height : int, optional
        Target height in pixels. If None, maintains aspect ratio.
    fit_mode : str, default "cover"
        Fit mode: "cover" (cover entire area), "contain" (entire image visible),
        "crop" (crop to fit).
    output_file : str, optional
        Path to write the output. If omitted, returns the content.
    extra_args : list[str], optional
        Extra vips CLI flags.
    
    Examples
    --------
    Resize to 800x600, covering the area:
        resize_image("photo.jpg", 800, 600, fit_mode="cover", output_file="small.jpg")
    
    Resize maintaining aspect ratio:
        resize_image("photo.jpg", 800, fit_mode="cover", output_file="small.jpg")
    """
    if height is None:
        # Maintain aspect ratio - use vips resize without height
        height_str = ""
    else:
        height_str = f"{height}"
    
    if output_file:
        if height_str:
            cmd = ["vips", "resize", input_path, output_file, 
                   f"--width={width}", f"--height={height_str}", 
                   f"--fit={fit_mode}"]
        else:
            cmd = ["vips", "resize", input_path, output_file,
                   f"--width={width}", f"--fit={fit_mode}"]
        
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
    else:
        if height_str:
            cmd = ["vips", "resize", input_path, f"stdout.{width}x{height}",
                   f"--fit={fit_mode}"]
        else:
            cmd = ["vips", "resize", input_path, f"stdout.{width}", f"--fit={fit_mode}"]
        
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
            return result.stdout if result.stdout else "Resize complete"
        except Exception as e:
            return f"Error: {e}"


@mcp.tool()
def thumbnail(
    input_path: str,
    width: int,
    height: int | None = None,
    fit_mode: str = "cover",
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Generate a thumbnail of a given size.
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    width : int
        Maximum width of the thumbnail.
    height : int, optional
        Maximum height of the thumbnail. If None, maintains aspect ratio.
    fit_mode : str, default "cover"
        Fit mode: "cover" (cover entire area), "contain" (entire image visible).
    output_file : str, optional
        Path to write the output. If omitted, returns the content.
    extra_args : list[str], optional
        Extra vips CLI flags.
    
    Examples
    --------
    Create a 150x150 thumbnail:
        thumbnail("photo.jpg", 150, 150, output_file="thumb.jpg")
    
    Create a 200px wide thumbnail maintaining aspect ratio:
        thumbnail("photo.jpg", 200, fit_mode="contain", output_file="thumb.jpg")
    """
    height_str = f"{height}" if height else ""
    
    if output_file:
        if height_str:
            cmd = ["vips", "resize", input_path, output_file,
                   f"--width={width}", f"--height={height_str}",
                   f"--fit={fit_mode}", "--without-giop"]
        else:
            cmd = ["vips", "resize", input_path, output_file,
                   f"--width={width}", f"--fit={fit_mode}", "--without-giop"]
        
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
    else:
        if height_str:
            cmd = ["vips", "resize", input_path, f"stdout.{width}x{height}",
                   f"--fit={fit_mode}", "--without-giop"]
        else:
            cmd = ["vips", "resize", input_path, f"stdout.{width}",
                   f"--fit={fit_mode}", "--without-giop"]
        
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
            return result.stdout if result.stdout else "Thumbnail complete"
        except Exception as e:
            return f"Error: {e}"


@mcp.tool()
def rotate_image(
    input_path: str,
    degrees: int,
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Rotate an image by given degrees.
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    degrees : int
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
    """
    if output_file:
        cmd = ["vips", "rotate", input_path, output_file, f"--degrees={degrees}"]
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
    else:
        cmd = ["vips", "rotate", input_path, f"stdout", f"--degrees={degrees}"]
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
            return result.stdout if result.stdout else "Rotate complete"
        except Exception as e:
            return f"Error: {e}"


@mcp.tool()
def flip_image(
    input_path: str,
    direction: str = "both",
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Flip an image horizontally or vertically.
    
    Parameters
    ----------
    input_path : str
        Path to the input image file.
    direction : str, default "both"
        Flip direction: "both" (flip both), "horizontal", "vertical".
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
    if direction == "both":
        flip_args = "--both"
    elif direction == "horizontal":
        flip_args = "--horizontal"
    elif direction == "vertical":
        flip_args = "--vertical"
    else:
        return "Error: Invalid direction. Use 'both', 'horizontal', or 'vertical'."
    
    if output_file:
        cmd = ["vips", "flip", input_path, output_file, flip_args]
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
    else:
        cmd = ["vips", "flip", input_path, "stdout", flip_args]
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
            return result.stdout if result.stdout else "Flip complete"
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
    if output_file:
        cmd = ["vips", "remove-icc", input_path, output_file]
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
    else:
        cmd = ["vips", "remove-icc", input_path, "stdout"]
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
            return result.stdout if result.stdout else "ICC profile removed"
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
    cmd = ["vips", "info", input_path]
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
    arguments: str,
) -> str:
    """Run arbitrary vips CLI commands.
    
    Pass any vips CLI command as a string. The command will be executed
    and the output (stdout + stderr) will be returned.
    
    Parameters
    ----------
    arguments : str
        The complete vips CLI command to execute. For example:
        "vips resize input.jpg output.jpg --width=800 --height=600"
    
    Returns
    -------
    str
        The output of the command (stdout + stderr).
    
    Examples
    --------
    "vips shrink input.jpg output.jpg --with-giop --interpolation=best"
    "vips concat img1.jpg img2.jpg output.jpg"
    """
    try:
        result = subprocess.run(
            ["vips"] + arguments.split(),
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
