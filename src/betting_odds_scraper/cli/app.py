import typer

from betting_odds_scraper.cli.commands.scrape import scrape_app


app = typer.Typer(no_args_is_help=True)
app.add_typer(scrape_app, name="scrape")


def main() -> None:
    app()
