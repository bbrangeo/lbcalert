#!/bin/bash
gunicorn main:app --daemon
python worker.py