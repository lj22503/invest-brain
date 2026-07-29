"""Wrapper to launch invest-brain MCP server with sys.path fix.

Why this exists:
- src/mcp_server/server.py uses relative imports (`.tools.thought_tools`).
- Running it directly as `python server.py` fails with
  `ImportError: attempted relative import with no known parent package`.
- This wrapper adds `src/` to sys.path so absolute imports resolve,
  then imports the FastMCP app from the original server module.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from mcp_server.server import mcp  # noqa: E402

if __name__ == "__main__":
    mcp.run()