import asyncio
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class StdioTest(unittest.IsolatedAsyncioTestCase):
    async def test_resize_image(self):
        with tempfile.TemporaryDirectory(prefix="vips-mcp-") as directory:
            source = Path(directory) / "source.png"
            output = Path(directory) / "resized.png"
            subprocess.run(
                ["vips", "black", str(source), "40", "30"], check=True, timeout=10
            )

            result = await asyncio.wait_for(self.resize(source, output), timeout=30)
            self.assertFalse(result.isError, result)
            self.assertEqual(
                [item.text for item in result.content if item.type == "text"],
                [f"Written to {output}"],
            )

            for field, expected in (("width", "20"), ("height", "15")):
                header = subprocess.check_output(
                    ["vipsheader", "-f", field, str(output)], text=True, timeout=10
                )
                self.assertEqual(header.strip(), expected, field)

    async def resize(self, source: Path, output: Path):
        server = Path(__file__).resolve().parents[1] / "server.py"
        params = StdioServerParameters(command=sys.executable, args=[str(server)])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(
                    "resize_image",
                    {
                        "input_path": str(source),
                        "width": 20,
                        "output_file": str(output),
                    },
                )
