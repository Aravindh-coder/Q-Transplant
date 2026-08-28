# Q-Transplant deployment checklist

## Required environment
- `JWT_SECRET`: long random secret; never commit it.
- `DATABASE_URL`: use PostgreSQL in production.
- `ORGANIZER_EMAIL` / `ORGANIZER_APP_PASSWORD`: SMTP sender credentials.
- `ALLOWED_ORIGINS`: comma-separated production frontend origins. Since the
  frontend (`public/`) is now served by this same FastAPI app, this is only
  needed if something else (an emergency device, a separate admin panel,
  local `npm run dev`, etc.) calls the API from a different origin.
- Configure OTP/login rate limits and token expiry for deployment.

## Production requirements
1. Run behind HTTPS and a reverse proxy/load balancer.
2. Use PostgreSQL and a real migration tool (Alembic recommended) instead of runtime schema creation.
3. Store uploads in private object storage or an encrypted private volume; serve through authorized backend download endpoints.
4. Run periodic encrypted database and document backups and test restoration regularly.
5. Run API workers behind a process manager/container platform.
6. Put long-running matching, email and backup work on a background worker/queue in production.
7. Centralize logs/metrics and alert on authentication, emergency, database, email and device failures.
8. Rotate SMTP, JWT and ESP32 device credentials periodically.
9. Keep OpenAPI available in development; protect or disable interactive docs in public production deployments as appropriate.
10. Run the full test suite, dependency audit and security review before clinical deployment.

## Medical safety
Q-Transplant provides decision support only. It must never instruct a user to perform a transplant. Final clinical decisions remain with qualified professionals and applicable authorities.

## Backup
Use an external encrypted backup destination, scheduled database dumps/snapshots and versioned document backups. The local helper in `app/services/backup.py` is a building block, not a substitute for encrypted off-host production backup infrastructure.
