import os

import yaml
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPEN_AI_KEY')
