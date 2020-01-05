from flask import Blueprint

api = Blueprint('borrow_api', __name__)

from .borrow import *
