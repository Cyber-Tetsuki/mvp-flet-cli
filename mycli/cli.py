import sys
import traceback
from tkinter.font import names

import typer
import copier
import os
import inflection
import textwrap
from jinja2 import Template

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


def append_in_init_file(path: str, file_name: str, class_name: str):
    try:
        if not os.path.exists(path):
            os.makedirs(path)

        init_path = path + "/__init__.py"
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("")

        with open(init_path, "r") as f:
            content = textwrap.dedent(f.read())

        content = content + "\n" + f"from .{file_name.removesuffix('.py')} import {class_name}"

        with open(init_path, "w") as f:
            f.write(content)

    except Exception as e:
        typer.echo(e)
        typer.echo(traceback.format_exc())


def append_rs_in_factory(name: str):
    try:
        service_name = name + "_service"
        repos_name = name + "_repos"
        repos_class_name = inflection.camelize(f"{name}Repos", uppercase_first_letter=True)
        service_class_name = inflection.camelize(f"{name}Service", uppercase_first_letter=True)
        path = "factory.py"
        content = open(path).read()
        new_content = textwrap.dedent(f"""
        from services import {service_class_name}
        from db.repository import {repos_class_name}
        """)

        for index, line in enumerate(content.splitlines()):
            if "append here. ps. ###dont remove this comment" in line:
                line += "\n" + "{{ init_code }}"
            new_content += "\n" + line

        template = Template(new_content)

        init_code = f"""
        self._{repos_name} = {repos_class_name}(self._env,self._db)
        self._{service_name} = {service_class_name}(self._{repos_name})
        """
        final_content = template.render(init_code=init_code)

        with open(path, "w") as f:
            f.write(final_content)
    except Exception as e:
        typer.echo(e)
        typer.echo(traceback.format_exc())


def append_in_main_routing(name: str):
    try:
        path = "main.py"
        content = open(path).read()
        view_name = f"create_{name.removesuffix('.py')}_view"
        new_route = f'\t\t"/{name.removesuffix(".py")}" : lambda : factory.{view_name}()'
        new_content = ""
        for index, line in enumerate(content.splitlines()):
            if "append here. ps. ###dont remove this comment" in line:
                line += "\n" + "{{ route_code }},"
            new_content += "\n" + line

        template = Template(new_content)

        final_content = template.render(route_code=new_route)

        with open(path, "w") as f:
            f.write(final_content)
    except Exception as e:
        typer.echo(e)
        typer.echo(traceback.format_exc())


def append_vp_in_factory(name: str, folder: str):
    try:
        view_name = name + "_view"
        presenter_class_name = inflection.camelize(f"{name}Presenter", uppercase_first_letter=True)
        view_class_name = inflection.camelize(f"{name}View", uppercase_first_letter=True)
        path = "factory.py"
        content = open(path).read()
        new_content = textwrap.dedent(f"""
        from views import {view_class_name}
        from presenter import {presenter_class_name}
        """)
        if folder:
            new_content = textwrap.dedent(f"""
                   from views.{folder} import {view_class_name}
                   from presenter.{folder} import {presenter_class_name}
                   """)

        for index, line in enumerate(content.splitlines()):
            if index == len(content.splitlines()) - 1:
                line += "\n \t\t{{ func_code }}"

            new_content += "\n" + line

        template = Template(new_content)

        new_func = f"""
    def create_{view_name.removesuffix('.py')}(self):
        view = {view_class_name}(self._env)
        presenter = {presenter_class_name}(view)
        view._presenter = presenter
        self._current_view = view
        return view.build()
        """

        final_content = template.render(func_code=new_func)

        with open(path, "w") as f:
            f.write(final_content)
    except Exception as e:
        typer.echo(e)
        typer.echo(traceback.format_exc())


def create_python_file(path: str, content: str):
    try:
        with open(path, "w") as f:
            f.write(content)
    except Exception as e:
        typer.echo(e)
        typer.echo(traceback.format_exc())


@app.command()
def create_presenter(name: str = typer.Option(..., "--name"), folder=typer.Option(None, "--folder")):
    cwd = os.getcwd()
    presenter_class_name = inflection.camelize(f"{name}Presenter", uppercase_first_letter=True)
    view_class_name = inflection.camelize(f"{name}View", uppercase_first_letter=True)
    presenter_content = textwrap.dedent(
        f"""
                from views import {view_class_name}

                class {presenter_class_name}:
                    def __init__(self,view : {view_class_name}):
                        self._view = view

            """
    )
    if folder:
        presenter_content = textwrap.dedent(
            f"""
                        from views.{folder} import {view_class_name}

                        class {presenter_class_name}:
                            def __init__(self,view : {view_class_name}):
                                self._view = view

                    """
        )

    file_name = name + "_presenter.py"
    presenter_path = cwd + "/presenter/"
    if folder:
        presenter_path += f"/{folder}/"
        if not os.path.exists(presenter_path):
            os.makedirs(presenter_path)

    file_path = presenter_path + file_name
    create_python_file(file_path, presenter_content)
    append_in_init_file(presenter_path, file_name, presenter_class_name)

    typer.echo("Created Presenter File")


@app.command()
def create_view(name: str = typer.Option(..., "--name"), folder=typer.Option(None, "--folder")):
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

    if folder:
        view_content = textwrap.dedent(
            f"""
               import flet as ft
               from flet.core.types import MainAxisAlignment, CrossAxisAlignment
               from model import EnvModel
               from typing import Optional, TYPE_CHECKING

               if TYPE_CHECKING:
                   from presenter.{folder} import {presenter_class_name}


               class {view_class_name}:
                   def __init__(self, env: EnvModel):
                       self._env = env
                       self._presenter: Optional["{presenter_class_name}"] = None
                   
                   def on_rendered(self):
                       pass
                       
                   def build(self):
                       return ft.View()
               """
        )

    file_name = name + "_view.py"
    view_path = cwd + "/views/"
    if folder:
        view_path += f"/{folder}/"
        if not os.path.exists(view_path):
            os.makedirs(view_path)

    file_path = view_path + file_name
    create_python_file(file_path, view_content)
    append_in_init_file(view_path, file_name, view_class_name)

    typer.echo("Created View File")


@app.command()
def create_vp(name: str = typer.Option(..., "--name"), folder=typer.Option(None, "--folder")):
    create_view(name, folder)
    create_presenter(name, folder)
    append_vp_in_factory(name, folder)
    append_in_main_routing(name)


@app.command()
def create_service(name: str = typer.Option(..., "--name")):
    cwd = os.getcwd()
    service_class_name = inflection.camelize(f"{name}Service", uppercase_first_letter=True)
    repos_class_name = inflection.camelize(f"{name}Repos", uppercase_first_letter=True)
    service_content = textwrap.dedent(
        f"""
            from typing import TYPE_CHECKING

            if TYPE_CHECKING:
                from db.repository import {repos_class_name}
            
            
            class {service_class_name}:
                def __init__(self, {name.removesuffix('.py')}_repos: '{repos_class_name}'):
                    self._{name.removesuffix('.py')}_repos = setting_repos

          """
    )

    file_name = name + "_service.py"
    view_path = cwd + "/services/"
    file_path = view_path + file_name
    create_python_file(file_path, service_content)
    append_in_init_file(view_path, file_name, service_class_name)

    typer.echo("Created Service File")


@app.command()
def create_repos(name: str = typer.Option(..., "--name")):
    cwd = os.getcwd()
    repos_class_name = inflection.camelize(f"{name}Repos", uppercase_first_letter=True)
    repos_content = textwrap.dedent(
        f"""
            import traceback
            from datetime import datetime
            from typing import TYPE_CHECKING
            from sqlalchemy import select, and_, update, insert
            from sqlalchemy.orm import joinedload
            from utils.logs import Logging
            
            if TYPE_CHECKING:
                from model import EnvModel
                from db import Database
            
            
            class {repos_class_name}:
                def __init__(self, env: 'EnvModel', db: "Database"):
                    self._env = env
                    self._db = db
                    self._logger = Logging()
                    self._db.build()
            """
    )

    file_name = name + "_repos.py"
    view_path = cwd + "/db/repository/"
    file_path = view_path + file_name
    create_python_file(file_path, repos_content)
    append_in_init_file(view_path, file_name, repos_class_name)

    typer.echo("Created Repos File")


@app.command()
def create_rs(name: str = typer.Option(..., "--name")):
    create_repos(name)
    create_service(name)
    append_rs_in_factory(name)


def main():
    app()
