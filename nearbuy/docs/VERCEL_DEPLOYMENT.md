# NEARBUY Vercel deployment

## Architecture

- Flask application: Vercel Python Function, auto-detected from `app.py`.
- Static assets: `public/static/`, served by Vercel's CDN at `/static/`.
- Templates and translations: bundled from `templates/` and `locales/`.
- Persistent data: managed PostgreSQL via `DATABASE_URL`.
- Desktop edition: unchanged local SQLite database and Waitress server.

## Required Vercel environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection URL. Use a provider's pooled URL if available and require SSL where the provider recommends it. |
| `SECRET_KEY` | Long random Flask session-signing key. Keep it stable between deployments. |
| `INITIAL_ADMIN_TOKEN` | Owner-only token required to create the first administrator. Remove after setup is complete. |

Generate each secret independently with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

## Deploy

1. Push the contents of the `nearbuy/` project folder to a Git repository. The files `app.py`, `requirements.txt`, `vercel.json`, `pyproject.toml`, `templates/`, `locales/` and `public/` must be at repository root.
2. Import the repository in Vercel. Set Root Directory to the repository root.
3. Add the three environment variables above to the target Vercel environments.
4. Deploy and visit the deployment URL.
5. Complete first-time setup using the `INITIAL_ADMIN_TOKEN`, then create a strong admin password.
6. Remove `INITIAL_ADMIN_TOKEN` from Vercel and redeploy after the first administrator exists.
7. Test `/health`, sign-in, shop registration, admin approval, product creation and a test order.

## Important

Vercel's function filesystem is temporary. Do not use SQLite for hosted production data. The app deliberately refuses to start in Vercel mode without `DATABASE_URL` and `SECRET_KEY`. Database backups, provider availability and access controls are the operator's responsibility. The app's current startup schema creation is suitable for this prototype; use a controlled migration process before a high-traffic production launch.
