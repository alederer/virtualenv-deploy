virtualenv-deploy
=================

What it does
---------------------

virtualenv and pip are cool!  But how do you deploy a standalone Python application (with dependencies) conveniently to your team?  Say, a tool required by non-technical team members who shouldn't have to mess with virtualenv or pip or whatever.

virtualenv-deploy is a simple script that handles setting up a virtualenv for your application on remote machines transparently (without installing anything on the system).  After the one-time virtualenv setup, on each subsequent run virtualenv-deploy simply passes control to your app, unless requirements.txt has changed, at which point it will update.

How to use
---------------------

What you'll check in to your repository for deployment is a folder containing the following:

* main.py (the entry-point and currently only file of virtualenv-deploy)
* requirements.txt (your pip requirements, a la "pip freeze > requirements.txt")
* src/main.py (entry-point to your real app)

That's it.  No need to commit/check-in any virtualenv folders.  When your non-technical friend clones the repository to his/her machine and runs the top-level main.py with whatever arguments, your application will run (after a slight one-time delay during which it's setting up a virtualenv in the directory and installing dependencies).

Limitations
---------------------

* Currently no Windows support - tar/gzip utilities aren't included as standard on Windows and untarring the virtualenv source wouldn't work.  Could possibly work around by requiring virtualenv to be installed globally for Windows machines, but that slightly defeats the purpose.

* Requires Python install - needs nothing fancy like virtualenv or pip, but it is a Python script.

* If you expect the machines you're deploying to to be homogenous (e.g. a fleet of identical Linux machines), it may be acceptable to just check in your virtualenv folder wholesale, eliminating the need for virtualenv-deploy.  This isn't recommended by the virtualenv docs, but I've done it and it works for the homogenous use-case, if you're down for cluttering your repository with thousands of irrelevant files.
