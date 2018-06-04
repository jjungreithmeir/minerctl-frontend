all: clean setup run

install:
	pip install -r requirements.txt --user

clean:
	rm -r __pycache__/

setup:
	export FLASK_APP=controller.py
	export FLASK_ENV=development

freeze:
	pip freeze > requirements.txt

run:
	python -m flask run
