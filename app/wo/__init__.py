from flask import Blueprint

wo = Blueprint('wo', __name__)

from . import views
