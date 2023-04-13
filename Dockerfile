FROM python:3.10

ADD /main.py .

RUN pip install requirements.txt

CMD [ "python", "./main.py" ]
## runs 'python ./main.py'
