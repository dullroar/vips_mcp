# Proposed vips_mcp methods

Each row is a bounded public workflow. Grouping controls implementation order. Confirm capabilities against the pinned Docker backend before advertising a method. Keep source provenance and unsupported cases visible in the shipped documentation.

## Core

| Tool | Use this when | Acceptance focus |
| --- | --- | --- |
| `get_info` | Identify size, format, orientation, page count and channels before editing. | Bounded vipsheader fields and capability notices. |
| `resize_image` | Resize a photo or directory to 75 percent, or fit inside a given box. | Typed scale_percent or fit width/height with aspect and rounding tests. |
| `thumbnail` | Make centered or attention-cropped catalog thumbnails. | Shrink-on-load with explicit fit/fill policy and cropping preset. |
| `convert_image` | Export web-ready JPEG or WebP copies or preserve PNG alpha. | Finite saver profiles and explicit alpha handling. |
| `rotate_image` | Fix sideways photos consistently. | EXIF auto-orientation or a finite quarter-turn enum. |
| `flip_image` | Mirror a scanned image. | Explicit horizontal/vertical direction. |
| `crop_image` | Extract a known rectangle from a large scan. | Validated bounds and extract_area. |
| `pad_image` | Center an image on a standard canvas without distortion. | Fit then embed with a prescribed background. |
| `prepare_image_batch` | Prepare a directory for a website or product catalog. | One bounded recipe per job, deterministic output names and dry-run preview. |
| `convert_color_profile` | Deliver predictable sRGB output. | ICC transform with explicit preserve or use_srgb policy. |
| `strip_icc` | Remove a profile when a downstream system requires it. | Named operation after documented color assumptions. |

## Expanded

| Tool | Use this when | Acceptance focus |
| --- | --- | --- |
| `create_contact_sheet` | Review a folder of images in one ordered grid. | Bounded arrayjoin with spacing and tile limits. |
| `compose_overlay` | Place a transparent logo on approved output images. | Typed anchor, opacity and asset path using composite. |
| `flatten_alpha` | Create an opaque image for JPEG delivery. | Explicit named or numeric background using flatten. |
| `trim_border` | Trim uniform scanner margins. | find_trim with bounded threshold and minimum output. |
| `adjust_tone` | Correct underexposed scans with a small named preset. | Fixed gamma and linear adjustment ranges. |
| `sharpen_image` | Sharpen thumbnails from a known soft source. | Named sharpen presets and pixel regression fixtures. |
| `denoise_image` | Reduce scan speckles using a bounded filter. | Named median or blur profiles without arbitrary kernels. |
| `image_histogram` | Check channel clipping or compare exposure. | Finite bins and bounded histogram summary. |
| `extract_page` | Export a page or frame from a supported TIFF or animation. | Explicit page index and frame limits. |
| `make_image_pyramid` | Create tiles for zoomable large images. | Fixed Deep Zoom layout, tile size and output manifest. |
| `split_channels` | Inspect or export named channels from an image. | Band extraction with finite channel names and output limits. |
| `make_mask` | Make a threshold mask from a document scan. | Typed threshold, luminance policy, and safe monochrome output. |
| `make_tiled_tiff` | Create a portable tiled TIFF for large-image workflows. | Bounded tile, compression and pyramid profile checked in Docker. |

## Primary references

- [libvips function families](https://github.com/libvips/libvips/blob/master/doc/function-list.md)
- [vipsthumbnail size and smart-crop examples](https://www.libvips.org/API/current/using-vipsthumbnail.html)
- [libvips Python image examples](https://www.libvips.org/API/current/examples.html)
- [libvips API reference](https://www.libvips.org/API/current/)
- [Community fit-versus-crop use case](https://stackoverflow.com/questions/69363178/resize-to-specific-height-and-width-with-pyvips)
