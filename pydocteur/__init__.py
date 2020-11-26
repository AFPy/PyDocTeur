from flask import Flask, request
import json

application = Flask(__name__)


@application.route('/', methods=['POST'])
def process_incoming_payload():
   print(request.data)
   return "OK", 200
