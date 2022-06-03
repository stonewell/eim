import logging
from .ag_tool import AgTool
from .pyeverything_tool import PyEverythingTool


def get_grep_tool(ctx):
  try:
    tool = PyEverythingTool(ctx)

    if tool.is_working():
      return tool

    tool = AgTool(ctx)

    if tool.is_working():
      return tool
  except:
    logging.exception('create tool fail')

  return None
