FROM python:3.7
ADD app.py /
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD [ "python3", "./app.py" ]
