import mylogging
from time import sleep
import numpy as np
import requests


class Requsts (object):
    def __init__(self):
        
        self.logger = mylogging.ColouredLogger("request")
        self.logger.debug("Request object created")

    def send(self,method,url):
        self.logger.debug("Sending request")
        if method == "GET":
            self.logger.debug("Sending GET request")
            response = requests.get(url, headers=self.headers)
            self.logger.debug("Response received")
            return response
        elif method == "POST":
            self.logger.debug("Sending POST request")
            response = requests.post(url, headers=self.headers, data=self.body)
            self.logger.debug("Response received")
            return response
        elif method == "PUT":
            self.logger.debug("Sending PUT request")
            response = requests.put(url, headers=self.headers, data=self.body)
            self.logger.debug("Response received")
            return response
        elif method == "DELETE":
            self.logger.debug("Sending DELETE request")
            response = requests.delete(url, headers=self.headers)
            self.logger.debug("Response received")
            return response
        else:
            self.logger.error("Invalid method")
            return None