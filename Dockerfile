FROM python

WORKDIR /stream-lit

COPY requirements.txt .

COPY ./src ./src

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "./src/main.py"]
