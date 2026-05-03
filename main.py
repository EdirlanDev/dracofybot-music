from platform import python_version
from utils.client import BotPool

print(f"Python - Versão do python: {python_version()}")

pool = BotPool()
pool.setup()
