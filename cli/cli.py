import sys

import typer
from typer import Typer
import copier

app = Typer()


@app.command()
def create(project_name: str = typer.Option(..., "--proj-name"),
           dst_folder: str = typer.Option(..., "--dist-path")) -> None:
    template_url = "https://github.com/Cyber-Tetsuki/mvp-flet"
    default = {
        "project_name": project_name,
        "python_path": sys.executable,
        "dst_path": dst_folder,
    }

    copier.run_copy(
        src_path=template_url,
        dst_path=dst_folder,
        data=default,
        unsafe=True,
    )

    print("MVP Flet App Created")


@app.command()
def hello(name: str):
    print("Hello ", name)
