#!/bin/bash

python manage.py migrate

python manage.py fetch

python manage.py apply_rules