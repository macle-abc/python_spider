import requests
from bs4 import BeautifulSoup

from spider.settings import get_setting
from tools.headers import get_headers

from queue import Queue
from threading import Event
from time import time
import queue
import re
import json
