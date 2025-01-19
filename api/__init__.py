from flask import Blueprint

api = Blueprint('api', __name__)

from . import auth, entries, search

#basic blueprint for all api routes