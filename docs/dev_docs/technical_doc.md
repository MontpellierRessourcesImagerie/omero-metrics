---
title: omero-metrics Technical doc

---


omero-metrics is an omero web app. It was initially generated using the cookiecutter https://github.com/ome/cookiecutter-omero-webapp

For visualization, we are using the help of dash and django-plotly-dash. 
We are using also microscope-metrics and microscopemetrics-schema developed previously by Julio. 


# Documentations
- https://django-plotly-dash.readthedocs.io/en/latest/
- https://dash.plotly.com/
- https://www.dash-mantine-components.com/
- https://github.com/GibbsConsulting/django-plotly-dash/tree/master/demo
- https://github.com/ome/omero-test-infra

# New Analysis Type

![image](media/project_structure.png)
 
To add a new analysis type, you create a folder under omero_metrics/dash_apps/dash_analysis
 
create two python files, one for the dataset view and the other for the image view. These files will corresponds to your 
django plotly dash pages.

You need to update tools/data_manager to add the new analysis type and to manage your data.

Make sure to add the django plotly dash pages to the urls.py file to trigger their registrations.





 

# Running Debug Mode on Pycharm
To run the debug mode and run omero locally using a django test server. 

```bash
$ git clone https://github.com/pro-dho/omero-metrics.git
$ cd omero-metrics
$ python -m venv my_venv
$ source my_venv/bin/activate
$ pip install -e .
```
![image](media/project_structure1.png)


We created a bash script to configure omero. You can run it by typing:

```bash
$ ./configuration_omero.sh /path/to/omeroweb /path/to/mydatabase
````
where `/path/to/omeroweb` is the path to the omero-web installation or path and `/path/to/mydatabase` is the path to the omero-metrics sqlite database.


```bash
export REACT_VERSION=18.2.0
export OMERODIR=$(pwd)
omero config set omero.web.server_list '[["localhost", 6064, "omero_server"]]'
omero web start
````

Make sure under etc directory you have ice.config. If it doesn't exist, you create it by adding the following:

```
omero.host=localhost
omero.port=6064
omero.rootpass=omero
```

Note: for the pytest to work the omero.web.server_list should start exactly with the server configured under ice.config. Otherwise, the test won't pass. 


For more information about ice.config. Click [Here](https://github.com/ome/openmicroscopy/blob/develop/etc/ice.config).

## Running Pytest on Pycharm for omero-metrics

Try to look for this small menu in the image to run and configure your pytest and Django server:

![image](media/debug_run_menu.png)

Click on "Edit Configurations" the following window will open to configure your pytest and debug mode:

![image](media/debug_run_window.png)

Click on add new run configuration and click on pytest:

![image](media/add_new_config.png)

Now, we need to add our configurations: 
The path to the pytest script you want to run
Working directory should be the root project omero-metrics. and add for Env variables : DJANGO_SETTINGS_MODULE=omeroweb.settings;REACT_VERSION=18.2.0;OMERODIR=~/omero-metrics;ICE_CONFIG=~/omero-metrics/etc/ice.config

![image](media/set_env_pytest.png)

That's it, now run your test.


## Debug Mode:

We will do the same as pytest but instead of adding pytest we will add Django Server:

![image](media/django_server_window.png)

When you click on the Django server, this is the view that you will see. You will need first to enable Django Support for the project and add some configurations.

![image](media/add_config_django_server.png)

The Django root project should be ~/omeroweb
manage script is manage.py and settings is settings.py

![image](media/setting_up_django_project.png)


The final step is to configure your configuration file to run a django server locally:
add these Env variables and run your omero web client instance locally DJANGO_SETTINGS_MODULE=omeroweb.settings;REACT_VERSION=18.2.0;OMERODIR=~/omero-metrics;ICE_CONFIG=~/omero-metrics/etc/ice.config

![image](media/set_env_django_server.png)
