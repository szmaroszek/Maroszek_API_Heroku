# Maroszek_API_Heroku
Maroszek-API is a simple REST API - a basic car makes and models database interacting with an external API.

Available endpoints:

POST /cars/ 

DELETE /cars/{ id }/

POST /rate/

GET /cars/ 

GET /popular/


Run in Docker:
$ git clone https://github.com/szmaroszek/Maroszek_API_Heroku.git

$ cd Maroszek_API_Heroku/

$ docker-compose run web python manage.py migrate

$ docker-compose run web python manage.py collectstatic --noinput

$ docker-compose up

and access on http://localhost:8000/


Public host:
https://api-maroszek.herokuapp.com/
