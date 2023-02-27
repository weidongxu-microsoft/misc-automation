from datetime import datetime, timedelta, timezone
import re
import itertools
import requests
import logging


date_start = datetime.strptime('02/01/2018/+00:00', '%m/%d/%Y/%z')
date_end = datetime.strptime('02/28/2023/+00:00', '%m/%d/%Y/%z')
regex_match = 'azure-resourcemanager.*_.+'
package_regex_group = '(.*)_.*'
version_regex_group = '.*_(.*)'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %X')

sdks = {}

for page in itertools.count(start=1):
    request_uri = f'https://api.github.com/repos/azure/azure-sdk-for-java/releases'
    releases_response = requests.get(request_uri,
                                     params={'per_page': 100, 'page': page})
    if releases_response.status_code == 200:
        releases_response_json = releases_response.json()
        if len(releases_response_json) == 0:
            # no more result, we are done
            break
        for release in releases_response_json:
            if not release['draft']:
                published_at = datetime.fromisoformat(release['published_at'].replace('Z', '+00:00'))
                if date_start < published_at < date_end:
                    release_tag = release['tag_name']
                    if re.match(regex_match, release_tag):
                        package = re.match(package_regex_group, release_tag).group(1)
                        version = re.match(version_regex_group, release_tag).group(1)
                        logging.info(f'Found release: {package} {version}')

                        if package in sdks:
                            sdk_version = sdks[package]
                            if '-beta.' in sdk_version and '-beta.' not in version:
                                sdks[package] = version
                        else:
                            sdks[package] = version
    else:
        logging.error(f'Request failed: {releases_response.status_code}\n{releases_response.json()}')
        break

count_stable = len([s for s in sdks.values() if '-beta.' not in s])
logging.info(f'stable SDKs: {count_stable}')
logging.info(f'all SDKs: {len(sdks.keys())}')
