pip install -r requirements.txt
mypy .
coverage run -m unittest discover .\src\tests
coverage report -m
coverage xml