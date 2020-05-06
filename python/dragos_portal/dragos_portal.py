#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A Python wrapper client for the Dragos portal API"""

from configparser import RawConfigParser
from pathlib import Path
import re
import requests
import urllib3

class DragosPortalAPI:
    def __init__(self, config_filename):
        portal_config = RawConfigParser()
        portal_config.read(config_filename)

        token = portal_config.get('dragos portal', 'access_token')
        key = portal_config.get('dragos portal', 'access_key')

        if not token:
            raise 'Config is Missing access_token'

        if not key:
            raise 'Config is Missing access_key'

        try:
            self.url = portal_config.get('dragos portal', 'url', fallback='https://portal.dragos.com/api/v1/')
            self.debug = portal_config.getboolean('dragos portal', 'debug', fallback=False)
            self.headers = { 'Api-Token': token, 'Api-Secret': key }
            self.ssl_verify = '-local' not in self.url # relax SSL verification for local development
            if not self.ssl_verify:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        except:
            raise('error reading Dragos config')


    def get_intel_report_pdf(self, url, **kwargs):
        if kwargs['debug']:
            print('Fetching %s' % url)

        request = requests.get(url, headers = self.headers, verify=self.ssl_verify)

        if request.status_code == 200:
            base_path = './'
            if 'save_dir' in kwargs:
                base_path = kwargs['save_dir'] + '/'

            filename = re.findall('filename="?([^"]+)"?', request.headers.get('content-disposition'))[0]
            filepath = Path(str(base_path) + filename)

            if kwargs['debug']:
                print('Saving %s' % filepath)

            open(filepath, 'wb').write(request.content)
        else:
            print('Could not fetch %s' % url)


    def get_intel_reports_page(self, page=1, **kwargs):
        url = self.url + 'products?page_size=500'
        if kwargs['updated_after']:
            url += '&updated_after=%s' % kwargs['updated_after']

        if kwargs['debug']:
            print('Fetching %s' % url)

        response = requests.get(url + '&page=%i' % page, headers=self.headers, verify=self.ssl_verify)

        if response.status_code == 200:
            return response.json()
        else:
            raise response.body


    def get_intel_reports(self, **kwargs):
        reports = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            data = self.get_intel_reports_page(page, **kwargs)
            total_pages = data['total_pages']
            reports += data['products']
            page += 1

        return reports


    def get_indicators_page(self, page=1, **kwargs):
        url = self.url + 'indicators?page_size=1000'
        if kwargs['updated_after']:
            url += '&updated_after=%s' % kwargs['updated_after']

        if kwargs['debug']:
            print('Fetching %s' % url)

        response = requests.get(url + '&page=%i' % page, headers=self.headers, verify=self.ssl_verify)

        if response.status_code == 200:
            return response.json()
        else:
            raise response.body


    def get_indicators(self, **kwargs):
        indicators = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            data = self.get_indicators_page(page, **kwargs)
            indicators += data['indicators']
            total_pages = data['total_pages']
            page += 1

        return indicators
