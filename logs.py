from datetime import datetime
import logging
import os

def timestamp_for_file():
  return datetime.now().strftime('%y-%m-%d-%H:%M.%S')


def CreateLogger(level, filename):
  directory = os.path.dirname(filename)
  if not os.path.exists(directory):
    os.makedirs(directory)
  logging.basicConfig(level = level,
                      datefmt='%m-%d %H:%M',
                      format='%(asctime)s %(name)s %(levelname)s %(message)s',
                      filename=filename,
                      filemode='w')
  logger = logging.getLogger()
  console = logging.StreamHandler()
  # TODO(fortuna): Make the debug level a flag.
  console.setLevel(level)
  logger.addHandler(console)
  logger.warning("Logging to: %s", filename)
  return logger
