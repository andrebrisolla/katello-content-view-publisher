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
'''
    Author: Andre Brisolla
    Date: May 18, 2022
    Goal: This script will check if is necessary 
    to publish a new Version of a Content View on Katello!
    Version: 1.0
'''
class Katello:
    
    def __init__(self, **kwargs):
        '''
            Set some class attributes
        '''
        self.fullpath = os.path.abspath(os.path.dirname(__file__))
        self.products = self.load_yaml()
        self.env = kwargs['env']
        self.publish_new_version=kwargs['publish_new_version']

    def load_yaml(self):
        '''
            Load yaml data
        '''
        try:
            file_data = open(f'{self.fullpath}/products.yml', 'r').read()
            yml = yaml.safe_load(file_data)
            return yml
        except Exception as err:
            raise str(err)
    
    def analyse_sync_date(self, **kwargs):
        '''
            Unfortunatly the 'hammer' command does not returns a timestamp of a sync,
            it returns a string like: '"about 5 days",  "about 2 hours". So, 
            we need to take this informations and turn it into a datetime object to compare with
            ContentView datetimes and "Now" datetime.
        '''
        try:
            moment = kwargs['moment']
            filter_1 = moment.replace('about','')
            filter_2 = re.sub('^\s+','', filter_1)
            time_key=''
            if re.search('day', filter_2):
                time_key='days'
                time_val = int(filter_2.split()[0])*24
            elif re.search('hour', filter_2):
                time_key='hours'
                time_val = int(filter_2.split()[0])
            if re.search('month', filter_2):
                time_key='days'
                time_val = (30*int(filter_2.split()[0])*24)
            td = timedelta(hours=time_val)
            now = datetime.now()
            dt = now - td
            return dt
        except Exception as err:
            raise str(err)

    def get_repo_sync_info(self, **kwargs):
        '''
            This method receives a list of repositories ID`s.
            It uses the command "hammer" to take 
            informations about sync and then return the information.
        '''
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
        '''
            Get a list of Content View that is Published in Katello
            It uses a organization-id 1 that is refenced to the Default Organization
        '''
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

    def publish_a_new_content_view(self, **kwargs):
        '''
            It receives a Content View ID and publish a new Version of it.
        '''
        try:
            id = kwargs['id']
            cmd = ['hammer', 'content-view', 'publish', '--id', f'{id}', '--async']
            res = sb.run(cmd, stdout=sb.PIPE, stderr=sb.PIPE)
            if res.returncode == 0:
                ret = res.stdout.decode('utf-8')
            else:
                ret = res.stderr.decode('utf-8')
            print(f'   {ret}')
        except Exception as err:
            raise str(err)

    def analyse_date(self, **kwargs):
        '''
            This method will iterate at a Content View data that was updated with
            repository infos ( like repo last sync ) and will show if is necessary to
            publish a new version of a Content View, if the parameter "--publish" was defined it will call the method
            "publish_a_new_content_view" that will publish a new version.
        '''
        try:
            data = kwargs['data']
            for cv in data:
                cv_name = cv['Name']
                cv_id = cv['Content View ID']
                cv_last_published = cv['Last Published'].split()
                date_str = f'{cv_last_published[0]} {cv_last_published[1]}'
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                compare_cv_repos = [ date_obj > x['last_sync'] for x in cv['sync_info'] ]
                cv_needs_to_be_published = False in compare_cv_repos
                if cv_needs_to_be_published:
                    print(f' - Content View "{cv_name}" needs to be published! ')
                    if self.publish_new_version:
                        self.publish_a_new_content_view(id=cv_id)
                else:
                    print(f' - Content View "{cv_name}" doesn\'t needs to be published! ')
        except Exception as err:
            raise str(err)

    def verify(self):
        try:
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
            self.analyse_date(data=cv_updated)
        except Exception as err:
            raise str(  err)
    
if __name__ == '__main__':
    parse = argparse.ArgumentParser(description="Create a Katello Content View")
    parse.add_argument('--verify', help='Verify if necessary a new version of a Content View.', action='store_true', required=True )
    parse.add_argument('--publish', help='Create a new version of a Content View if necessary.', action='store_true')
    parse.add_argument('--env', help='Katello environment [nprod|prod].', required=True, choices=['nprod','prod'])
    arguments = parse.parse_args()
    args = vars(arguments)
    kt = Katello(env=args['env'],publish_new_version=args['publish'])
    if args['verify']:
        kt.verify()
