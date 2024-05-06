FROM python:3.10-alpine


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /code

#define work dir
WORKDIR /code
COPY requirements.txt /code/

# install packages in requirements
RUN python -m pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 3000

COPY . /code