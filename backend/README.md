# Backend setup

This README is for the Django backend of LocalChef.

## Prerequisites
- Python 3.9+
- pip

## Quick start

```powershell
cd c:\Users\neera\Documents\localchef\backend
python -m venv C:\venvs\localchef
C:\venvs\localchef\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```

The backend will be available at:
- http://127.0.0.1:8000/

## Useful commands

Check the project configuration:

```powershell
cd c:\Users\neera\Documents\localchef\backend
C:\venvs\localchef\Scripts\Activate.ps1
python manage.py check
```

Apply database migrations:

```powershell
cd c:\Users\neera\Documents\localchef\backend
C:\venvs\localchef\Scripts\Activate.ps1
python manage.py migrate
```

## Notes
- The backend uses Django with SQLite.
- Dependencies are installed from the requirements file in this folder.
- Use a local virtual environment such as C:\venvs\localchef; it is ignored by Git via the repository root .gitignore file.
