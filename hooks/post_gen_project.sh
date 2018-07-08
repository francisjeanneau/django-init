#!/bin/bash

# Init virtualenv and install requirements
virtualenv env
. env/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Init SQLite database
python manage.py makemigrations {{cookiecutter.project_slug}}
python manage.py migrate
