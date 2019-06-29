## service-structure
A service based on `sbwoaservices` uses the following project-structure:
```bash
├── conda-build
│   └── meta.yaml
├── conda-packages
│   └── ...
├── docker-compose.yaml
├── Dockerfile
├── docs
│   ├── index.md
│   ├── <servicename>.md
│   └── usage.md
├── .gitignore
├── <servicename>
│   ├── blueprints
│   │   └── <api-name>_api.py
│   ├── errors.py
│   ├── models
│   │   ├── <api-name>_api.py
│   │   └── validators.py
│   ├── options.py
│   ├── processing
│   │   └── <api-name>_api.py
│   ├── README.md
│   ├── rules.py
│   ├── service.py
│   └── tests
│       └── ...
├── MANIFEST.in
├── mkdocs.yml
├── README.md
└── setup.py
```


### environment- / package-files
Files used to create the conda environment for this service are:

* `conda-build/meta.yaml`: this file is (in combination with the `setup.py`)
  file the blueprint for creation of the conda package for the service. It is
  also used to create the conda environment for the service in combination
  with the `cenv`-tool.
* `setup.py`: this file is required to create the conda package for this
  service.
* `MANIFEST.in`: if the service requires additional non-python files like
  `csv`-files, `yaml`-files, etc. these files have to be included inside this
  file.


### rollout-files
A service based on sbwoaservices is run inside a docker-container.
For this the following files are needed:

* `Dockerfile`: required to create the docker-image used to run the
  docker-container.
* `docker-compose.yaml`: this file defines how the docker-container should be
  run.
* `conda-packages`: this folder contains all self-build conda-packages required
  by the service to run.


### source-code
The source-code of the service is located in the `<servicename>`-folder.
A service requires the following modules:

* `<servicename>.blueprints.<api-name>`: this file contains an api to be
  served by the service.
* `<servicename>.errors`: all possible errors have to be defined here.
* `<servicename>.models.<api-name>`: the input- and output-model definitions
  for each api served by the service is defined in such a module.
* `<servicename>.models.validators`: inside this module all validators for
  the input- and output-models are defined.
* `<servicename>.options`: if the service requires some special non-default
  parameters on startup they have to be defined inside this file.
* `<servicename>.processing.<api-name>`: the logic for each api is defined
  inside such a module.
* `<servicename>.rules`: all servicerules, like the name of the service, which
  error-handler to use, are defined in this module.
* `<servicename>.service`: this module combines all definitions and functions
  of the other modules. How to run the service is defined inside this method.
  Also the blueprints for the service are loaded here.
* `<servicename>.tests`: this module contains all tests for the service.


### documentation
For the documentation of the service (to create the documentation-page, the
readme-file and the helptext for the argparse) the following files and folders
are required:

* `docs`: this folder contains all markdown files required to create the
  documentation-page. If you want to add additional sections you have to add
  a new markdown file here and also add this file to the `mkdocs.yml`.
* `docs/index.md`: this file defines the welcome page of the
  documentation-page.
* `docs/<servicename>.md`: this file is created automatically by the
  `sbwoaservices-tools` and contains the reference for the service based on
  the docstrings inside the source-code.
* `docs/usage.md`: here you will have to explain how the service can be
  started, updated, etc.
* `mkdocs.yml`: this file defines which docs-parts are required to create the
  documentation-page.
* `README.md`: this file contains the readme for the service. The content of
  this file is also used to create the help-text for the argparse.
