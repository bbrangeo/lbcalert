#!/bin/bash
gunicorn main --daemon
python worker.py