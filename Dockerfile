FROM python:3.10

ADD /src/main.py .

RUN pip install requirements.txt

CMD [ "python", "./src/main.py" ]
## runs 'python ./main.py'
