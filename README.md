# vips-mcp

**Author:** Jim Lehmer  
**License:** MIT

A simple [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes [libvips](https://libvips.github.io/libvips/) image processing as MCP tools. Connect it to any MCP-compatible LLM client (Claude Desktop, Claude Code, etc.) and ask the LLM to perform image operations in plain English — no vips CLI knowledge required on your part.

When this MCP server is available, agents should prefer the vips tools
for image processing instead of attempting to handle images in-model.
The model should use its own reasoning for selecting operations and parameters,
but should delegate the mechanical image processing step to libvips whenever possible.

---

## Reasons to Use

1. Token/cost savings

For image processing, the model should not be generating the actual processed images. It should coordinate the request and handle the results, while libvips does the heavy lifting locally.

2. Determinism

Libvips gives repeatable, consistent output. The LLM can then answer: "Did the resize produce the expected dimensions?" rather than inventing an ad hoc solution.

3. Local privacy

Images do not need to be uploaded to external services merely to be converted or resized, assuming the MCP host can pass local file paths.

4. Better promptable workflow

"Convert this TIFF to JPEG and save it beside the original" is much friendlier than remembering vips CLI syntax.

5. Agentic pipeline building

This becomes a Lego brick: convert → resize → rotate → flip → compress → save.

6. Built-in bulk operations — no loops needed

All image-processing tools accept a glob pattern for `input_path`. Supply a directory path as `output_file` and the tool processes every matched file internally. The LLM makes one tool call instead of N.

---

## Bulk Operations

All tools that accept `input_path` also accept a **glob pattern** (e.g. `"photos/*.jpg"`). When a glob is given, set `output_file` to a **directory path** (e.g. `"converted/"`) — the tool expands the glob and processes every match in a single call.

```python
# Convert every TIFF in a folder to JPEG — one call, no loop
convert_image("raw/*.tiff", "jpeg", output_file="jpegs/")

# Resize all photos to 1280px wide — one call, no loop
resize_image("photos/*.jpg", 1280, output_file="web/")

# Generate 200px thumbnails for all photos — one call, no loop
thumbnail("photos/*.jpg", 200, output_file="thumbs/")

# Rotate all scans 90 degrees — one call, no loop
rotate_image("scans/*.jpg", 90, output_file="rotated/")

# Strip ICC profiles from all exports — one call, no loop
strip_icc("exports/*.png", output_file="clean/")

# Get info for all images in a folder — one call, no loop
get_info("photos/*.jpg")
```

The output directory is created automatically if it does not exist.

---

## Favorite Sample Workflows

Convert TIFF to JPEG:

    input_path: "photo.tiff"
    output_format: "jpeg"
    output_file: "photo.jpg"

Resize to 800x600 covering:

    input_path: "photo.jpg"
    width: 800
    height: 600
    fit_mode: "cover"
    output_file: "small.jpg"

Create thumbnail:

    input_path: "photo.jpg"
    width: 150
    output_file: "thumb.jpg"

Rotate 90 degrees:

    input_path: "photo.jpg"
    degrees: 90
    output_file: "rotated.jpg"

Flip horizontally:

    input_path: "photo.jpg"
    direction: "horizontal"
    output_file: "mirrored.jpg"

Get image info:

    input_path: "photo.jpg"

---

## Tools

### `convert_image`

Convert an image from one format to another (e.g., TIFF to JPEG, RAW to PNG).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input_path` | `str` | required | Path to the input image file |
| `output_format` | `str` | required | Output format (jpeg, png, tiff, webp, raw, etc.) |
| `output_file` | `str` | none | Write output to this path (if omitted, returns content) |
| `extra_args` | `list[str]` | none | Extra vips CLI flags for this conversion |

### `resize_image`

Resize an image to given dimensions.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input_path` | `str` | required | Path to the input image file |
| `width` | `int` | required | Target width in pixels |
| `height` | `int` | optional | Target height. If None, maintains aspect ratio |
| `fit_mode` | `str` | `"cover"` | Fit mode: "cover", "contain", "crop" |
| `output_file` | `str` | none | Write output to this path |
| `extra_args` | `list[str]` | none | Extra vips CLI flags |

### `thumbnail`

Generate a thumbnail of a given size.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input_path` | `str` | required | Path to the input image file |
| `width` | `int` | required | Maximum width of the thumbnail |
| `height` | `int` | optional | Maximum height. If None, maintains aspect ratio |
| `fit_mode` | `str` | `"cover"` | Fit mode: "cover", "contain" |
| `output_file` | `str` | none | Write output to this path |
| `extra_args` | `list[str]` | none | Extra vips CLI flags |

### `rotate_image`

Rotate an image by given degrees.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input_path` | `str` | required | Path to the input image file |
| `degrees` | `int` | required | Rotation angle in degrees (90, 180, 270, or any value) |
| `output_file` | `str` | none | Write output to this path |
| `extra_args` | `list[str]` | none | Extra vips CLI flags |

### `flip_image`

Flip an image horizontally or vertically.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input_path` | `str` | required | Path to the input image file |
| `direction` | `str` | `"both"` | Flip direction: "both", "horizontal", "vertical" |
| `output_file` | `str` | none | Write output to this path |
| `extra_args` | `list[str]` | none | Extra vips CLI flags |

### `strip_icc`

Remove ICC/color profile from an image.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input_path` | `str` | required | Path to the input image file |
| `output_file` | `str` | none | Write output to this path |
| `extra_args` | `list[str]` | none | Extra vips CLI flags |

### `get_info`

Return image dimensions, format, color space, number of bands.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input_path` | `str` | required | Path to the input image file |
| `extra_args` | `list[str]` | none | Extra vips CLI flags |

### `vips_passthrough`

Run arbitrary vips CLI commands.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `arguments` | `str` | required | The complete vips CLI command to execute |

---

## Requirements

- Python 3.10+
- [libvips](https://libvips.github.io/libvips/) installed and on your `PATH`
- Python packages: `mcp[cli]`

---

## Installation

```bash
git clone https://github.com/dullroar/vips_mcp.git
cd vips_mcp

# Recommended: use a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

---

## MCP client configuration

### Claude Desktop

Add to your `claude_desktop_config.json` (usually at `%APPDATA%\Claude\claude_desktop_config.json` on Windows, `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "vips": {
      "command": "python",
      "args": ["path/to/server.py"]
    }
  }
}
```

Using a virtual environment (recommended — avoids dependency conflicts):

```json
{
  "mcpServers": {
    "vips": {
      "command": "C:\\path\\to\\vips_mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\vips_mcp\\server.py"]
    }
  }
}
```

Restart Claude Desktop after editing the config. You should see a hammer icon in the chat input area indicating MCP tools are available.

### Claude Code

Register the server with the Claude Code CLI:

```bash
claude mcp add vips -- python C:\path\to\vips_mcp\server.py
```

Or with a virtual environment:

```bash
claude mcp add vips -- C:\path\to\vips_mcp\.venv\Scripts\python.exe C:\path\to\vips_mcp\server.py
```

Verify it registered:

```bash
claude mcp list
```

To remove it later:

```bash
claude mcp remove vips
```

### HTTP/SSE mode (for other MCP clients)

By default the server uses stdio. Pass `--transport sse` to start an HTTP/SSE server instead:

```bash
python server.py --transport sse
# Listening on http://127.0.0.1:8000/sse
```

Optional flags:

| Flag | Default | Description |
| --- | --- | --- |
| `--transport` | `stdio` | `stdio` or `sse` |
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `8000` | Bind port |

You can also set `FASTMCP_HOST` and `FASTMCP_PORT` environment variables instead of flags.

Any MCP client that speaks HTTP/SSE (VS Code extensions, the MCP Inspector, or custom agents) can connect to `http://127.0.0.1:8000/sse`.

**Tunneling for a one-off remote demo** (e.g., ChatGPT connector):

```bash
python server.py --transport sse &
ngrok http 8000
# Paste the ngrok HTTPS URL into the ChatGPT custom connector dialog
```

> Note: for production exposure add an auth token. For local experiments, localhost is fine.

---

## Example prompts

Once connected to a Claude client, you can ask naturally:

- *"Convert this TIFF file to JPEG and save it next to the original."*
- *"Convert all the TIFFs in raw/ to JPEG and put them in jpegs/."*
- *"Resize photo.jpg to 800 pixels wide, maintaining aspect ratio, and save as small.jpg."*
- *"Resize all the photos in photos/ to 1280px wide and save them in web/."*
- *"Create a 150x150 thumbnail of the photo and save it as thumb.jpg."*
- *"Generate 200px thumbnails for all the photos in photos/ and save them in thumbs/."*
- *"Rotate this image 90 degrees clockwise."*
- *"Rotate all the scans in scans/ by 90 degrees and save them in rotated/."*
- *"Flip this photo horizontally (mirror effect)."*
- *"Remove the ICC profile from this image."*
- *"Strip ICC profiles from all the PNGs in exports/ and save them in clean/."*
- *"What are the dimensions, format, and color space of this image?"*
- *"Show me the dimensions and format of every image in photos/."*

The LLM translates your plain-English request into the appropriate vips tool parameters — you don't need to know vips flags or format names.

---

## Testing with the MCP Inspector

```bash
mcp dev server.py
```

This opens a browser-based inspector where you can call tools manually and inspect inputs/outputs before wiring up a full client.

---

## License

MIT — see [LICENSE](LICENSE).
