# Q-Transplant deployment checklist

## Required environment
- `JWT_SECRET`: long random secret; never commit it.
- `DATABASE_URL`: use PostgreSQL in production.
- `ORGANIZER_EMAIL` / `ORGANIZER_APP_PASSWORD`: SMTP sender credentials
  (a Gmail address + app password) used to deliver OTPs and notifications.
  Without these set, `/forgot-password`, email verification, and organizer
  notification emails silently fail to send (by design — the API never
  reveals whether an email exists, so a misconfigured mailer looks
  identical to "email not registered" from the client's perspective).
- `ORGANIZER_BOOTSTRAP_EMAIL` / `ORGANIZER_BOOTSTRAP_PASSWORD`: the very
  first organizer login. Organizer accounts can't self-register through
  `/register` (by design), so without these set, a fresh database has
  **no organizer account at all** and every organizer login attempt will
  fail with "Incorrect email or password" regardless of what's typed. Set
  these once, redeploy, then unset/rotate the password afterward — the
  bootstrap only ever creates the first organizer and never overwrites an
  existing one. Deliberately distinct from `ORGANIZER_EMAIL` above, which
  is only an SMTP sender identity, not a login.
- `GROQ_API_KEY` / `ANTHROPIC_API_KEY` (both optional): enable AI-assisted
  comparison of a doctor's live selfie against their submitted certificate
  photo during onboarding. If `GROQ_API_KEY` is set it's used (faster and
  cheaper for most accounts, via Groq's current vision model); otherwise
  `ANTHROPIC_API_KEY` is used if present. Without either set, document
  upload still works fine — the organizer just sees "not run" in the
  approvals table and reviews the two images manually instead. This check
  is always assistive, never authoritative; the organizer makes the actual
  approve/reject decision either way.
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
