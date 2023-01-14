import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
database = os.getenv('REUNITE_TAG_DB_NAME')
password = os.getenv('REUNITE_TAG_DB_PASSWORD')
user = os.getenv('REUNITE_TAG_DB_USER')

DB_URI = "mongodb+srv://{}:{}@dscntshop-cluster.t3hfzto.mongodb.net/{}".format(user, password, database)
