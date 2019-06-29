# sbwoaservice-documentation


## introduction
The sbwoaservices are REST-services using the sanic-framework in combination
with pydantic. The services are developed inside conda environment and rolled
out as docker-containers. For testings the pytest-package is used. The
documentation is served as a combination of mkdocs and swagger.


## commands

* `mkdocs build && mkdocs serve`: recreates and serves the documentation for
  the service.
* `conda build . --python=<PYTHON-VERSION>`: create a conda package for the
  service. IMPORTANT: Please ensure to add a new git-tag for your service
  before. For correct versioning use semantic-versioning style.
* `cenv -ay`: create / update the conda environment for the service.
* `create_docu --project_name <servicename>`: create / update the
  documentation for the service.


## relevant and helpful links


### links for sbwoaservices

* if you run your service, the swagger-documentation can be accessed on
  `http://<hostname>:<port>/swagger`


### links for tools, packages and frameworks

* [sanic-documentation](https://sanic.readthedocs.io/en/latest/index.html)
* [mkdocs-documentation](https://www.mkdocs.org/)
* [sanic-openapi-documentation](https://github.com/huge-success/sanic-openapi)
* [pydantic-documentation](https://pydantic-docs.helpmanual.io/#)
* [REST-definition](https://en.wikipedia.org/wiki/Representational_state_transfer)
* [pytest-documentation](https://docs.pytest.org/en/latest/)
* toolz
* itertools
* functools
* more-itertools
* conda
* docker
* docker-compose
* asyncio
* GitLab-CI


### links for workflows, code-styles, etc.

* git-workflow
* decorators
* functional programming
* toolz
* semantic-versioning
* concurrency
* CI / CD
* pep8
* changelog
