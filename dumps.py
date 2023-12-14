import importlib
import pathlib

import click

md_base_template = """
```bash
{help}
```
"""

md_home_template = """
# bkm-sage 运维锦囊工具主目录

|模块|工具|作用|
|--|--|--|
{toc}
"""


def recursive_help(cmd, parent=None):
    """从 command 命令中迭代中 help 内容"""
    ctx = click.core.Context(cmd, info_name=cmd.name, parent=parent)
    yield {"command": cmd, "help": cmd.get_help(ctx), "is_parent": True if parent is None else False, "ctx": ctx}
    commands = getattr(cmd, "commands", {})
    for sub in commands.values():
        for help_dct in recursive_help(sub, ctx):
            yield help_dct


def dump_helper(base_command, docs_dir):
    """将 help 内容导出至 md 文件"""
    docs_path = pathlib.Path(docs_dir)
    # 判断目录是否存在
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=False)
    for help_dct in recursive_help(base_command):
        help_txt = help_dct.get("help")
        command_name = str(help_dct.get("command").name)
        is_parent = help_dct.get("is_parent")
        if is_parent:
            ctx = help_dct.get("ctx")
            toc = ""
            for child_command_name, child_command in ctx.command.commands.items():
                module_name = child_command_name.split("-")[0]
                toc += f"|{module_name}|[{child_command_name}](https://github.com/canway/bkm-sage/wiki/{child_command_name})|{child_command.short_help}|\n"
            md_template = md_home_template.format(toc=toc)
            md_file_path = docs_path.joinpath("HOME.md").absolute()
        else:
            md_template = md_base_template.format(
                command_name=command_name,
                help=help_txt,
            )
            md_file_path = docs_path.joinpath(command_name.lower() + ".md").absolute()

        # Create the file per each command
        with open(md_file_path, "w") as md_file:
            md_file.write(md_template)


@click.group()
def cli():
    """
    Example:

        python dumps.py dumps --module=main --command=bkm --docPath=../bk-sage.wiki
        需要注意的是，docPath 需要填写为 GitHub wiki locally 的地址
    """
    pass


@cli.command("dumps")
@click.option("--module", default="main", help="模块文件，在本项目中默认为main", required=False)
@click.option("--command", default="bkm", help="命令名，在本项目中默认为bkm", required=False)
@click.option("--docPath", help="帮助文档路径，需要设置为 GitHub wiki locally 的目录地址", required=True)
def dumps(**kwargs):
    """
    创建 md 文件，并将目标命令及子命令的帮助文档导出输出至指定目录: docsPath 下
    """
    base_module = kwargs.get("module")
    base_command = kwargs.get("command")
    docs_path = kwargs.get("docpath")

    click.secho(f"Creating a new documents from {base_module}.{base_command} into {docs_path}", color="green")

    try:
        # Import the module
        module_ = importlib.import_module(base_module)
    except Exception as e:
        click.echo(f"Could not find module: {base_module}. Error: {str(e)}")
        return

    try:
        command_ = getattr(module_, base_command)
    except Exception as e:
        click.echo(f"Could not find command {base_command} on module {base_module}")
        return

    try:
        dump_helper(command_, docs_dir=docs_path)
        click.secho(f"Created docs under {docs_path}", color="green")
    except Exception as e:
        click.secho(f"Dumps command failed: {str(e)}", color="red")
        raise

    return


if __name__ == "__main__":
    cli()
