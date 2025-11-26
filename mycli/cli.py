import sys
import typer
import copier

app = typer.Typer()


@app.command()
def hello(name: str):
    print("Hello", name)


@app.command()
def create(
        project_name: str = typer.Option(..., "--proj-name", prompt=True),
        dst_folder: str = typer.Option(..., "--dist-path", prompt=True),
):
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


def main():
    app()
