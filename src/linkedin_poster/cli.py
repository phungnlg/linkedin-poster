"""Typer CLI commands."""

import asyncio
import os
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from linkedin_poster.auth.oauth import OAuthFlow
from linkedin_poster.auth.token_store import TokenStore
from linkedin_poster.config import Settings
from linkedin_poster.services.post_service import PostService
from linkedin_poster.services.history import HistoryStore
from linkedin_poster.services.scheduler import Scheduler
from linkedin_poster.services.template_engine import TemplateEngine
from linkedin_poster.models.post import PostContent
from linkedin_poster.models.schedule import ScheduledPost

app = typer.Typer(
    name="linkedin-poster",
    help="CLI tool for auto-generating and posting LinkedIn content from GitHub POC projects.",
    no_args_is_help=True,
)
auth_app = typer.Typer(help="Authentication commands.")
post_app = typer.Typer(help="Post management commands.")
schedule_app = typer.Typer(help="Scheduling commands.")

app.add_typer(auth_app, name="auth")
app.add_typer(post_app, name="post")
app.add_typer(schedule_app, name="schedule")

console = Console()


# --- Auth commands ---


@auth_app.command("login")
def auth_login(
    token: Optional[str] = typer.Option(None, "--token", "-t", help="Paste base64 token from edge callback"),
):
    """Authenticate with LinkedIn via OAuth 2.0."""
    if token:
        # Edge function mode: decode pasted token
        import base64
        import json
        try:
            token_data = json.loads(base64.b64decode(token).decode())
            store = TokenStore()
            store.save(token_data)
            console.print("[green]Login successful! (from edge callback)[/green]")
        except Exception as e:
            console.print(f"[red]Invalid token: {e}[/red]")
            raise typer.Exit(1)
        return

    settings = Settings.load()
    error = settings.validate_credentials()
    if error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)

    console.print("Opening browser for LinkedIn login...")
    flow = OAuthFlow(settings)
    try:
        flow.run_login()
        console.print("[green]Login successful![/green]")
    except Exception as e:
        console.print(f"[red]Login failed: {e}[/red]")
        raise typer.Exit(1)


@auth_app.command("status")
def auth_status():
    """Show current authentication status."""
    store = TokenStore()
    data = store.load()
    if data:
        person_urn = data.get("person_urn", "unknown")
        saved_at = data.get("saved_at", "unknown")
        console.print(f"[green]Authenticated[/green]")
        console.print(f"  Person URN: {person_urn}")
        console.print(f"  Token saved: {saved_at}")
    else:
        console.print("[yellow]Not authenticated. Run 'auth login' first.[/yellow]")


@auth_app.command("logout")
def auth_logout():
    """Clear stored tokens."""
    store = TokenStore()
    store.clear()
    console.print("[green]Tokens cleared.[/green]")


# --- Post commands ---


@post_app.command("create")
def post_create(
    text: str = typer.Argument(..., help="Post text content"),
    org: Optional[str] = typer.Option(None, "--org", help="Organization ID to post as company page"),
):
    """Publish a text post to LinkedIn. Use --org to post to company page."""
    org_id = org or os.getenv("LINKEDIN_ORG_ID")
    service = PostService()
    try:
        post_urn = asyncio.run(service.publish_text(text, org_id=org_id))
        target = f"org:{org_id}" if org_id else "personal"
        console.print(f"[green]Post published ({target})![/green] URN: {post_urn}")
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        raise typer.Exit(1)


@post_app.command("from-poc")
def post_from_poc(
    config: str = typer.Argument(..., help="Path to POC config JSON file"),
    template: str = typer.Option("poc_showcase", "--template", "-t", help="Template name"),
    images: bool = typer.Option(False, "--images", "-i", help="Upload screenshots"),
    org: Optional[str] = typer.Option(None, "--org", help="Organization ID to post as company page"),
):
    """Generate and publish a POC showcase post. Use --org to post to company page."""
    org_id = org or os.getenv("LINKEDIN_ORG_ID")
    service = PostService()
    try:
        post_urn = asyncio.run(service.publish(config, template, with_images=images, org_id=org_id))
        target = f"org:{org_id}" if org_id else "personal"
        console.print(f"[green]Post published ({target})![/green] URN: {post_urn}")
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        raise typer.Exit(1)


@post_app.command("draft")
def post_draft(
    text: Optional[str] = typer.Argument(None, help="Text content (omit for POC mode)"),
    from_poc: Optional[str] = typer.Option(None, "--from-poc", help="POC config JSON file"),
    template: str = typer.Option("poc_showcase", "--template", "-t", help="Template name"),
):
    """Preview a post without publishing."""
    service = PostService()
    if from_poc:
        service.draft(from_poc, template)
    elif text:
        service.draft_text(text)
    else:
        console.print("[red]Provide text or --from-poc config path.[/red]")
        raise typer.Exit(1)


@post_app.command("list")
def post_list():
    """Show post history."""
    history = HistoryStore()
    records = history.list_records()
    if not records:
        console.print("[yellow]No posts yet.[/yellow]")
        return

    table = Table(title="Post History")
    table.add_column("Date", style="cyan")
    table.add_column("URN", style="green")
    table.add_column("Template")
    table.add_column("Preview")

    for r in records:
        table.add_row(
            str(r.created_at)[:19],
            r.post_urn[:40],
            r.template_name or "-",
            r.text_preview[:50] + "..." if len(r.text_preview) > 50 else r.text_preview,
        )

    console.print(table)


@post_app.command("templates")
def post_templates():
    """List available post templates."""
    names = TemplateEngine.list_templates()
    for name in names:
        console.print(f"  - {name}")


# --- Schedule commands ---


@schedule_app.command("add")
def schedule_add(
    config: str = typer.Argument(..., help="POC config JSON file"),
    at: str = typer.Option(..., "--at", help="Schedule time (YYYY-MM-DD HH:MM)"),
    template: str = typer.Option("poc_showcase", "--template", "-t", help="Template name"),
):
    """Schedule a POC post for later."""
    try:
        scheduled_at = datetime.strptime(at, "%Y-%m-%d %H:%M")
    except ValueError:
        console.print("[red]Invalid date format. Use YYYY-MM-DD HH:MM[/red]")
        raise typer.Exit(1)

    service = PostService()
    poc = service.load_poc_config(config)
    text = service.generate_text(poc, template)

    post = ScheduledPost(
        post_content=PostContent(commentary=text, article_url=poc.github_url),
        scheduled_at=scheduled_at,
        poc_config_path=config,
        template_name=template,
    )

    scheduler = Scheduler()
    schedule_id = scheduler.add(post)
    console.print(f"[green]Scheduled![/green] ID: {schedule_id}, at: {at}")


@schedule_app.command("list")
def schedule_list():
    """Show pending scheduled posts."""
    scheduler = Scheduler()
    pending = scheduler.list_pending()
    if not pending:
        console.print("[yellow]No pending posts.[/yellow]")
        return

    table = Table(title="Scheduled Posts")
    table.add_column("ID", style="cyan")
    table.add_column("Scheduled At", style="green")
    table.add_column("Template")
    table.add_column("Config")
    table.add_column("Preview")

    for p in pending:
        table.add_row(
            p.id,
            str(p.scheduled_at)[:16],
            p.template_name or "-",
            p.poc_config_path or "-",
            p.post_content.commentary[:40] + "...",
        )

    console.print(table)


@schedule_app.command("run")
def schedule_run():
    """Execute all due scheduled posts (for cron use)."""
    scheduler = Scheduler()
    due = scheduler.get_due()
    if not due:
        console.print("No posts due.")
        return

    service = PostService()
    for post in due:
        try:
            if post.poc_config_path:
                post_urn = asyncio.run(
                    service.publish(post.poc_config_path, post.template_name or "poc_showcase")
                )
            else:
                post_urn = asyncio.run(service.publish_text(post.post_content.commentary))
            scheduler.mark_published(post.id)
            console.print(f"[green]Published[/green] {post.id} -> {post_urn}")
        except Exception as e:
            console.print(f"[red]Failed {post.id}: {e}[/red]")
