# SuperForm


## Synopsis

SuperForm is a data sharing manager that lets users insert information in a single input form to then share it on multiple channels (Facebook,Mail,Twitter,RSS,...).

This project is a web applciation written in Python and use the framework Flask.


## Motivation

As a huge information sharer, the INGI department of UCLouvain, and especially the secretariat, manage different channels. The insertion part is a long and painful task, the differents channels have multiple layouts that need a lot of human modification to fit with.

The main goal of this project is to simplify this task by providing a unique form that will manage layouts,necessary fields and sharing part.

A validation part is also an important feature of this project to let everyone insert data and then verify that it suits with the channel goal.

## Installation

SuperForm has the following dependencies:

* Python 3.5
* Flask 1.0.2
* SQLAlchemy 1.2.8
* Jinja 2.10
* Setuptools 39.1.0
* Onelogin 1.4.0

## How to run it?

Superform needs some instructions before to run the app:

```python

from superform import models
from superform import app
app.app_context().push()
models.db.create_all()

```

## Tests

Be in Superform/superform folder and then 'pytest -v' in your terminal.
All tests are under superform/tests.

## How to write a plugin/module

A plugin is a simple python file (called a module) that needs some function and variables to work in our Superform system.
This file should contain :

* a variable called FIELDS_UNAVAILABLE. This is a list of field names that are not used by your module. This names must match with post variables.
* a variable called CONFIG_FIELDS.This is also a python list. This lets the manager of your module enter data that are used to communicate with other services. Example : The mail where the information must be send.
* a function called run with as many arguments as you want (**kwargs).

## Contributors

Kim Mens - @kimmens 

Nicolas Detienne - @NDetienne

Anthony Gego - @anthonygego

Ludovic Taffin - @Drumor/@ltaffin
