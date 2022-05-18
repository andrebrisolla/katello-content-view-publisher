#!/usr/bin/python3
import yaml
import os
import configparser
import sys
import argparse
import subprocess as sb
import json

class Katello:

    def load_yaml(self):
        ''' load yaml data '''
        try:
            file_data = open(f'{self.fullpath}/products.yml', 'r').read()
            yml = yaml.safe_load(file_data)
            return yml
        except Exception as err:
            raise str(err)
    
    def __init__(self, **kwargs):
        self.fullpath = os.path.abspath(os.path.dirname(__file__))
        self.products = self.load_yaml()
        self.env = kwargs['env']

    def get_product_repos(self, **kwargs):
        try:
            product = kwargs['product']
            cmd_get_repos = ['hammer', 
                    '--output', 'json', 
                    'repository', 'list', 
                    '--organization-id', '1', 
                    '--product', f'{product}']
            res = sb.run(cmd_get_repos, stdout=sb.PIPE, stderr=sb.PIPE)
            if res.returncode == 0:
                json_data = res.stdout.decode('utf-8')
                data = json.loads(json_data)
                id_repos = [ x['Id'] for x in data ]
                return id_repos
            else:
                raise str(res.stderr)
        except Exception as err:
            raise str(err)

    def analyse_sync_date(self, **kwargs):
        try:
            moment = kwargs['moment']
            parsed = moment.replace('about','')
            return parsed
        except Exception as err:
            raise str(err)

    def parse_repos(self, **kwargs):
        try:
            ids = kwargs['repositories']
            info_repos = []
            for id in ids:
                cmd_get_repos_info = ['hammer', '--output', 'json', 'repository', 'info', '--id', f'{id}']
                res = sb.run(cmd_get_repos_info, stdout=sb.PIPE, stderr=sb.PIPE)
                if res.returncode == 0:
                    ret = res.stdout.decode('utf-8')
                    data = json.loads(ret)
                    info_repos.append({
                        'id' : data['ID'],
                        'name' : data['Name'],
                        'sync_status' : self.analyse_sync_date(moment=data['Sync']['Status']),
                        'last_sync' : data['Sync']['Last Sync Date']
                    })
            return info_repos
        except Exception as err:
            raise str(err)
    
    def get_content_view_info(self):
        try:
            cmd = ['hammer', 
                    '--output', 'json', 
                    'content-view', 'list', 
                    '--organization-id', '1']
            res = sb.run(cmd, stdout=sb.PIPE, stderr=sb.PIPE)
            if res.returncode == 0:
                ret = res.stdout.decode('utf-8')
                data = json.loads(ret)
                return data
        except Exception as err:
            raise str(err)


    def verify(self):
        try:
            yml = self.load_yaml()
            data = yml[self.env]
            content_views = data['content_views']
            content_view_info = self.get_content_view_info()
            filter_cvs = [ x for x in content_view_info if x['Name'] in content_views ]
            print(json.dumps(filter_cvs))
            
                #repos = self.get_product_repos(product=product_name)
                #repos_info = self.parse_repos(repositories=repos)
                #repo_parsed_data.append(repos_info)
                
                
        except Exception as err:
            raise str(err)
    



    def create(self):
        print('cria')
        




if __name__ == '__main__':
    parse = argparse.ArgumentParser(description="Create a Katello Content View")
    parse.add_argument('--verify', help='Verify if necessary a new version of a Content View.', action='store_true' )
    parse.add_argument('--create', help='Create a new version of a Content View if necessary.', action='store_true')
    parse.add_argument('--env', help='Katello environment [nprod|prod].', required=True, choices=['nprod','prod'])
    arguments = parse.parse_args()
    args = vars(arguments)
    kt = Katello(env=args['env'])
    if (args['verify'] and args['create']) or (not args['verify'] and not args['create']):
        print('\nError: You need to specify one parameter.\n')
        parse.print_help()
        sys.exit(1)
    elif args['verify']:
        kt.verify()
    elif args['create']:
        kt.create()