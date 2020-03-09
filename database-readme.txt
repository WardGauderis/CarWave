how do database:
- make a database called carwave_db with a user
- set enviroment variables to match user and password, or in config.py edit the url to fit your user & password
- run "flask db init" in the venv (a folder called migrations should appear) (dont forget to install dependencies)
- run "flask db migrate"
- run "flask db upgrade"
- the migrations folder must also be pushed to github for compatibility
every time you change something to the database in models.py, run these last 2 commands

NB: the postgis extension is needed, so run `CREATE EXTENSION postgis;` on carwave_db

adding/removing data:
https://docs.sqlalchemy.org/en/13/core/dml.html
