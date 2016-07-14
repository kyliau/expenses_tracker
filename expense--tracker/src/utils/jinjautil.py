import jinja2
import os

currentDir = os.path.dirname(__file__)
srcDir = os.path.dirname(currentDir)
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(srcDir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)