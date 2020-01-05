from flask import Blueprint

api = Blueprint('book_api', __name__)

from .book import *
