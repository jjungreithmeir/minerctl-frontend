all: clean run

install: source
	source env/bin/activate; pip install -r requirements.txt

clean:
	rm -rf __pycache__/ src/__pycache__/

clean_db:
	rm -f config/database.sqlite3

lint:
	~/.local/bin/pylint controller.py

freeze:
	source env/bin/activate; pip freeze > requirements.txt

run:
	source env/bin/activate; export FLASK_APP=controller.py; export FLASK_ENV=development; python controller.py 
