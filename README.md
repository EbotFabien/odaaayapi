[![Python](https://img.shields.io/badge/python-2.7%2C%203.5%2C%203.6--dev-blue.svg)]()
[![Requirements](https://requires.io/github/brennv/flask-app/requirements.svg?branch=master)](https://requires.io/github/brennv/flask-app/requirements/?branch=master)
[![Travis](https://travis-ci.org/brennv/flask-app.svg?branch=master)](https://travis-ci.org/brennv/flask-app)
[![Coverage](https://codecov.io/gh/brennv/flask-app/branch/master/graph/badge.svg)](https://codecov.io/gh/brennv/flask-app)
[![Code Climate](https://codeclimate.com/github/brennv/flask-app/badges/gpa.svg)](https://codeclimate.com/github/brennv/flask-app)
[![Docker](https://img.shields.io/docker/automated/jrottenberg/ffmpeg.svg?maxAge=2592000)]()

# News
News application for information gathering and sharing with an API backend built with flask. This application is company material and should not be shared with any unauthorized persons.

## Rules

- Do not share code with unauthorized personnels.
- Make sure you send commits to branches with commit messages.
- Comment code properly before commit.
- Create pull requests and talk with teams.
- **DO NOT PUSH** to **MASTER** Branch.


## Getting started

Install [Python](https://www.python.org/downloads/) and run code bellow. Otherwise, for the standalone web service:

```shell
pip install -r requirements.txt
python app.py
```

-- Visit [http://localhost:5000](http://localhost:5000)

To create models run the following command:

For Windows
```shell
set FLASK_APP=news.py
flask db init
flask db migrate
flask db upgrade
```
For MacOs and Linux
```shell

export FLASK_APP=news.py

flask db init
flask db migrate
flask db upgrade
```

## Development

Create a new branch off the **master** branch for features or fixes.

After making changes rebuild images and run the app:

```shell
docker-compose build
docker-compose run -p 5000:5000 web python app.py
# docker stop flaskapp_redis_1
```

## Tests

Tests are not a priority so skip tests if possible.
Standalone unit tests run with:

```shell
pip install pytest pytest-cov pytest-flask
pytest --cov=web/ --ignore=tests/integration tests
```

Integration with docker:

```shell
docker-compose build
docker-compose up
```

Integration and unit tests run with:

```shell
docker-compose -f test.yml -p ci build
docker-compose -f test.yml -p ci run test python -m pytest --cov=web/ tests
# docker stop ci_redis_1 ci_web_1
```

After testing, submit a pull request to merge changes with **master**.


## Notifications

Updates and alerts pushed via Zoom or gmail:

- boogiedas (zoom)
- leslie.etubo@gmail.com
- bakariwarday@gmail.com
- Join [SlackGroup](https://join.slack.com/t/newsapp-global/shared_invite/zt-fejgqdzk-5uOwp7cefQwGDOaUHCv9wg) 

