# MiniMarket

Django CRUD project (SQLite) for a small marketplace (“petites annonces”).

## Setup

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py runserver
```

## Features (planned)

- Categories + Listings (with relations)
- Full CRUD
- Login / Logout
- Search + Pagination
- Bootstrap UI
- Image upload

