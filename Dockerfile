FROM python:3.9

WORKDIR /flask_crud

COPY requirements.txt . 
RUN pip install -r requirements.txt

COPY app.py .

CMD ["python3","./app.py"]