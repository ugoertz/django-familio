# -*- coding: utf8 -*-

"""
fabfile for deploying the django-familio project.
"""

from __future__ import unicode_literals

import json

from fabric.api import run, local, env, settings, cd, task
from fabric.operations import _prefix_commands, _prefix_env_vars

secrets = json.load(file('../fabsecrets.json'))

env.hosts = secrets["ENV_HOSTS"]
env.code_dir = secrets["ENV_CODE_DIR"]
env.project_dir = secrets["ENV_PROJECT_DIR"]
env.static_root = secrets["ENV_STATIC_ROOT"]
env.virtualenv = secrets["ENV_VIRTUALENV"]
env.code_repo = secrets["ENV_CODE_REPO"]
env.django_settings_module = secrets["ENV_DJANGO_SETTINGS_MODULE"]

# Python version
PYTHON_BIN = "python"


def virtualenv(venv_dir):
    """
    Context manager that establishes a virtualenv to use.
    """
    return settings(venv=venv_dir)


def run_venv(command, **kwargs):
    """
    Runs a command in a virtualenv (which has been specified using
    the virtualenv context manager
    """
    run("source %s/bin/activate" % env.virtualenv + " && " + command, **kwargs)


def install_dependencies():
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            run_venv("pip install -U -r requirements/production.txt")


def pull_sources():
    """
    Pull source code from server
    """
    with cd(env.code_dir):
        run('git pull origin master')


@task
def run_tests():
    """ Runs the Django test suite as is.  """
    local("./manage.py test")


@task
def version():
    """ Show last commit to the deployed repo. """
    with cd(env.code_dir):
        run('git log -1')


@task
def uname():
    """ Prints information about the host. """
    run("uname -a")


@task
def webserver_restart():
    """
    Restarts the webserver that is running the Django instance
    """
    with cd(env.code_dir):
        run("touch %s/wsgi*.py" % env.project_dir)


@task
def build_doc():
    """
    Build Sphinx HTML documentation.
    """
    with virtualenv(env.virtualenv):
        with cd('%s/docs' % env.code_dir):
            run_venv("make html")
            run_venv("make latexpdf")
            run("cp _build/latex/project.pdf ../base/static/dokumentation.pdf")


def restart():
    """ Restart the wsgi process """
    with cd(env.code_dir):
        run("touch %s/{{ project_name }}/wsgi*.py" % env.code_dir)


def build_static():
    assert env.static_root.strip() != '' and env.static_root.strip() != '/'
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            run_venv("./manage.py collectstatic -v 0 --clear --noinput"
                     " --settings=%s" % env.django_settings_module)

    run("chmod -R ugo+r %s" % env.static_root)


@task
def first_deployment_mode():
    """
    Use before first deployment to switch on fake south migrations.
    """
    env.initial_deploy = True


@task
def update_database(app=None):
    """
    Update the database (run the migrations)
    Usage: fab update_database:app_name
    """
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            if getattr(env, 'initial_deploy', False):
                run_venv("./manage.py syncdb --all"
                         " --settings=%s" % env.django_settings_module)
                run_venv("./manage.py migrate --fake --noinput"
                         " --settings=%s" % env.django_settings_module)
            else:
                run_venv("./manage.py syncdb --noinput"
                         " --settings=%s" % env.django_settings_module)
                if app:
                    run_venv("./manage.py migrate %s --noinput" % app +
                             " --settings=%s" % env.django_settings_module)
                else:
                    run_venv("./manage.py migrate --noinput"
                             " --settings=%s" % env.django_settings_module)


@task
def sshagent_run(cmd):
    """
    Helper function.
    Runs a command with SSH agent forwarding enabled.

    Note:: Fabric (and paramiko) can't forward your SSH agent.
    This helper uses your system's ssh to do so.
    """
    # Handle context manager modifications
    wrapped_cmd = _prefix_commands(_prefix_env_vars(cmd), 'remote')
    try:
        host, port = env.host_string.split(':')
        return local(
            "ssh -p %s -A %s@%s '%s'" % (port, env.user, host, wrapped_cmd)
        )
    except ValueError:
        return local(
            "ssh -A %s@%s '%s'" % (env.user, env.host_string, wrapped_cmd)
        )


@task
def deploy():
    """
    Deploy the project.
    """
    pull_sources()
    install_dependencies()
    update_database()
    build_doc() # must be run before build_static to ensure
                # pdf documentation is updated
    build_static()
    webserver_restart()
