# LinkedIn Auto-Poster CLI

CLI tool for auto-generating and posting LinkedIn content showcasing GitHub POC projects.

## What This Demonstrates

- **LinkedIn REST API v2** (`/rest/posts`) - latest API with OAuth 2.0 3-legged flow
- **Python CLI architecture** - Typer + Rich for beautiful terminal output
- **Async HTTP** - httpx with rate limit retry, respx for test mocking
- **Data modeling** - Pydantic v2 for validation and JSON serialization
- **Template engine** - pluggable templates for different post formats
- **Scheduling** - JSON-based schedule with cron runner

## Architecture

```
src/linkedin_poster/
├── cli.py                 # Typer CLI commands
├── config.py              # Settings, env loading
├── auth/                  # LinkedIn OAuth 2.0 flow
│   ├── oauth.py           # 3-legged auth with local callback server
│   └── token_store.py     # Token persistence to JSON
├── api/                   # LinkedIn API client
│   ├── client.py          # Async httpx with retry on 429
│   ├── posts.py           # Create text/image/article posts
│   └── images.py          # Image upload flow
├── services/              # Business logic
│   ├── post_service.py    # Orchestrates post creation
│   ├── template_engine.py # Template rendering
│   ├── scheduler.py       # JSON schedule + cron runner
│   └── history.py         # Post history + dedup
├── models/                # Pydantic data models
│   ├── poc.py             # PocProject
│   ├── post.py            # PostContent, PostRecord
│   └── schedule.py        # ScheduledPost
└── templates/             # Post templates
    ├── poc_showcase.py     # Full project highlight
    ├── tech_insight.py     # Learning/insight format
    └── project_update.py   # Progress update format
```

## Commands

| Command | Description |
|---------|-------------|
| `auth login` | Authenticate with LinkedIn via OAuth 2.0 |
| `auth status` | Show current authentication status |
| `auth logout` | Clear stored tokens |
| `post create "text"` | Publish a text post |
| `post from-poc config.json` | Generate and publish POC showcase |
| `post draft "text"` | Preview a text post |
| `post draft --from-poc config.json` | Preview POC showcase |
| `post list` | Show post history |
| `post templates` | List available templates |
| `schedule add config.json --at "2026-03-27 10:00"` | Schedule a post |
| `schedule list` | Show pending scheduled posts |
| `schedule run` | Execute due posts (for cron) |

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v2/userinfo` | GET | Get authenticated user info |
| `/rest/posts` | POST | Create a post (text, image, article) |
| `/rest/posts/{id}` | DELETE | Delete a post |
| `/rest/images?action=initializeUpload` | POST | Initialize image upload |
| Upload URL (pre-signed) | PUT | Upload image binary |

## POC Config Format

```json
{
  "name": "Project Name",
  "github_url": "https://github.com/user/repo",
  "description": "Project description for the post.",
  "keywords": ["Python", "CLI", "API"],
  "screenshots": ["path/to/screenshot.png"],
  "tech_stack": ["Python", "httpx", "Typer"],
  "demo_url": "https://demo.example.com"
}
```

## Setup

1. Create a LinkedIn Developer App at https://developer.linkedin.com
2. Add `http://localhost:8080/callback` as an authorized redirect URL
3. Request the following products/scopes: `openid`, `profile`, `w_member_social`

```bash
cp .env.example .env
# Edit .env with your LinkedIn app credentials
```

## Install & Run

```bash
# Install in development mode
pip install -e ".[dev]"

# Authenticate
python -m linkedin_poster auth login

# Preview a POC post
python -m linkedin_poster post draft --from-poc poc_configs/safari-ad-blocker.json

# Publish
python -m linkedin_poster post from-poc poc_configs/safari-ad-blocker.json

# Schedule for later
python -m linkedin_poster schedule add poc_configs/safari-ad-blocker.json --at "2026-03-27 10:00"
```

## Cron Setup

To auto-publish scheduled posts, add to crontab:

```bash
*/5 * * * * cd /path/to/linkedin-poster && python -m linkedin_poster schedule run
```

## Build & Test

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```
