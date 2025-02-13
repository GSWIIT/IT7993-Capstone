from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
import json
from web3 import Web3
import hashlib
import time

home_bp = Blueprint('home', __name__, template_folder='templates')

@home_bp.route('/')
def show_homepage():
    """Render the HTML UI."""
    return render_template('home.html')

