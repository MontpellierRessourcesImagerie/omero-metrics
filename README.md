
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/pro-dho/omero-metrics/omero_plugin.yml)
![GitHub License](https://img.shields.io/github/license/pro-dho/omero-metrics)

<img alt="omero-metrics logo" height="100" src="omero_metrics/static/omero_metrics/images/metrics_logo.png"/>

This project is financed by [France BioImaging](https://france-bioimaging.org/).

<img alt="FBI logo" height="100" src="docs/slides/media/logo_FBI.png"/>


An OMERO webapp to follow microscope performance over time.

The following instructions are for Linux. Instructions for other OSs will be added soon.

# Installation on your OMERO-web server instance

To be completed

# Try omero-metrics using docker

Install docker and docker-compose on your computer following the instructions on the [docker website](https://docs.docker.com/get-docker/).

Clone the repository:
```bash
git clone https://github.com/pro-dho/omero-metrics.git
cd omero-metrics
```

Run the following command to start the server:

```bash
docker compose up -d
```

Wait for the server to start and then go to <http://localhost:5080/> in your server.

Before trying anything, you need to generate users, and import some data, etc. If you wish, you can do that 
automatically. To do so you need to install the python environment and run a script that will generate some data for you.

```bash
# cd to the omero-metrics directory
cd omero-metrics
# create a virtual environment and install omero-metrics
python -m venv .venv
# activate the virtual environment
source .venv/bin/activate
pip install -e .
cd test/omero-server
python structure_generator.py
```

Go to <http://localhost:5080/> and log in with the following credentials:
- Username: Asterix
- Password: abc123

Once you are logged in:
- Change your default group to any of the microscope groups
- Select any project, dataset or image
- In the middle pannel select the metrics view in the top right menu.

# Installation for development

Here we explain how to install omero-metrics using an OMERO-web server running locally. The main advantage is
that you may edit the code and debug very easily.

## Pre-requirements

You need to make sure that Python (version 3.9, 3.10 or 3.11) is installed in your computer.
You need to have an OMERO instance running. You may use the docker-compose file provided. All the configurations in 
these instructions are meant to connect locally to this docker instance.

## Configuration of a virtual environment

Clone the repository and create a virtual environment to run your server in. We use poetry to manage the virtual environment.
While not mandatory, we recommend using poetry to manage your virtual environment.

install poetry according to the [official documentation](https://python-poetry.org/docs/#installation).
We recommend configuring poetry to create virtual environments in the project directory:
```bash
poetry config virtualenvs.in-project true
```

Then, install the package in development mode:
```bash
git clone https://github.com/pro-dho/omero-metrics.git
cd omero-metrics
poetry install
```

## Configuration of OMERO-web and omero-metrics

To configure OMERO-web and omero-metrics we created a bash script. Look into it to see how it works.
Be sure to cd into the project directory and activate the virtual environment before running the script.

```bash
./configuration_omero.sh
```

This script will create a configuration directory "omerodir" in the project directory. 
All configuration files will be stored there.

The script is recognizing your activated python environment and using for the deployment.
Alternatively, you can manually specify the path:

```bash
./configuration_omero.sh /path/to/omero-metrics/enviroment
```

## Start OMERO-web

Once configured, start the OMERO-web server:

```bash
export REACT_VERSION=18.2.0
omero web start
```

The server will be available at <http://localhost:8000>

**Note:** The `REACT_VERSION=18.2.0` environment variable is required for dash-mantine-components to work properly. 
Without it, the app will use React 16 which is incompatible.

## Debugging

In order to debug the server, you need to start the server in the foreground:
```bash
export REACT_VERSION=18.2.0
omero web start --foreground
```

## Debugging with PyCharm

We use Pycharm so here is how we setup the project for development and debugging. You do not require the payed version.
A run configuration can be created as follows:

- Open the project in PyCharm as you would normally do.
- Create or select the interpreter/virtual environment.
- Create a new run configuration:
    - Give it a name as you wish.
    - Select the interpreter
    - Configure the script. This corresponds with the manage.py script in the omeroweb package in your venv. eg: "./.venv/lib/python3.10/site-packages/omeroweb/manage.py"
    - Enter the script parameters: `runserver localhost:8000 --noreload`
    - Configure the environment variables:
        - DJANGO_SETTINGS_MODULE=omeroweb.settings
        - OMERODIR=/the/path/to/the/omerodir/created/by/the/configuration/script/ eg: home/your_name/PycharmProjects/omero-metrics/omerodir
        - REACT_VERSION=18.2.0  <!-- TODO: This will have to be removed in future versions -->
        - PYTHONUNBUFFERED=1
- Apply and click OK.
- Run or debug the configuration as usual.

The debug server runs with Django's development server on `localhost:8000` with auto-reload disabled for stable debugging.

# Some Useful Links To install ZeroC-Ice

The proper installation of ZeroC-Ice should be managed in the pyproject.toml file. However, if you have troubles
with the installation, you can download the proper precompiled version of ZeroC-Ice from the following links.

```python
#zeroc-ice @ https://github.com/glencoesoftware/zeroc-ice-py-macos-universal2/releases/download/20240131/zeroc_ice-3.6.5-cp311-cp311-macosx_11_0_universal2.whl
#zeroc-ice @ https://github.com/glencoesoftware/zeroc-ice-py-linux-x86_64/releases/download/20240202/zeroc_ice-3.6.5-cp311-cp311-manylinux_2_28_x86_64.whl
```

## Further Info

1.  This app was derived from [cookiecutter-omero-webapp](https://github.com/ome/cookiecutter-omero-webapp).
2.  For further info on deployment, see [Deployment](https://docs.openmicroscopy.org/latest/omero/developers/Web/Deployment.html)


## License

This project, similar to many Open Microscopy Environment (OME) projects, is
licensed under the terms of the AGPL v3.


## Copyright

2024 CNRS

