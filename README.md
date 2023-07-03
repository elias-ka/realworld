# RealWorld

This is a sample backend project for the [RealWorld specification](https://www.realworld.how/docs/intro) written in Python using FastAPI, SQLAlchemy, Pydantic, and PostgreSQL as the database.
Essentially, it's a blogging platform similar to [Medium](https://medium.com/).

I don't plan on adding any frontend to this project, but you can see it in action using the demo frontend at [https://demo.realworld.io/](https://demo.realworld.io/).

Thanks to [Thinkster](https://thinkster.io/) for creating the RealWorld specification and providing the [original implementation](https://github.com/gothinkster/realworld)

## Features
- User registration and authentication
- User profiles
- User follow/unfollow
- Create/update/delete articles 
- Articles listing/feed
- Article comments 
- Favorite/unfavorite articles  

## Getting started
Clone the repository and install the dependencies:
```bash
git clone https://github.com/elias-ka/realworld.git
cd realworld
poetry install
```

Copy the `.env.example` file to `.env` and fill in the values:
```bash
cp .env.example .env
```

Create a PostgreSQL database and run the migrations:
```bash
poetry run alembic upgrade head
```

Run the server:
```bash
poetry run uvicorn realworld.main:app
```

## Running the Postman tests
To locally run the provided Postman collection against your backend, in the root folder execute:

```bash
./postman/run-api-tests.sh
```

For more details, see the script [run-api-tests.sh](./postman/run-api-tests.sh).

The tests are copied from the original implementation.

