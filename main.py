import yaml
import openai

config = yaml.safe_load(open("config.yml"))
openai.api_key = config['KEYS']['openai']