from flask import Blueprint

authenticate= Blueprint('authenticate', __name__)

from . import auth