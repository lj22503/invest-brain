"""MCP Server main entry point"""

from mcp.server.fastmcp import FastMCP

from .tools.thought_tools import thought_tools
from .tools.rag_tools import rag_tools
from .tools.memory_tools import memory_tools
from .tools.reminder_tools import reminder_tools
from .tools.pattern_tools import pattern_tools
from .tools.report_tools import report_tools
from .tools.roundtable_tools import roundtable_tools
from .tools.notifier_tools import notifier_tools
from .datasources.akshare_datasource import akshare_tools
from .datasources.tushare_datasource import tushare_tools
from .price_checker import check_price_conditions
from .scheduler import start_scheduler

# Initialize FastMCP server
mcp = FastMCP("investment-assistant")

# Vector store is lazy-loaded on first use to avoid ONNX download blocking startup
# Uncomment the following lines after ONNX model is downloaded (~30 min at current speed)
# from .knowledge.vector_store import get_vector_store
# vs = get_vector_store()
# vs.rebuild_index()

# Check price conditions on startup
triggered = check_price_conditions()

# Start time-based reminder scheduler
start_scheduler()

# Register all tools from each FastMCP group
_tool_groups = [
    ("thought", thought_tools),
    ("rag", rag_tools),
    ("memory", memory_tools),
    ("reminder", reminder_tools),
    ("pattern", pattern_tools),
    ("report", report_tools),
    ("invest", roundtable_tools),
    ("notify", notifier_tools),
    ("market", akshare_tools),
    ("tushare", tushare_tools),
]
for prefix, group in _tool_groups:
    for tool in group._tool_manager.list_tools():
        mcp.add_tool(tool.fn, name=prefix + "_" + tool.name, description=tool.description)


def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()