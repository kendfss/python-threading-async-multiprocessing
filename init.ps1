$env:FLASK_APP="src"
$env:FLASK_DEBUG=[boolean] 1
# flask run
flask initdb
flask run --host=0.0.0.0