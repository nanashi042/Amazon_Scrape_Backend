# Amazon Scrape Backend

Lightweight Django + Django REST Framework backend designed to power an Amazon product scraping workflow. The repository currently contains the base project scaffolding (`main_api`) plus the `Scraping_Event` app where scraping jobs, serializers, and API endpoints will live.

---

## Tech Stack
- Python 3.12+
- Django 5.2
- Django REST Framework 3.16
- SQLite (default dev DB, can be swapped via settings)

---

## Project Layout
```
Amazon_Backend/
├── manage.py
├── pyproject.toml          # project metadata + dependencies
├── main_api/               # global Django project config
│   ├── settings.py         # DRF installed, SQLite configured
│   ├── urls.py             # root router placeholder
│   └── ...
├── Scraping_Event/         # app for scraping jobs + APIs
│   ├── views.py            # ready for DRF views/viewsets
│   ├── urls.py             # expose app endpoints once added
│   └── ...
└── db.sqlite3              # default dev database
```

---

## Getting Started

### 1. Install dependencies
```bash
cd "/Users/nanashi/Library/CloudStorage/GoogleDrive-ny1113548@gmail.com/My Drive/Python_Learning/Projects/Amazon_Backend"
uv sync
```
(If you prefer pip, run `pip install -r <(uv pip compile pyproject.toml)`.)

### 2. Apply migrations
```bash
uv run python manage.py migrate
```

### 3. Create a superuser (optional, for quick admin checks)
```bash
uv run python manage.py createsuperuser
```

### 4. Run the dev server
```bash
uv run python manage.py runserver
```
Open `http://127.0.0.1:8000/` to confirm the project boots (currently only the Django admin is exposed).

---

## Next Steps / TODO
- **Data model**: define models for products, scrape jobs, and run history in `Scraping_Event/models.py`.
- **API surface**: add DRF serializers/viewsets, wire them in `Scraping_Event/urls.py`, and include the app URLs from `main_api/urls.py`.
- **Scraping pipeline**: integrate the actual scraping logic (Celery task, background worker, or synchronous job) and connect it to API actions.
- **Filtering & pagination**: leverage `django-filter` for product/job querying once data exists.
- **Testing**: add model + API tests in `Scraping_Event/tests.py` as functionality lands.

---

## Running Tests
When tests are added:
```bash
uv run python manage.py test
```

---

## Environment Notes
- Defaults to SQLite; update `DATABASES` in `main_api/settings.py` for Postgres/MySQL in production.
- `DEBUG` is enabled; configure env vars (`DJANGO_SECRET_KEY`, `DEBUG`, etc.) before deployment.
- Static files are served by Django in dev; use a proper static host/CDN for production.

---

## Contributing
1. Fork or create a feature branch.
2. Keep dependencies in `pyproject.toml` / `uv.lock`.
3. Run migrations + tests before opening a PR.

---

Happy scraping!