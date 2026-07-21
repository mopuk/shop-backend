FROM python:3.14

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./static /code/static

COPY ./alembic.ini /code/alembic.ini
COPY ./migrations /code/migrations
COPY ./tests /code/tests
COPY ./pytest.ini /code/pytest.ini
COPY ./conftest.py /code/conftest.py

CMD ["fastapi", "run", "app/app.py", "--port", "8000"]
