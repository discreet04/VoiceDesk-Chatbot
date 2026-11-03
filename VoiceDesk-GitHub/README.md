# VoiceDesk
A Django + Django REST Framework campus helpdesk with a responsive HTML/CSS/JavaScript frontend.

## Run locally (PowerShell)
```powershell
python -m venv .venv
python -m pip --python .venv install -r requirements.txt
.\.venv\Scripts\python.exe scripts/download_model.py
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```
Open http://127.0.0.1:8000. Demo accounts: **student** or **staff**, password **VoiceDesk123!**. Demo tickets and FAQ entries are clearly sample content. The seed command is idempotent and does not change existing passwords.

## Features
- Session login, CSRF protection, student-owned tickets, and staff queue.
- Click Speak to record from your microphone, then Stop and Send. Audio is transcribed locally with Whisper; no API key or browser speech service is required. English and Hindi speech are detected automatically.
- Complaint extraction, follow-up questions, editable confirmation, and explicit submission.
- English/Hindi/Hinglish keyword parser without a key; optional LLM extraction with a key.
- Spoken responses via browser speech synthesis; available Hindi voices depend on the device.
- Duplicate warnings for open complaints with the same category and exact normalized location. Reports remain separate; no automatic merging.
- Ticket status/history and voice/text status queries with ownership checks.
- Staff upload of UTF-8 .txt/.md FAQs, separated into paragraphs. Answers use keyword retrieval and cite the source; unsupported questions get a fallback instead of a fabricated answer.
- Conversation history persisted per account; “New conversation” resets the current draft and screen, preserving history.

## AI configuration
Set environment variables before starting Django. No secrets belong in source files.
```powershell
$env:OPENAI_API_KEY = "<your-key>"
$env:OPENAI_TEXT_MODEL = "gpt-4.1-mini"
$env:OPENAI_TRANSCRIBE_MODEL = "whisper-1"
```
The Speak button records audio and sends it to the Django server for local Whisper transcription. Run scripts/download_model.py once with internet access to download the multilingual base model. Subsequent transcription runs locally on the server CPU without an API key. Microphone permission is required. An optional OPENAI_API_KEY enables LLM complaint extraction; without it, transcripts use the deterministic complaint parser. Spoken replies use browser speech synthesis.

References: [file transcription](https://developers.openai.com/api/docs/guides/speech-to-text), [text generation](https://developers.openai.com/api/docs/guides/text).

## PostgreSQL
SQLite is the local default. Set POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, and POSTGRES_PORT, then run migrations again. PostgreSQL support is configured but has not been integration-tested against a running PostgreSQL service.

## Checks
```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
node --check static/app.js
node --test tests/speech.test.cjs
```
Tests cover confirmation before creation, follow-ups, duplicate detection, role authorization, ticket privacy, status queries, FAQ retrieval, audio validation, and login CSRF.

## Deployment notes
This is a local MVP, not a production deployment. Use a Django-capable host (Sites/Cloudflare Workers does not execute Django), a production WSGI/ASGI server, HTTPS, static-file serving, a strong DJANGO_SECRET_KEY, DJANGO_DEBUG=0, and DJANGO_ALLOWED_HOSTS. Do not seed demo credentials on a public deployment. Add authentication/API rate limits, college SSO or account provisioning, operational logging, and a data-retention policy before a campus rollout. Configure real campus FAQ content. API calls and microphone capture require network connectivity and browser permission. Live streaming conversation is deliberately outside this recorded-message MVP.
