# Demo Project

This is a comprehensive demo project designed to test the performance of [django-global-search](https://github.com/your-repo/django-global-search) with large-scale datasets and complex model relationships.

## Setup

### Installation

1. **Install dependencies**
   ```bash
   cd demo
   uv sync
   ```

2. **Run migrations**
   ```bash
   uv run python manage.py migrate
   ```

3. **Create a superuser**
   ```bash
   uv run python manage.py createsuperuser
   ```

4. **Generate demo data**
   ```bash
   uv run python manage.py create_data
   ```

   You can adjust batch size for better performance:
   ```bash
   uv run python manage.py create_data --chunk-size 5000
   ```

5. **Run the development server**
   ```bash
   uv run python manage.py runserver
   ```

6. **Access the admin interface**
   - Navigate to http://localhost:8000/admin/
   - Log in with your superuser credentials
   - Try the global search at http://localhost:8000/admin/global-search/
