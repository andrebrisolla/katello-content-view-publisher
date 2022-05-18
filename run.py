#!/usr/bin/python3
import yaml
import os
import configparser

class Katello:

    def load_yaml(self):
        ''' load yaml data '''
        try:
            file_data = open(f'{self.fullpath}/products.yml', 'r').read()
            yml = yaml.safe_load(file_data)
            return yml
        except Exception as err:
            print(str(err))
    
    def load_conf(self):
        ''' load configs '''
        try:
            config = configparser.ConfigParser()
            config.read(f'{self.fullpath}/config.ini')
            environment = config['environment']
            return {
                'environment' : environment
            }
        except Exception as err:
            print(str(err))

    def __init__(self):
        self.fullpath = os.path.abspath(os.path.dirname(__file__))
        self.product = self.load_yaml()
        self.configs = self.load_conf()
        

kt = Katello()
print(kt.configs)