#!/usr/bin/python3
import yaml
import os

class Katello:

    def load_yaml_data(self):
        ''' load yaml data '''
        try:
            file_data = open(f'{self.fullpath}/products.yml', 'r').read()
            yml = yaml.safe_load(file_data)
            return yml
        except Exception as err:
            print(str(err))

    def __init__(self):
        self.fullpath = os.path.abspath(os.path.dirname(__file__))
        self.product = self.load_yaml_data()
        

kt = Katello()
print(kt.product)