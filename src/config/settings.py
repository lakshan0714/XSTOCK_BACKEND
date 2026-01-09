import os
from dotenv import load_dotenv  

# Load environment variables from .env file
load_dotenv(override=True)  


class Settings:
    
    #Intialize admin credentials
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD =os.getenv("ADMIN_PASSWORD")


    #server config
    PROJECT_NAME = "CSE Stock Project"
    PORT= 8000
    HOST = "0.0.0.0"
    DEBUG = False

    
    # CORS Config
    BACKEND_CORS_ORIGINS = os.getenv("ALLOWED_ORIGINS")
   

    COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")
    
    ENV = os.getenv("ENV")
    
