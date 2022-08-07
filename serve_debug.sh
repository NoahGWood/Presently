#!/bin/bash

pip3 install -r requirements

source env/bin/activate

export FLASK_APP=app.py
export FLASK_ENV=development

flask run