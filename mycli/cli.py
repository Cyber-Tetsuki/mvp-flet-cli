import sys
import typer
import copier
import os
import inflection
import textwrap

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


def append_in_init(path: str, file_name: str, class_name: str):
    try:
        init_path = path + "/__init__.py"
        with open(init_path, "w") as f:
            content = textwrap.dedent(f.read())

        content = content + "\n" + f"from .{file_name} import {class_name}"

        with open(path, "w") as f:
            f.write(content)

    except Exception as e:
        typer.echo(e)


def create_python_file(path: str, content: str):
    try:
        with open(path, "w") as f:
            f.write(content)
    except Exception as e:
        typer.echo(e)


@app.command()
def create_presenter(name: str = typer.Option(..., "--name")):
    cwd = os.getcwd()
    presenter_class_name = inflection.camelize(f"{name}Presenter", uppercase_first_letter=True)
    view_class_name = inflection.camelize(name, uppercase_first_letter=True)
    presenter_content = textwrap.dedent(
        f"""
                from views import {view_class_name}View

                class {presenter_class_name}:
                    def __init__(self,view : {view_class_name}View):
                        self._view = view

            """
    )

    file_name = name + "_presenter.py"
    presenter_path = cwd + "/presenter/" + file_name
    create_python_file(presenter_path, presenter_content)
    append_in_init(presenter_path, file_name, presenter_class_name)


@app.command()
def create_view(name: str = typer.Option(..., "--name")):
    cwd = os.getcwd()
    presenter_class_name = inflection.camelize(f"{name}Presenter", uppercase_first_letter=True)
    view_class_name = inflection.camelize(f"{name}View", uppercase_first_letter=True)
    view_content = textwrap.dedent(
        f"""
        import flet as ft
        from flet.core.types import MainAxisAlignment, CrossAxisAlignment
        from model import EnvModel
        from typing import Optional, TYPE_CHECKING

        if TYPE_CHECKING:
            from presenter import {presenter_class_name}


        class {view_class_name}:
            def __init__(self, env: EnvModel):
                self._env = env
                self._presenter: Optional["{presenter_class_name}"] = None
            
            def build(self):
                return ft.View()
        """
    )

    file_name = name + "_view.py"
    view_path = cwd + "/views/" + file_name
    create_python_file(view_path, view_content)
    append_in_init(view_path, file_name, view_class_name)


def main():
    app()
