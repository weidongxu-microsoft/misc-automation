from datetime import datetime, timedelta, timezone
import re
import itertools
import requests
import logging


date_start = datetime.strptime('09/01/2022/+00:00', '%m/%d/%Y/%z')
date_end = datetime.strptime('09/30/2022/+00:00', '%m/%d/%Y/%z')
regex_match = 'azure-resourcemanager.*_.+'
package_regex_group = '(.*)_.*'
version_regex_group = '.*_(.*)'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %X')

packages = []
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
                        packages.append((package, version))
    else:
        logging.error(f'Request failed: {releases_response.status_code}\n{releases_response.json()}')
        break

packages.sort()
for package in packages:
    preview = '(preview)' if 'beta' in package[1] else ''
    print(f'{package[0]} {preview}')
