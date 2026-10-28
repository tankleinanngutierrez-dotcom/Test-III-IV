# MediBook Clinic Appointments — IT 424 Test III & IV

Django-rendered clinic booking project demonstrating templates, forms, server validation, HTMX partial requests, and Alpine.js interface state.

## Requirements
- Python 3.10+
- Django 4.2 LTS or Django 5.x
- Browser with internet access for the pinned HTMX and Alpine.js CDN scripts (can be switched to local static files).

## Windows PowerShell setup
```powershell
cd MediBook_TestIII_IV
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations clinic
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Open http://127.0.0.1:8000/ . No login is required for staff pages, as the exam specifies.

## Hosting choices
- HTMX 2.0.4 is loaded from a pinned CDN URL in `templates/base.html` to keep the project build-free and use its documented request/swap behavior. For an offline classroom demo, download the pinned file to `static/js/` and change the script tag.
- Alpine.js 3.14.8 is loaded with `defer` from a pinned CDN URL. It is only used for interface state, not authoritative data. For an offline demo, place the pinned distribution in `static/js/`.
- Custom CSS and project JavaScript live in `static/css/` and `static/js/`; image assets belong in `static/img/`. Uploaded doctor photos are stored under `media/doctors/` and served via `MEDIA_URL` in development.

## Sample data
Run `python manage.py seed_demo`. The command creates specialties and seven example doctors. Add photos using **Manage doctors → Add doctor**.

## Architecture rule
Django owns saved doctors, appointments, validation, booking conflicts, and persistence. HTMX requests and swaps server-rendered HTML partials. Alpine owns local UI state only: menu open/closed, tabs, booking wizard step, theme preference, and toast messages.

## Alpine component inventory
| Component | Page | State/getters | Scope/store |
|---|---|---|---|
| Navbar | All | `menuOpen` | local `x-data` |
| Search clear button | Directory | `searchText` | local `x-data` |
| Doctor quick view | Directory | `quick` | local per-card `x-data` |
| Booking wizard | Booking | `step`, `reasonLength`, `canAdvance`, `stepLabel` | reusable `Alpine.data()` |
| Appointment status tabs | Appointment management | `active`, `statuses`, computed `counts` | reusable `Alpine.data()` |
| Theme | All | `dark`, `toggle()` | shared `Alpine.store('theme')`, persisted in localStorage |
| Toasts | All | `items`, `add()` | shared `Alpine.store('toasts')` |

## State map
- Local state (`x-data`): menu state, quick-view hover state, active tabs, and current booking wizard step. These are transient UI concerns.
- Shared state (`Alpine.store`): theme and toast notifications, because multiple components/pages need to read or update them.
- Server-owned state: doctors, appointment records, selected slots that are available, form validation, appointment status, and booking conflicts remain in Django/database.

## HTMX and Alpine integration points
1. Directory search/filter/sort uses `hx-get` to request server-filtered HTML; Alpine only clears the search input.
2. Date changes use HTMX to refresh `#slot-container`; Django determines which slots are booked and disables them.
3. Booking form submits with `hx-post`, includes the CSRF token, swaps validation fields on errors, and uses `HX-Redirect` on success.
4. `htmx:beforeRequest` / `htmx:afterRequest` toggle the page loading class.
5. A `toast` event can be dispatched from an HTMX response and handled by the Alpine toast store.
6. Alpine wizard state is placed outside the swapped `#booking-fields` region so the step component remains mounted when form errors are swapped.

## Important implementation notes
- The project is a practical starter, not a production deployment. Review security, permissions, email delivery, and production static/media hosting before deployment.
- The model-level unique constraint prevents duplicate doctor/date/slot bookings even if two requests race.
- The provided Word document includes **illustrative UI preview images** for planning evidence. They are not screenshots from a running Django server. Replace them with genuine screenshots after running and testing locally.
- Run `python manage.py test` after setup. Confirm every checklist item manually and record only verified results in the report.
