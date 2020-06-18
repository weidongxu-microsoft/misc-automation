import os
import logging
import os.path as path
import csv
import json
from enum import Enum

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

SPEC_REPO = 'c:/github/azure-rest-api-specs'


def collect():
    spec_file_infos = list()
    spec_endpoint_infos = list()

    spec_dir = path.join(SPEC_REPO, 'specification')
    for service in os.listdir(spec_dir):
        service_dir = path.join(spec_dir, service)
        if path.isdir(service_dir):
            for plane_name in os.listdir(service_dir):
                try:
                    plane = Plane(plane_name)
                except ValueError:
                    plane = None
                if plane:
                    plane_dir = path.join(service_dir, plane_name)
                    for rp in os.listdir(plane_dir):
                        rp_dir = path.join(plane_dir, rp)
                        if path.isdir(rp_dir):
                            for state_name in os.listdir(rp_dir):
                                try:
                                    state = State(state_name)
                                except ValueError:
                                    state = None
                                if state:
                                    state_dir = path.join(rp_dir, state_name)
                                    for version in os.listdir(state_dir):
                                        version_dir = path.join(state_dir, version)
                                        if path.isdir(version_dir):
                                            for json_filename in os.listdir(version_dir):
                                                json_file = path.join(version_dir, json_filename)
                                                if path.isfile(json_file) and json_filename.endswith('.json'):
                                                    spec_file_info = SpecFile()
                                                    spec_file_info.service = service
                                                    spec_file_info.plane = plane
                                                    spec_file_info.resource_provider = rp
                                                    spec_file_info.state = state
                                                    spec_file_info.version = version
                                                    spec_file_info.name = os.path.splitext(json_filename)[0]
                                                    spec_file_infos.append(spec_file_info)

                                                    with open(json_file, 'r', encoding='utf-8') as jsonfile:
                                                        try:
                                                            spec_json = json.loads(jsonfile.read())
                                                            spec_endpoint_infos.extend(get_spec_endpoint_infos(spec_file_info, spec_json))
                                                        except UnicodeDecodeError:
                                                            logging.warning('failed to read file: {}'.format(json_file))

    with open('spec_file_info.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for info in spec_file_infos:
            csvwriter.writerow(info.csv_row())

    with open('spec_endpoint_info.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for info in spec_endpoint_infos:
            csvwriter.writerow(info.csv_row())


def analysis():
    pd.set_option('display.max_colwidth', -1)

    df = pd.read_csv('spec_endpoint_info.csv', sep=',', header=None)
    df.columns = ['service', 'plane', 'version', 'endpoint']
    df.sort_values('version', ascending=False, inplace=True)
    df.drop_duplicates(['endpoint', 'service'], keep='first', inplace=True)
    df1 = df.groupby('plane').count()
    print(str(df1))

    df2 = df.groupby(['plane', 'service']).count().drop('version', axis=1).sort_values('endpoint', ascending=False)
    print(str(df2.head(50)))


class Plane(Enum):
    DATA = 'data-plane'
    RESOURCE = 'resource-manager'


class State(Enum):
    STABLE = 'stable'
    PREVIEW = 'preview'


class SpecEndpointInfo:
    service: str
    plane: Plane
    version: str
    endpoint: str

    def csv_row(self):
        return [self.service, self.plane.value, self.version, self.endpoint]


class SpecFile:
    service: str
    plane: Plane
    resource_provider: str
    state: State
    version: str
    name: str

    def csv_row(self):
        return [self.service, self.plane.value, self.resource_provider, self.state.value, self.version, self.name.lower()]


def get_spec_endpoint_infos(spec_file_info: SpecFile, spec_json):
    spec_endpoint_infos = list()

    version = spec_json['info']['version']
    for endpoint in spec_json['paths'].keys():
        spec_info = SpecEndpointInfo()
        spec_info.service = spec_file_info.service
        spec_info.plane = spec_file_info.plane
        spec_info.version = version
        spec_info.endpoint = endpoint

        spec_endpoint_infos.append(spec_info)

    return spec_endpoint_infos


if __name__ == '__main__':
    analysis()
