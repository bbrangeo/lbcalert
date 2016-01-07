#!/bin/bash
python worker.py
gunicorn main:app --daemon