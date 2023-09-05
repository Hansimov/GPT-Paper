# %load_ext autoreload
# %autoreload

# Use `%load startup.py` to load this script
# Use `%run -i "startup.py"` to run this script in IPython namespace
# Run this cell when initialized

import asyncio
import nest_asyncio
import datetime
import os
import sys
from pathlib import Path
import logging
import ipynbname
import platform

repo_path = Path(os.path.abspath(".")).parent
if str(repo_path) not in sys.path:
    sys.path.append(str(repo_path))
work_dir = Path().absolute()
if platform.system() == "Windows":
    ipynb_path = ipynbname.path()
    # ipynb_name = ipynbname.name()

import jupyter_black
import ipywidgets as widgets
from importlib import reload
from IPython.display import display
from IPython.display import Javascript
from ipywidgets import Image as wImage
from ipywidgets import HBox, Layout
from utils.logger import logger
from termcolor import colored
from cells import get_above_cell_content, get_notebook_cells
from interactions import chat
from agents.openai import OpenAIAgent
from agents.retriever import DocumentsRetriever
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

nest_asyncio.apply()
jupyter_black.load(lab=True)

print(f"Repo path:   [{repo_path}]")
print(f"Working dir: [{work_dir}]")
# print(f"Notebook Path: [{ipynb_path}]")
# logger.note(f"Notebook Name: [{ipynb_name}]")
print(f"Now: [{datetime.datetime.now()}]")
