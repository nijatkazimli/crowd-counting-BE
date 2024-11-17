from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    AZURE_STORAGE_CONNECTION_STRING = 'AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://azuriteDocker:10000/devstoreaccount1;QueueEndpoint=http://azuriteDocker:10001/devstoreaccount1;TableEndpoint=http://azuriteDocker:10002/devstoreaccount1'
    AZURE_STORAGE_CONTAINER = 'crowd-counting'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
