all: run

install: source
	. env/bin/activate; pip install -r requirements.txt

clean:
	rm -rf __pycache__/ src/__pycache__/

clean_db:
	rm -f config/database.sqlite3

clean_layout:
	rm -f config/layout.json

lint:
	. env/bin/activate; pylint controller.py || exit 0

freeze:
	. env/bin/activate; pip freeze > requirements.txt

dev:
	. env/bin/activate; export FLASK_APP=controller.py; export FLASK_ENV=development; python controller.py

run:
	. env/bin/activate; uwsgi --socket 0.0.0.0:8080 --protocol=http -w wsgi:APP;
