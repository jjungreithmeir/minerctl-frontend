all: clean run

install:
	pip install -r requirements.txt --user

clean:
	rm -rf __pycache__/ src/__pycache__/

clean_db:
	rm -f config/database.sqlite3

freeze:
	pip freeze > requirements.txt

run:
	export FLASK_APP=controller.py; export FLASK_ENV=development; python -m flask run
