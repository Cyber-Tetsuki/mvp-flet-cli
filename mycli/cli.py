import sys
import typer
import copier
import os
import inflection

app = typer.Typer()


@app.command()
def hello(name: str):
    print("Hello", name)


@app.command()
def create(
        project_name: str = typer.Option(..., "--proj-name"),
        dst_folder: str = typer.Option(os.getcwd(), "--dist-path"),
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


def create_python_file(path: str, content: str):
    try:
        with open(path, "w") as f:
            f.write(content)
    except Exception as e:
        print(e)


@app.command()
def create_view(view_name: str = typer.Option(..., "--name")):
    cwd = os.getcwd()
    class_name = inflection.camelize(view_name, uppercase_first_letter=True)
    view_content = f"""
    import flet as ft
    from flet.core.types import MainAxisAlignment, CrossAxisAlignment
    from model import EnvModel
    from typing import Optional, TYPE_CHECKING
    
    if TYPE_CHECKING:
        from presenter import {class_name}Presenter
    
    
    class AppView:
        def __init__(self, env: EnvModel):
            self._env = env
            self._presenter: Optional["{class_name}Presenter"] = None
    """

    presenter_content = f"""
        from views import {class_name}View

        class AppPresenter:
            def __init__(self,view : {class_name}View):
                self._view = view

    """

    view_path = cwd + "/views/" + view_name + "_view.py"
    presenter_path = cwd + "/presenter/" + view_name + "_view.py"

    create_python_file(view_path, view_content)
    create_python_file(presenter_path, presenter_content)


def main():
    app()
