import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do .env

print(os.getenv("GOOGLE_CLIENT_ID"))
