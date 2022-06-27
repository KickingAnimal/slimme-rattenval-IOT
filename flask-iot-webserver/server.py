import os
from threading import Thread


def httpApp(): 
    os.system('python httpApp.py')

def httpsApp():
    os.system('python app.py')

Thread(target = httpApp).start() 
Thread(target = httpsApp).start()
