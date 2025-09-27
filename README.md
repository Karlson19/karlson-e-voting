# KARLSON'S E-VOTING SYSTEM (Django MVP)

**A minimal e-voting management system built with Django and Bootstrap.**  
This repository contains the MVP used for demonstrations and local testing. It is *not* production-ready (no OTP, email verification, or blockchain). The focus is on core functionality: register/login, create/manage elections, add candidates, cast 1 vote per voter, and view results after an election ends.

---

## Quick overview (for non-technical users)

- Admins (staff users) can **create elections** and **add candidates**.
- Voters can **register**, **log in**, browse **active elections**, and **cast one vote per election**.
- Results are visible **only after** the election finishes.

---

## Table of contents

- [Prerequisites](#prerequisites)  
- [Installation (Windows, step-by-step)](#installation-windows-step-by-step)  
- [Run the project locally](#run-the-project-locally)  
- [Create admin (superuser)](#create-admin-superuser)  
- [How to test voting flow](#how-to-test-voting-flow)  
- [Important files & structure](#important-files--structure)  
- [Security & .gitignore note](#security--gitignore-note)  
- [Troubleshooting](#troubleshooting)  
- [Contributing](#contributing)  
- [Contact](#contact)

---

## Prerequisites

Make sure you have on your machine:

- Python 3.10+ (you have 3.13, that's OK)  
- pip (comes with Python)  
- Git + GitHub Desktop installed  
- (Optional) `virtualenv` or use Python built-in `venv`  

---

## Installation (Windows — exact commands)

Open PowerShell in your project folder (`C:\Users\HomePC\PycharmProjects\DjangoProject1`).

1. Create and activate a virtual environment (recommended):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```
If you don't have `requirements.txt`, install Django and other libs:
```powershell
pip install django
# plus any other packages your project uses (e.g. python-dotenv)
```

3. Create `.env` (optional local secrets) — recommended for not committing `SECRET_KEY`:
Create a file named `.env` in the project root with this content:
```text
SECRET_KEY=change_this_to_a_random_string_for_local_dev
DEBUG=True
```
*(If you don't use `.env`, your `settings.py` may still use a literal SECRET_KEY — do **not** push that to a public repo.)*

---

## Run the project locally

1. Apply database migrations:
```powershell
python manage.py makemigrations
python manage.py migrate
```

2. Create a superuser (admin account) to access Django admin and the app dashboard:
```powershell
python manage.py createsuperuser
# follow the prompts for username, email, password
```

3. Run the development server:
```powershell
python manage.py runserver
```

4. Open in your browser:
- Public app: `http://127.0.0.1:8000/`
- Django admin: `http://127.0.0.1:8000/admin/`

---

## Create admin (superuser)

Use the `createsuperuser` command above. If you lose the account or reset DB, recreate with same command. If you need to mark an existing user as staff:

```powershell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> u = User.objects.get(username='yourusername')
>>> u.is_staff = True
>>> u.is_superuser = True
>>> u.save()
>>> exit()
```

---

## How to test voting flow (manual steps)

1. Log in as the admin account (via `/admin/` or the app dashboard `/dashboard/elections/`).  
2. Create a new election with a start and end time that includes "now" (so it is active).  
3. Add at least two candidates for that election (via the app dashboard).  
4. Register another test user (or open a private window) and log in as that user.  
5. Visit the election page (click the election on the home page) and cast a vote — you should only be allowed one vote per election.  
6. If you try to vote twice, the application should block the second vote and show a message.  
7. After the election end time passes, visit the results page to see final counts.

---

## Important files & structure

Top-level:
```
E_Voting/                # Django project settings
manage.py
requirements.txt
db.sqlite3               # (should be ignored by .gitignore)
voting/                  # Django app
templates/               # HTML templates (base.html, voting/..., accounts/...)
```

Key app files:
- `voting/models.py` — Election, Candidate, Vote models (unique constraint for one vote)
- `voting/views.py` — Views for listing, details, voting, admin dashboard
- `voting/urls.py` — App routes (home, election detail, vote, dashboard)
- `templates/base.html` — site layout (title, navbar, footer)
- `templates/voting/election_detail.html` — where the vote POST is performed

---

## Security & .gitignore note (VERY IMPORTANT)

- **Do not commit** `db.sqlite3`, `.venv`, or `E_Voting/settings.py` with your `SECRET_KEY`. Add them to `.gitignore`. We added `.gitignore` by default.
- If your `SECRET_KEY` was accidentally pushed to a **public** repository, treat it as compromised — rotate it and invalidate any credentials connected to it.
- For production, use environment variables and turn `DEBUG=False`.

---

## Troubleshooting (common issues)

- **“NoReverseMatch” / missing URL name** — ensure the `voting/urls.py` matches the view names used in templates (e.g. `election_detail`, `cast_vote`).
- **IntegrityError on Vote** — the model enforces unique voter/election. If you see duplicates, check DB migrations and constraints.
- **Datetime validation errors** when creating elections — ensure browser sends `datetime-local` format, or use separate date/time inputs.
- **Admin pages not visible** — ensure your user has `is_staff=True`. See the shell commands above to set it.
- **Cannot commit changes in GitHub Desktop** — check `.gitignore` and ensure files are saved in your editor. Use *Repository → Open in Explorer* to open files.

If you hit an error, copy the full traceback shown in the browser (the red Django debug page) and paste it into the chat — I’ll explain the specific fix.

---

## Contributing

This is a personal MVP. If you want to extend it:
- Add email verification for voters.
- Add CSV/PDF export for results.
- Add dashboard analytics for admin.
- Add unit tests for the voting flow.

If you submit PRs, keep migration files tidy and document DB schema changes.

---

## License

This project is provided as-is for learning and prototyping. No license specified — contact the author for reuse.

---

## Contact / Author

**Karlson W. Achegeba** — creator of this MVP.  
If you need help setting up, paste errors here and I’ll walk you through fixes step-by-step.

