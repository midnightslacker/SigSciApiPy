#!/usr/bin/env python
# Signal Sciences Python API Client
# Science all the Signals!

#### Configuration Section ################
EMAIL    = '' # The email address associated with your
              # Signal Sciences account, e.g. user@yourdomain.com

PASSWORD = '' # The password associated with your Signal Sciences account.

# Your CORP and SITE can be found by logging
# into the Signal Sciences Dashboard. The URL 
# for the overview page contains these values.
# Example:
# https://dashboard.signalsciences.net/<CORP>/<SITE>
#
CORP = ''
SITE = ''

# API Query settings
# For help with time search syntax see:
# https://dashboard.signalsciences.net/documentation/knowledge-base/search-syntax#time
FROM   = None # example: FROM = '-6h'
UNTIL  = None # example: UNTIL = '-4h'
TAGS   = None # example: TAGS = 'SQLI XSS TRAVERSAL'
CTAGS  = None # example: CTAGS = 'bad-bot failed-login'
SERVER = None # example: SERVER = 'example.com'
LIMIT  = None # example: LIMIT = 250
FIELD  = None # example: FIELD = 'all'
FILE   = None # example: FILE = '/tmp/sigsci.json'
FORMAT = None # example: FORMAT = 'csv'
SORT   = None # example: SORT = 'asc'
###########################################

# default for retriveing agent metrics
AGENTS = False
# default for feed requests
FEED   = False
# default for whitelist parameters
WHITELIST_PARAMETERS        = False
WHITELIST_PARAMETERS_ADD    = False
WHITELIST_PARAMETERS_DELETE = False
# default for whitelist paths
WHITELIST_PATHS        = False
WHITELIST_PATHS_ADD    = False
WHITELIST_PATHS_DELETE = False
# default for whitelist
WHITELIST        = False
WHITELIST_ADD    = False
WHITELIST_DELETE = False
# default for blacklist
BLACKLIST        = False
BLACKLIST_ADD    = False
BLACKLIST_DELETE = False
# default for redactions
REDACTIONS        = False
REDACTIONS_ADD    = False
REDACTIONS_DELETE = False
###########################################

import sys
import os
import argparse
import requests
import json
import csv
import datetime

sys.dont_write_bytecode = True

class SigSciAPI:
    """
    SigSciAPI()
    Methods:
        authenticate()
        build_query(from_time=<string>, until_time=<string>, tags=<list>)
        query_api()
    
    Example:
        sigsci       = SigSciAPI()
        sigsci.email = 'foo@bar.com'
        sigsci.pword = 'c0mpl3x'
        sigsci.corp  = 'foo_bar'
        sigsci.site  = 'www.bar.com'
        sigsci.limit = 1000
        sigsci.file  = '/tmp/foo.json'
        
        if sigsci.authenticate():
            sigsci.build_query(from_time='-6h', until_time='-5h', tags=['SQLI', 'XSS', 'CMDEXE'])
            sigsci.query_api()
    """
    base       = 'https://dashboard.signalsciences.net'
    url        = base + '/api/'
    version    = 'v0'
    base_url   = None
    authn      = None
    email      = None
    pword      = None
    corp       = None
    site       = None
    query      = 'from:-6h '
    from_time  = '-1h'
    until_time = None
    tags       = None
    ctags      = None
    server     = None
    limit      = 100
    field      = 'data'
    file       = None
    format     = 'json'
    sort       = 'desc'
    ua         = 'Signal Sciences Client API (Python)'
    
    # api end points
    LOGIN_EP      = '/auth/login'
    LOGOUT_EP     = '/auth/logout'
    CORPS_EP      = '/corps/'
    SITES_EP      = '/sites/'
    REQEUSTS_EP   = '/requests'
    AGENTS_EP     = '/agents'
    FEED_EP       = '/feed/requests'
    WLPARAMS_EP   = '/paramwhitelist'
    WLPATHS_EP    = '/pathwhitelist'
    WHITELIST_EP  = '/whitelist'
    BLACKLIST_EP  = '/blacklist'
    REDACTIONS_EP = '/redactions'

    def authenticate(self):
        """
        SigSciAPI.authenticate()
        
        Before calling, set:
            SigSciAPI.email
            SigSciAPI.pword
        
        Stores session cookie in:
            SigSciAPI.authn.cookies
        """
        
        self.authn = requests.post(self.base_url + self.LOGIN_EP,
            data = { 'email': self.email, 'password': self.pword }, 
            allow_redirects = False)
        
        if self.authn.headers['Location'] == '/':
            return True
        elif self.authn.headers['Location'] == '/login?p=invalid':
            print 'Login failed!'
            return False
        else:
            print 'Unexpected error %s' % self.authn.headers['Location']
            return False

    def build_query(self):
        """
        SigSciAPI.build_query()
        
        For from_time and until_time syntax see:
        https://dashboard.signalsciences.net/documentation/knowledge-base/search-syntax#time
        
        Default values (query):
            SigSciAPI.from_time  = -1h
            SigSciAPI.until_time = None
            SigSciAPI.tags       = <all tags>
        """
        
        if None != self.from_time:
            self.query = 'from:%s ' % str(self.from_time)
        
        if None != self.until_time:
            self.query += 'until:%s ' % str(self.until_time)
        
        if None != self.server:
            self.query += 'server:%s ' % str(self.server)
        
        if None != self.sort:
            self.query += 'sort:time-%s ' % str(self.sort)
        
        if None != self.tags:
            self.query += 'tag:'
            self.query += ' tag:'.join(self.tags)
            self.query += ' ' # extra space required for appending ctags
        
        if None != self.ctags:
            self.query += 'tag:'
            self.query += ' tag:'.join(self.ctags)

    def query_api(self):
        """
        SigSciAPI.query_api()
        
        Before calling, set:
            (Required):
                SigSciAPI.corp
                SigSciAPI.site
            
            (Optional):
                SigSciAPI.query
                SigSciAPI.limit
                SigSciAPI.file
        
        """
        
        try:
            headers = { 'Content-type': 'application/json', 'User-Agent': self.ua }
            url     = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.REQEUSTS_EP + '?q=' + str(self.query).strip() + '&limit=' + str(self.limit)
            r       = requests.get(url, cookies=self.authn.cookies, headers=headers)
            j       = json.loads(r.text)
            f       = None if 'all' == self.field else self.field

            if 'message' in j:
                raise ValueError(j['message'])
            
            if 'json' == self.format:
                if not self.file:
                    if None == f:
                        print('%s' % json.dumps(j))
                    else:
                        print('%s' % json.dumps(j[f]))
                else:
                    with open(self.file, 'a') as outfile:
                        if None == f:
                            outfile.write('%s' % json.dumps(j))
                        else:
                            outfile.write('%s' % json.dumps(j[f]))
            
            elif 'csv' == self.format:
                if not self.file:
                    csvwritter = csv.writer(sys.stdout)
                else:
                    csvwritter = csv.writer(open(self.file, "wb+"))

                # for now only output data "j['data']"
                f = None
                if None == f:
                    for row in j['data']:
                        tag_list = ''
                        detector = row['tags']

                        for t in detector:
                            tag_list = tag_list + t['type'] + '|'
                        
                        csvwritter.writerow([str(row['timestamp']), str(row['id']), str(row['remoteIP']), str(row['remoteCountryCode']), unicode(row['path']).encode('utf8'), str(tag_list[:-1]), str(row['responseCode']), str(row['agentResponseCode'])])
                else:
                    print('%s' % json.dumps(j[f]))

            else:
                print('Error: Invalid output format!')
            
        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)

    def get_feed_requests(self):
        """
        SigSciAPI.get_feed_requests()
        
        Before calling, set:
            (Required):
                SigSciAPI.corp
                SigSciAPI.site
            
            (Optional):
                SigSciAPI.from_time
                SigSciAPI.until_time
                SigSciAPI.tags
                SigSciAPI.file
                SigSciAPI.format
        
        """
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__feed_requests_get
        # /corps/{corpName}/sites/{siteName}/feed/requests
        try:
            now = datetime.datetime.now()

            if None == self.from_time:
                tm             = now - datetime.timedelta(hours=1, minutes=5)
                stm            = tm.strftime("%Y-%m-%d %H:%M:00")
                self.from_time = int(tm.strptime(stm, "%Y-%m-%d %H:%M:00").strftime("%s"))
                self.query     = 'from=%s' % str(self.from_time)
            else:
                self.query     = 'from=%s' % str(self.from_time)

            if None == self.until_time:
                tm              = now - datetime.timedelta(minutes=5)
                stm             = tm.strftime("%Y-%m-%d %H:%M:00")
                self.until_time = int(tm.strptime(stm, "%Y-%m-%d %H:%M:00").strftime("%s"))
                self.query      = '&until+=%s' % str(self.until_time)
            else:
                self.query = '&until+=%s' % str(self.until_time)
            
            if None != self.tags:
                self.query += '&tags='
                self.query += ','.join(self.tags)
        
            if None != self.ctags:
                if None == self.tags:
                    self.query += '&tags='
                
                self.query += ','.join(self.ctags)
            
            headers = { 'Content-type': 'application/json', 'User-Agent': self.ua }
            url     = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.FEED_EP + '?' + str(self.query).strip()
            r       = requests.get(url, cookies=self.authn.cookies, headers=headers)
            j       = json.loads(r.text)

            if 'message' in j:
                raise ValueError(j['message'])
            
            if 'json' == self.format:
                if not self.file:
                    print('%s' % json.dumps(j['data']))

                else:
                    with open(self.file, 'a') as outfile:
                        outfile.write('%s' % json.dumps(j['data']))
            
            # get all next
            next = j['next']
            while '' != next['uri'].strip():
                url = self.base +  next['uri']
                r   = requests.get(url, cookies=self.authn.cookies, headers=headers)
                j   = json.loads(r.text)

                if 'message' in j:
                    raise ValueError(j['message'])
            
                if 'json' == self.format:
                    if not self.file:
                        print('%s' % json.dumps(j['data']))

                    else:
                        with open(self.file, 'a') as outfile:
                            outfile.write('%s' % json.dumps(j['data']))
                
                next = j['next']

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)

    def get_agent_metrics(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__agents_get
        # /corps/{corpName}/sites/{siteName}/agents
        try:
            headers = { 'Content-type': 'application/json', 'User-Agent': self.ua }
            url     = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.AGENTS_EP
            r       = requests.get(url, cookies=self.authn.cookies, headers=headers)
            j       = json.loads(r.text)

            self.json_out(j)

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()
    
    def get_configuration(self, EP):
        try:
            headers = { 'Content-type': 'application/json', 'User-Agent': self.ua }
            url     = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + EP
            r       = requests.get(url, cookies=self.authn.cookies, headers=headers)
            j       = json.loads(r.text)

            self.json_out(j)
        
        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def post_configuration(self, EP):
        try:
            headers = { 'Content-type': 'application/json', 'User-Agent': self.ua }
            url     = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + EP

            with open(self.file) as data_file:    
                data = json.load(data_file)

            for config in data['data']:
                del config['created']
                del config['createdBy']
                del config['id']
                
                r = requests.post(url, cookies=self.authn.cookies, headers=headers, json=config)
                j = json.loads(r.text)

                if 'message' in j:
                    print('Data: %s ' % json.dumps(config))
                    raise ValueError(j['message'])

            print("Post complete!")

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def update_configuration(self, EP):
        headers = { 'Content-type': 'application/json', 'User-Agent': self.ua }
        url     = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + EP
    
    def delete_configuration(self, EP):
        try:
            headers = { 'Content-type': 'application/json', 'User-Agent': self.ua }
            url     = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + EP

            with open(self.file) as data_file:    
                    data = json.load(data_file)

            for config in data['data']:
                url = url + "/" + config['id']
                r = requests.delete(url, cookies=self.authn.cookies, headers=headers)

            print("Delete complete!")

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def get_whitelist_parameters(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__paramwhitelist_get
        # /corps/{corpName}/sites/{siteName}/paramwhitelist
        self.get_configuration(self.WLPARAMS_EP)
    
    def post_whitelist_parameters(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__paramwhitelist_post
        # /corps/{corpName}/sites/{siteName}/paramwhitelist
        self.post_configuration(self.WLPARAMS_EP)
    
    def delete_whitelist_parameters(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__paramwhitelist__paramID__delete
        # /corps/{corpName}/sites/{siteName}/paramwhitelist/{paramID}
        self.delete_configuration(self.WLPARAMS_EP)
    
    def get_whitelist_paths(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist_get
        # /corps/{corpName}/sites/{siteName}/pathwhitelist
        self.get_configuration(self.WLPATHS_EP)
    
    def post_whitelist_paths(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist_post
        # /corps/{corpName}/sites/{siteName}/pathwhitelist
        self.post_configuration(self.WLPATHS_EP)
    
    def delete_whitelist_paths(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist__pathID__delete
        # /corps/{corpName}/sites/{siteName}/pathwhitelist/{pathID}
        self.delete_configuration(self.WLPATHS_EP)
    
    def get_whitelist(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__whitelist_get
        # /corps/{corpName}/sites/{siteName}/whitelist
        self.get_configuration(self.WHITELIST_EP)
    
    def post_whitelist(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist_post
        # /corps/{corpName}/sites/{siteName}/whitelist
        self.post_configuration(self.WHITELIST_EP)
    
    def delete_whitelist(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist__pathID__delete
        # /corps/{corpName}/sites/{siteName}/whitelist/{source}
        self.delete_configuration(self.WHITELIST_EP)
    
    def get_blacklist(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__blacklist_get
        # /corps/{corpName}/sites/{siteName}/blacklist
        self.get_configuration(self.BLACKLIST_EP)
    
    def post_blacklist(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathblacklist_post
        # /corps/{corpName}/sites/{siteName}/blacklist
        self.post_configuration(self.BLACKLIST_EP)
    
    def delete_blacklist(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathblacklist__pathID__delete
        # /corps/{corpName}/sites/{siteName}/blacklist/{source}
        self.delete_configuration(self.BLACKLIST_EP)
    
    def get_redactions(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__redactions_get
        # /corps/{corpName}/sites/{siteName}/redactions
        self.get_configuration(self.REDACTIONS_EP)
    
    def post_redactions(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__redactions_post
        # /corps/{corpName}/sites/{siteName}/redactions
        self.post_configuration(self.REDACTIONS_EP)
    
    def delete_redactions(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__redactions__field__delete
        # /corps/{corpName}/sites/{siteName}/redactions/{field}
        self.delete_configuration(self.REDACTIONS_EP)
    
    def json_out(self, j):
        if 'message' in j:
            raise ValueError(j['message'])

        if 'json' == self.format:
            if not self.file:
                print('%s' % json.dumps(j))

            else:
                with open(self.file, 'a') as outfile:
                    outfile.write('%s' % json.dumps(j))
        
        elif 'csv' == self.format:
            print("CSV output not availible for this request.")

    def __init__(self):
        self.base_url = self.url + self.version


if __name__ == '__main__':
    TAGLIST = ('SQLI', 'XSS', 'CMDEXE', 'TRAVERSAL', 'USERAGENT', 'BACKDOOR', 'SCANNER', 'RESPONSESPLIT', 'CODEINJECTION',
        'HTTP4XX', 'HTTP404', 'HTTP500', 'SANS', 'DATACENTER', 'TORNODE', 'NOUA', 'NOTUTF8', 'BLOCKED', 'PRIVATEFILES', 'FORCEFULBROWSING', 'WEAKTLS')
    
    parser = argparse.ArgumentParser(description='Signal Sciences API Client.', prefix_chars='--')
    
    parser.add_argument('--from',   help='Filter results from a specified time.', dest='from_time', metavar=' =<value>', type=str, default=None)
    parser.add_argument('--until',  help='Filter results until a specified time.', dest='until_time', metavar='=<value>')
    parser.add_argument('--tags',   help='Filter results on one or more tags.', nargs='*')
    parser.add_argument('--ctags',  help='Filter results on one or more custom tags.', nargs='*')
    parser.add_argument('--server', help='Filter results by server name.', default=None)
    parser.add_argument('--limit',  help='Limit the number of results returned from the server (default: 100).', type=int, default=100)
    parser.add_argument('--field',  help='Specify fields to return (default: data).', type=str, default=None, choices=['all', 'totalCount', 'next', 'data'])
    parser.add_argument('--file',   help='Output results to the specified file.', type=str, default=None)
    parser.add_argument('--list',   help='List all supported tags', default=False, action='store_true')
    parser.add_argument('--format', help='Specify output format (default: json).', type=str, default='json', choices=['json', 'csv'])
    parser.add_argument('--sort',   help='Specify sort order (default: desc).', type=str, default=None, choices=['desc', 'asc'])
    parser.add_argument('--agents', help='Retrieve agent metrics.', default=False, action='store_true')
    parser.add_argument('--feed',   help='Retrieve data feed.', default=False, action='store_true')
    parser.add_argument('--whitelist-parameters',  help='Retrieve whitelist parameters.', default=False, action='store_true')
    parser.add_argument('--whitelist-parameters-add',  help='Add whitelist parameters.', default=False, action='store_true')
    parser.add_argument('--whitelist-parameters-delete',  help='Delete whitelist parameters.', default=False, action='store_true')
    parser.add_argument('--whitelist-paths',  help='Retrieve whitelist paths.', default=False, action='store_true')
    parser.add_argument('--whitelist-paths-add',  help='Add whitelist paths.', default=False, action='store_true')
    parser.add_argument('--whitelist-paths-delete',  help='Delete whitelist paths.', default=False, action='store_true')
    parser.add_argument('--whitelist',  help='Retrieve IP whitelist.', default=False, action='store_true')
    parser.add_argument('--whitelist-add',  help='Add to IP whitelist.', default=False, action='store_true')
    parser.add_argument('--whitelist-delete',  help='Delete IP whitelist.', default=False, action='store_true')
    parser.add_argument('--blacklist',  help='Retrieve IP blacklist.', default=False, action='store_true')
    parser.add_argument('--blacklist-add',  help='Add to IP blacklist.', default=False, action='store_true')
    parser.add_argument('--blacklist-delete',  help='Delete IP blacklist.', default=False, action='store_true')
    parser.add_argument('--redactions',  help='Retrieve redactions.', default=False, action='store_true')
    parser.add_argument('--redactions-add',  help='Add to redactions.', default=False, action='store_true')
    parser.add_argument('--redactions-delete',  help='Delete redactions.', default=False, action='store_true')
    
    arguments = parser.parse_args()
    
    # list supported tags and quit
    if arguments.list:
        print 'Supported tags:'
        for tag in TAGLIST:
            print('\t%s' % str(tag))

        quit()

    # setup and run api query
    sigsci       = SigSciAPI()
    
    # first get configuration, environment variables (if set) override 
    # settings specified at the begining of this script.
    sigsci.email      = os.environ.get('SIGSCI_EMAIL')    if None != os.environ.get('SIGSCI_EMAIL') else EMAIL
    sigsci.pword      = os.environ.get("SIGSCI_PASSWORD") if None != os.environ.get('SIGSCI_PASSWORD') else PASSWORD
    sigsci.corp       = os.environ.get("SIGSCI_CORP")     if None != os.environ.get('SIGSCI_CORP') else CORP
    sigsci.site       = os.environ.get("SIGSCI_SITE")     if None != os.environ.get('SIGSCI_SITE') else SITE
    sigsci.from_time  = os.environ.get("SIGSCI_FROM")     if None != os.environ.get('SIGSCI_FROM') else FROM
    sigsci.until_time = os.environ.get("SIGSCI_UNTIL")    if None != os.environ.get('SIGSCI_UNTIL') else UNTIL
    sigsci.tags       = os.environ.get("SIGSCI_TAGS")     if None != os.environ.get('SIGSCI_TAGS') else TAGS
    sigsci.ctags      = os.environ.get("SIGSCI_CTAGS")    if None != os.environ.get('SIGSCI_CTAGS') else CTAGS
    sigsci.server     = os.environ.get("SIGSCI_SERVER")   if None != os.environ.get('SIGSCI_SERVER') else SERVER
    sigsci.limit      = os.environ.get("SIGSCI_LIMIT")    if None != os.environ.get('SIGSCI_LIMIT') else LIMIT
    sigsci.field      = os.environ.get("SIGSCI_FIELD")    if None != os.environ.get('SIGSCI_FIELD') else FIELD
    sigsci.file       = os.environ.get("SIGSCI_FILE")     if None != os.environ.get('SIGSCI_FILE') else FILE
    sigsci.format     = os.environ.get("SIGSCI_FORMAT")   if None != os.environ.get('SIGSCI_FORMAT') else FORMAT
    sigsci.sort       = os.environ.get("SIGSCI_SORT")     if None != os.environ.get('SIGSCI_SORT') else SORT
    sigsci.agents     = os.environ.get("SIGSCI_AGENTS")   if None != os.environ.get('SIGSCI_AGENTS') else AGENTS
    sigsci.feed       = os.environ.get("SIGSCI_FEED")     if None != os.environ.get('SIGSCI_FEED') else FEED
    sigsci.whitelist_parameters        = os.environ.get("SIGSCI_WHITELIST_PARAMETERS")        if None != os.environ.get('SIGSCI_WHITELIST_PARAMETERS') else WHITELIST_PARAMETERS
    sigsci.whitelist_parameters_add    = os.environ.get("SIGSCI_WHITELIST_PARAMETERS_ADD")    if None != os.environ.get('SIGSCI_WHITELIST_PARAMETERS_ADD') else WHITELIST_PARAMETERS_ADD
    sigsci.whitelist_parameters_delete = os.environ.get("SIGSCI_WHITELIST_PARAMETERS_DELETE") if None != os.environ.get('SIGSCI_WHITELIST_PARAMETERS_DELETE') else WHITELIST_PARAMETERS_DELETE
    sigsci.whitelist_paths             = os.environ.get("SIGSCI_WHITELIST_PATHS")             if None != os.environ.get('SIGSCI_WHITELIST_PATHS') else WHITELIST_PATHS
    sigsci.whitelist_paths_add         = os.environ.get("SIGSCI_WHITELIST_PATHS_ADD")         if None != os.environ.get('SIGSCI_WHITELIST_PATHS_ADD') else WHITELIST_PATHS_ADD
    sigsci.whitelist_paths_delete      = os.environ.get("SIGSCI_WHITELIST_PATHS_DELETE")      if None != os.environ.get('SIGSCI_WHITELIST_PATHS_DELETE') else WHITELIST_PATHS_DELETE
    sigsci.whitelist                   = os.environ.get("SIGSCI_WHITELIST")                   if None != os.environ.get('SIGSCI_WHITELIST') else WHITELIST
    sigsci.whitelist_add               = os.environ.get("SIGSCI_WHITELIST_ADD")               if None != os.environ.get('SIGSCI_WHITELIST_ADD') else WHITELIST_ADD
    sigsci.whitelist_delete            = os.environ.get("SIGSCI_WHITELIST_DELETE")            if None != os.environ.get('SIGSCI_WHITELIST_DELETE') else WHITELIST_DELETE
    sigsci.blacklist                   = os.environ.get("SIGSCI_BLACKLIST")                   if None != os.environ.get('SIGSCI_BLACKLIST') else BLACKLIST
    sigsci.blacklist_add               = os.environ.get("SIGSCI_BLACKLIST_ADD")               if None != os.environ.get('SIGSCI_BLACKLIST_ADD') else BLACKLIST_ADD
    sigsci.blacklist_delete            = os.environ.get("SIGSCI_BLACKLIST_DELETE")            if None != os.environ.get('SIGSCI_BLACKLIST_DELETE') else BLACKLIST_DELETE
    sigsci.redactions                  = os.environ.get("SIGSCI_REDACTIONS")                  if None != os.environ.get('SIGSCI_REDACTIONS') else REDACTIONS
    sigsci.redactions_add              = os.environ.get("SIGSCI_REDACTIONS_ADD")              if None != os.environ.get('SIGSCI_REDACTIONS_ADD') else REDACTIONS_ADD
    sigsci.redactions_delete           = os.environ.get("SIGSCI_REDACTIONS_DELETE")           if None != os.environ.get('SIGSCI_REDACTIONS_DELETE') else REDACTIONS_DELETE
    
    # if command line arguments exist then override any previously set values.
    # note: there is no command line argument for EMAIL, PASSWORD, CORP, or SITE.
    sigsci.from_time  = arguments.from_time  if None != arguments.from_time else sigsci.from_time
    sigsci.until_time = arguments.until_time if None != arguments.until_time else sigsci.until_time
    sigsci.tags       = arguments.tags       if None != arguments.tags else sigsci.tags
    sigsci.ctags      = arguments.ctags      if None != arguments.ctags else sigsci.ctags        
    sigsci.server     = arguments.server     if None != arguments.server else sigsci.server
    sigsci.limit      = arguments.limit      if None != arguments.limit else sigsci.limit
    sigsci.field      = arguments.field      if None != arguments.field else sigsci.field
    sigsci.file       = arguments.file       if None != arguments.file else sigsci.file
    sigsci.format     = arguments.format     if None != arguments.format else sigsci.format
    sigsci.sort       = arguments.sort       if None != arguments.sort else sigsci.sort
    sigsci.agents     = arguments.agents     if None != arguments.agents else sigsci.agents
    sigsci.feed       = arguments.feed       if None != arguments.feed else sigsci.feed
    sigsci.whitelist_parameters        = arguments.whitelist_parameters        if None != arguments.whitelist_parameters else sigsci.whitelist_parameters
    sigsci.whitelist_parameters_add    = arguments.whitelist_parameters_add    if None != arguments.whitelist_parameters_add else sigsci.whitelist_parameters_add
    sigsci.whitelist_parameters_delete = arguments.whitelist_parameters_delete if None != arguments.whitelist_parameters_delete else sigsci.whitelist_parameters_delete
    sigsci.whitelist_paths             = arguments.whitelist_paths             if None != arguments.whitelist_paths else sigsci.whitelist_paths
    sigsci.whitelist_paths_add         = arguments.whitelist_paths_add         if None != arguments.whitelist_paths_add else sigsci.whitelist_paths_add
    sigsci.whitelist_paths_delete      = arguments.whitelist_paths_delete      if None != arguments.whitelist_paths_delete else sigsci.whitelist_paths_delete
    sigsci.whitelist                   = arguments.whitelist                   if None != arguments.whitelist else sigsci.whitelist
    sigsci.whitelist_add               = arguments.whitelist_add               if None != arguments.whitelist_add else sigsci.whitelist_add
    sigsci.whitelist_delete            = arguments.whitelist_delete            if None != arguments.whitelist_delete else sigsci.whitelist_delete
    sigsci.blacklist                   = arguments.blacklist                   if None != arguments.blacklist else sigsci.blacklist
    sigsci.blacklist_add               = arguments.blacklist_add               if None != arguments.blacklist_add else sigsci.blacklist_add
    sigsci.blacklist_delete            = arguments.blacklist_delete            if None != arguments.blacklist_delete else sigsci.blacklist_delete
    sigsci.redactions                  = arguments.redactions                  if None != arguments.redactions else sigsci.redactions
    sigsci.redactions_add              = arguments.redactions_add              if None != arguments.redactions_add else sigsci.redactions_add
    sigsci.redactions_delete           = arguments.redactions_delete           if None != arguments.redactions_delete else sigsci.redactions_delete
    
    # determine if we are getting agent metrics or performing a query.
    if sigsci.agents:
        # authenticate and get agent metrics
        if sigsci.authenticate():
            sigsci.get_agent_metrics()
    
    elif sigsci.feed:
        # authenticate and get feed
        if sigsci.authenticate():
            sigsci.get_feed_requests()
    
    elif sigsci.whitelist_parameters:
        # authenticate and get whitelist parameters
        if sigsci.authenticate():
            sigsci.get_whitelist_parameters()
    
    elif sigsci.whitelist_parameters_add:
        # authenticate and post whitelist parameters
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_whitelist_parameters()
    
    elif sigsci.whitelist_parameters_delete:
        # authenticate and delete whitelist parameters
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_whitelist_parameters()
    
    elif sigsci.whitelist_paths:
        # authenticate and get whitelist paths
        if sigsci.authenticate():
            sigsci.get_whitelist_paths()
    
    elif sigsci.whitelist_paths_add:
        # authenticate and post whitelist paths
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_whitelist_paths()
    
    elif sigsci.whitelist_paths_delete:
        # authenticate and delete whitelist paths
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_whitelist_paths()
    
    elif sigsci.whitelist:
        # authenticate and get ip whitelist
        if sigsci.authenticate():
            sigsci.get_whitelist()
    
    elif sigsci.whitelist_add:
        # authenticate and post ip whitelist
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_whitelist()
    
    elif sigsci.whitelist_delete:
        # authenticate and delete ip whitelist
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_whitelist()
    
    elif sigsci.blacklist:
        # authenticate and get ip blacklist
        if sigsci.authenticate():
            sigsci.get_blacklist()
    
    elif sigsci.blacklist_add:
        # authenticate and post ip blacklist
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_blacklist()
    
    elif sigsci.blacklist_delete:
        # authenticate and delete ip blacklist
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_blacklist()
    
    elif sigsci.redactions:
        # authenticate and get redactions
        if sigsci.authenticate():
            sigsci.get_redactions()
    
    elif sigsci.redactions_add:
        # authenticate and post redactions
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_redactions()
    
    elif sigsci.redactions_delete:
        # authenticate and delete redactions
        if sigsci.authenticate():
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_redactions()
    
    else:
        # verify provided tags are supported tags
        if None != sigsci.tags:
            for tag in sigsci.tags:
                if not set([tag.upper()]).issubset(set(TAGLIST)):
                    print('Invalid tag in tag list: %s' % str(tag))
                    quit()
                    
        # authenticate, build the query, and run the query.
        if sigsci.authenticate():
            sigsci.build_query()
            sigsci.query_api()
