#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from processors.processor_interface import Processor
from services.processor_service import ProcessorService
from selenium import webdriver


__author__ = 'Iván de Paz Centeno'


def save_screenshot(binary_data, filename):
    if not filename.endswith(".png"):
        filename += ".png"

    with open(filename, "wb") as file:
        file.write(binary_data)


class PhantomJSProcessor(Processor):

    def __init__(self):
        """
        Constructor of the class.
        Initializes the webdriver for this processor.
        """
        Processor.__init__(self)
        self.driver = webdriver.PhantomJS("phantomjs/phantomjs")  # the normal SE phantomjs binding
        self.driver.set_window_size(1024, 768)

    def process(self, url):
        """
        Retrieves a request (any url) and returns a screenshot in binary format.
        :param url: URL to process.
        :return: binary data in PNG format of the screenshot.
        """

        self.driver.get(url)  # whatever reachable url
        binary_data = self.driver.get_screenshot_as_png()
        return binary_data

    def __del__(self):
        self.driver.quit()

# 1. Arrancamos el servicio con 2 procesos
processor_service = ProcessorService(PhantomJSProcessor, parallel_workers=2)
processor_service.start()

pages = ["https://www.google.com",
         "https://www.stackoverflow.com",
         "https://es.quora.com",
         "https://www.docker.com"]

promises = []

# 2. Encolamos las páginas
for page in pages:
    print("Queued {}".format(page))
    promises.append(processor_service.queue_request(page))


# 3. Guardamos sus screenshots
for page, promise in zip(pages, promises):
    print("Retrieved {}".format(page))
    save_screenshot(promise.get_result(), page.split("https://")[1])


processor_service.stop()




