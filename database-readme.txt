hoe werken met database:
- maak met een user een database carwave_db aan
- zet envoriment variables voor de db of pas in config.py de postgres url aan met je wachtwoord
- run in de venv "flask db init" (er zou nu een migrations folder moeten aangemaakt worden)
- run "flask db migrate"
- run "flask db upgrade"
elke keer als je een update aan de database doet moet je die 2 laatste runnen