import json

import click
from pathlib import Path

@click.group()
@click.version_option('0.1.0')
def cli():
    pass

@cli.command()
@click.argument('url')
@click.option('--job-id', default=None, help='Optionale Job-ID')
def clone(url, job_id):
    from backend.analyzer.cloner import clone_repo
    path = clone_repo(url, job_id)
    click.echo(f'✅ Geklont nach: {path}')

@cli.command()
@click.argument('repo_path')
@click.argument('repo_url')
@click.option('--output', '-o', default='analysis.json')
def analyze(repo_path, repo_url, output):
    from backend.analyzer.unified_analyzer import analyze as run_analysis
    result = run_analysis(Path(repo_path), repo_url)
    Path(output).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    click.echo(f'✅ Analyse gespeichert: {output}')

if __name__ == '__main__':
    cli()
