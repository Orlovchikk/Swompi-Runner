import click
from swompi.functions import create_repo, delete_repo, get_all_repos
from swompi.session import SessionLocal as db_session_factory

@click.group()
def cli():
    pass

@cli.command()
def ls():
    with db_session_factory() as db_session:
        repos = get_all_repos(db_session)
        for n in range(len(repos)):
            click.echo(f"{n+1}. {repos[n].name} {repos[n].url}. Created at: {repos[n].created_at}")

@cli.command()
@click.argument("url", nargs=1)
@click.argument("name", nargs=1)
def create(url, name):
    if url.startswith("https://github.com/"):
        with db_session_factory() as db_session:
            create_repo(db_session, url, name)
            click.echo("Url succesfully added")

    else:
        click.echo("Url must start with \"https://github.com/\"")

@cli.command()
@click.argument("url")
def delete(url):
    with db_session_factory() as db_session:
        if delete_repo(db_session, url):
            click.echo("Url was deleted")
        else:
            click.echo("Url not found")
    
if __name__ == '__main__':
    cli()