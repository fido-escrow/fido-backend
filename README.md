## Installation
  - Install [Python](https://www.python.org/downloads/), [Pipenv](https:/.pipenv.org/) and [Postgres](https://www.postgresql.org/) on your machine
  - Clone the repository `$ git clone git@github.com:jerichoruz/fido-back.git`
  - Change into the directory `$ cd /fido-back`
  - Create the project virtual environment with `$ pipenv --three` command
  - Activate the project virtual environment with `$ pipenv shell` command
  - Install all required dependencies with `$ pipenv install`
  - Rename .env.sample to .env and edit variables
      ```
      FLASK_ENV=
      FLASK_PORT=
      DATABASE_URL=
      JWT_SECRET_KEY=
      FRONT_URL=
      MIFIEL_APP_ID=
      MIFIEL_APP_SECRET=
      PAYPAL_ID=
      PAYPAL_SECRET=
      MAIL_SERVER=
      MAIL_PORT=465
      MAIL_USERNAME=
      MAIL_PASSWORD=
      ```
  - Create database fido
      ```
      $ sudo su - postgres -c "createuser -s fido" 2> /dev/null || true
      $ psql
      # ALTER USER fido WITH ENCRYPTED PASSWORD 'fido';
      # CREATE DATABASE fido WITH TEMPLATE template0;
      # ALTER DATABASE fido OWNER TO fido;
      ```
  - Due to a bad flask relation please Comment line 5 from UserModel before Migrate
      ```
      1 # src/models/UserModel.py
      2 from marshmallow import fields, Schema
      3 import datetime
      4 from . import db
      5 #from ..app import bcrypt #after database migration uncomment after to esxecute python run.py
      ```
  - `$ python manage.py db init`
  - `$ python manage.py db migrate`
  - `$ python manage.py db upgrade`
  
  - Start the app with `python run.py`
