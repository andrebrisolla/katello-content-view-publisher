#!/usr/bin/python3
import yaml
import os
import configparser
import sys
import argparse
import subprocess as sb
import json
from datetime import datetime, timedelta
import re

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

    def analyse_sync_date(self, **kwargs):
        try:
            moment = kwargs['moment']
            filter_1 = moment.replace('about','')
            filter_2 = filter_1.replace('2','')
            return 'ok'
        except Exception as err:
            raise str(err)

    def get_repo_sync_info(self, **kwargs):
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
                        'last_sync' : self.analyse_sync_date(moment=data['Sync']['Last Sync Date']),
                        'sync_status' : data['Sync']['Status']
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

    def analyse_date(self, **kwargs):
        try:
            data = kwargs['data']
            ''' START DEV'''
            #data = json.loads(open('teste.json','r').read())
            
            ''' END DEV '''
            for cv in data:
                cv_name = cv['Name']
                cv_id = cv['Content View ID']
                cv_last_published = cv['Last Published'].split()
                # convert date str to date object
                date_str = f'{cv_last_published[0]} {cv_last_published[1]}'
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                print(f'{cv_id} {cv_name} {date_obj}')
                for sync_info in cv['sync_info']:
                    print(sync_info)
            sys.exit()

        except Exception as err:
            raise str(err)


    def verify(self):
        try:
            ##self.analyse_date()
            yml = self.load_yaml()
            data = yml[self.env]
            content_views = data['content_views']
            content_view_info = self.get_content_view_info()
            cvs = [ x for x in content_view_info if x['Name'] in content_views ]
            cv_updated = []
            for cv in cvs:
                ids = cv['Repository IDs']
                repos_info = self.get_repo_sync_info(repositories=ids)
                cv['sync_info'] = repos_info
                cv_updated.append(cv)
            self.analyse_date(data=json.dumps(cv_updated))
        except Exception as err:
            raise str(  err)
    
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