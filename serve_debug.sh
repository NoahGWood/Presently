#!/bin/bash

rm /tmp/test.db

source env/bin/activate

export FLASK_APP=app.py
export FLASK_ENV=development

flask run
