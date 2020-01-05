from flask import Blueprint

api = Blueprint('card_api', __name__)

from .card import *
