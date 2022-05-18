#!/usr/bin/python3
import yaml
import os
import configparser
import sys
import argparse

class Katello:

    def load_yaml(self):
        ''' load yaml data '''
        try:
            file_data = open(f'{self.fullpath}/products.yml', 'r').read()
            yml = yaml.safe_load(file_data)
            return yml
        except Exception as err:
            raise str(err)
    
    def load_conf(self):
        ''' load configs '''
        try:
            config = configparser.ConfigParser()
            config.read(f'{self.fullpath}/config.ini')
            c = config['config']
            environment = c['environment']
            return {
                'environment' : environment
            }
        except Exception as err:
            raise str(err)

    def __init__(self):
        self.fullpath = os.path.abspath(os.path.dirname(__file__))
        self.product = self.load_yaml()
        self.configs = self.load_conf()

    def verify(self):
        print('verifica')
    
    def create(self):
        print('cria')
        
if __name__ == '__main__':
    parse = argparse.ArgumentParser(description="Create a Katello Content View")
    parse.add_argument('--verify', help='Verify if necessary a new version of a Content View.', action='store_true' )
    parse.add_argument('--create', help='Create a new version of a Content View if necessary.', action='store_true')
    arguments = parse.parse_args()
    args = vars(arguments)
    if (args['verify'] and args['create']) or (not args['verify'] and not args['create']):
        print('\nError: You need to specify one parameter.\n')
        parse.print_help()
        sys.exit(1)
    elif args['verify']:
        kt = Katello()
        kt.verify()
    elif args['create']:
        kt = Katello()
        kt.create()