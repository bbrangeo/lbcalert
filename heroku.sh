#!/bin/bash
gunicorn manage:runserver --daemon
python worker.py