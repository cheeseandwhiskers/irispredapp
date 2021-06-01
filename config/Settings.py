import os

class Settings:
    secret="sajdjsah#@!$#cxbcxbn(*12ssap[s"
    
    # Heroku database settings
    host=os.environ['HOST']
    database=os.environ['DATABASE']
    user=os.environ['USERNAME']
    password=os.environ['PASSWORD']

    # #local dev database settings
    # host='localhost'
    # database='iris_db'
    # user='root'
    # password='rootpass'