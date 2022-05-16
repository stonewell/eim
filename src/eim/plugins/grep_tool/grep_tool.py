from .ag_tool import AgTool


def get_grep_tool(ctx):
  tool = AgTool(ctx)

  if tool.is_working():
    return tool

  return None
