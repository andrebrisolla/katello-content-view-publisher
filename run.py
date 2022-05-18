#!/usr/bin/python3
import yaml
import os

class Katello:

    def load_yaml_data(self):
        try:
            file = open(f'{self.fullpath}/products.yml', 'r').read()
            print(file)
        except Exception as err:
            print(str(err))

    def __init__(self):
        self.fullpath = os.path.abspath(os.path.dirname(__file__))
        ''' load yaml data '''

kt = Katello()
kt.load_yaml_data()