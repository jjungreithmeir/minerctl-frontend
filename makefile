all: setup run

install:
    pip install -r requirements.txt --user

setup:
	export FLASK_APP=controller.py
	export FLASK_ENV=development

run:
	python -m flask run
