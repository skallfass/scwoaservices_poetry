from argparse import ArgumentParser
import os
from pathlib import Path

MKDOCS_TEMPLATE = """
site_name: {project_name}
theme: readthedocs
nav:
    - Home: index.md
    - reference:
        - {project_name}: {project_name}.md
"""


def creating_docs_folder(current_path):
    docs_folder = current_path / 'docs'
    if not docs_folder.exists():
        print('created docs folder ...')
        docs_folder.mkdir()
        (docs_folder /
         'index.md').write_text('place your introduction and overview here')


def creating_mkdocs_file(current_path, mkdocs_template):
    mkdocs_file = current_path / 'mkdocs.yml'
    if not mkdocs_file.exists():
        print('creating mkdocs.yml ...')
        mkdocs_file.write_text(mkdocs_template)


def creating_docu(project_name, current_path):
    print('creating docu ...')
    create_docu_command = '+ '.join([
        str(module.relative_to(current_path)).replace('.py',
                                                      '').replace('/', '.')
        for module in current_path.rglob('*.py')
        if 'setup.py' not in str(module)
    ])
    os.system(
        f'pydocmd simple {create_docu_command}+ > docs/{project_name}.md')
    os.system('mkdocs build')


def parse_options():
    parser = ArgumentParser()
    parser.add_argument('-p', '--project_name', required=True)
    return parser.parse_args()


def main():
    options = parse_options()
    current_path = Path.cwd()
    creating_docs_folder(current_path)
    creating_mkdocs_file(current_path=current_path,
                         mkdocs_template=MKDOCS_TEMPLATE.format(
                             project_name=options.project_name))
    creating_docu(project_name=options.project_name, current_path=current_path)


if __name__ == '__main__':
    main()
