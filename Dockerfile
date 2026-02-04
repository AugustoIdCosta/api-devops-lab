
FROM python:3.9-alpine as builder

RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt .

RUN pip install --prefix=/install -r requirements.txt 


FROM python:3.9-alpine 

WORKDIR /app

RUN apk add --no-cache libpq

COPY --from=builder /install /usr/local
COPY . .

CMD ["python", "app.py"]


