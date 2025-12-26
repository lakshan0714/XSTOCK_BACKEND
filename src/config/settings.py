import os
from dotenv import load_dotenv  

# Load environment variables from .env file
load_dotenv(override=True)  


class Settings:
    
    #Intialize super admin credentials
    SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL")
    SUPER_ADMIN_PASSWORD =os.getenv("SUPER_ADMIN_PASSWORD")


    #server config
    PROJECT_NAME = "CSE Stock Project"
    PORT= 8000
    HOST = "0.0.0.0"
    DEBUG = False

    
    # CORS Config
    BACKEND_CORS_ORIGINS = os.getenv("ALLOWED_ORIGINS")
   

    COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")
    
    ENV = os.getenv("ENV")
    
