import jinja2
import os

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
JINJA_ENVIRONMENT = jinja2.Environment(     
    loader=jinja2.FileSystemLoader(parentDir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)