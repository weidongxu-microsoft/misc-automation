import os
import re

SDK_REPO = 'c:/github/azure-sdk-for-java/sdk/resourcemanager'

README_TEMPLATE = '''
For documentation on how to use this package, please see [Azure Management Libraries for Java](https://aka.ms/azsdk/java/mgmt).

## Getting started

### Prerequisites

- [Java Development Kit (JDK)][jdk] with version 8 or above
- [Azure Subscription][azure_subscription]

### Adding the package to your product

[//]: # ({x-version-update-start;com.azure.resourcemanager:azure-resourcemanager-{{sdk}};current})
```xml
<dependency>
    <groupId>com.azure.resourcemanager</groupId>
    <artifactId>azure-resourcemanager-{{sdk}}</artifactId>
    <version>{{sdk_version}}</version>
</dependency>
```
[//]: # ({x-version-update-end})

### Include the recommended packages

Azure Management Libraries require a `TokenCredential` implementation for authentication and an `HttpClient` implementation for HTTP client.

[Azure Identity][azure_identity] package and [Azure Core Netty HTTP][azure_core_http_netty] package provide the default implementation.

### Authentication

By default, Azure Active Directory token authentication depends on correct configure of following environment variables.

- `AZURE_CLIENT_ID` for Azure client ID.
- `AZURE_TENANT_ID` for Azure tenant ID.
- `AZURE_CLIENT_SECRET` or `AZURE_CLIENT_CERTIFICATE_PATH` for client secret or client certificate.

In addition, Azure subscription ID can be configured via environment variable `AZURE_SUBSCRIPTION_ID`.

With above configuration, `azure` client can be authenticated by following code:

<!-- embedme ./src/samples/java/com/azure/resourcemanager/{{sdk}}/ReadmeSamples.java#L21-L26 -->
```java
AzureProfile profile = new AzureProfile(AzureEnvironment.AZURE);
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .authorityHost(profile.getEnvironment().getActiveDirectoryEndpoint())
    .build();
{{sdk_manager}} manager = {{sdk_manager}}
    .authenticate(credential, profile);
```

The sample code assumes global Azure. Please change `AzureEnvironment.AZURE` variable if otherwise.

See [Authentication][authenticate] for more options.

## Key concepts

See [API design][design] for general introduction on design and key concepts on Azure Management Libraries.

## Examples

See [Samples][sample] for code snippets and samples.

## Troubleshooting

## Next steps

## Contributing

If you would like to become an active contributor to this project please follow the instructions provided in [Microsoft
Azure Projects Contribution Guidelines](https://azure.github.io/guidelines.html).

1. Fork it
1. Create your feature branch (`git checkout -b my-new-feature`)
1. Commit your changes (`git commit -am 'Add some feature'`)
1. Push to the branch (`git push origin my-new-feature`)
1. Create new Pull Request

<!-- LINKS -->
[jdk]: https://docs.microsoft.com/java/azure/jdk/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_identity]: https://github.com/Azure/azure-sdk-for-java/blob/master/sdk/identity/azure-identity
[azure_core_http_netty]: https://github.com/Azure/azure-sdk-for-java/blob/master/sdk/core/azure-core-http-netty
[authenticate]: https://github.com/Azure/azure-sdk-for-java/blob/master/sdk/resourcemanager/docs/AUTH.md
[sample]: https://github.com/Azure/azure-sdk-for-java/blob/master/sdk/resourcemanager/docs/SAMPLE.md
[design]: https://github.com/Azure/azure-sdk-for-java/blob/master/sdk/resourcemanager/docs/DESIGN.md
'''

README_SAMPLES_TEMPLATE='''// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

package com.azure.resourcemanager.{{sdk}};

import com.azure.core.credential.TokenCredential;
import com.azure.core.management.AzureEnvironment;
import com.azure.core.management.profile.AzureProfile;
import com.azure.identity.DefaultAzureCredentialBuilder;

/**
 * WARNING: MODIFYING THIS FILE WILL REQUIRE CORRESPONDING UPDATES TO README.md FILE. LINE NUMBERS
 * ARE USED TO EXTRACT APPROPRIATE CODE SEGMENTS FROM THIS FILE. ADD NEW CODE AT THE BOTTOM TO AVOID CHANGING
 * LINE NUMBERS OF EXISTING CODE SAMPLES.
 *
 * Code samples for the README.md
 */
public class ReadmeSamples {

    public void authenticate() {
        AzureProfile profile = new AzureProfile(AzureEnvironment.AZURE);
        TokenCredential credential = new DefaultAzureCredentialBuilder()
            .authorityHost(profile.getEnvironment().getActiveDirectoryEndpoint())
            .build();
        {{sdk_manager}} manager = {{sdk_manager}}
            .authenticate(credential, profile);
    }
}
'''


def update_readme(readme_dir: str, sdk_name: str, sdk_manager_name: str):
    if os.path.exists(readme_dir):
        keep_lines = []
        sdk_version = ''
        with open(readme_dir, 'r') as f:
            keep = True
            for line in f.readlines():
                if keep:
                    keep_lines.append(line)
                if line.startswith('Azure Resource Manager'):
                    keep = False

                line = line.strip()
                if line.startswith('<version>'):
                    match = re.search('<version>(.+?)</version>', line)
                    if match:
                        sdk_version = match.group(1)
                    break
        with open(readme_dir, 'w') as f:
            content = README_TEMPLATE\
                .replace('{{sdk}}', sdk_name)\
                .replace('{{sdk_manager}}', sdk_manager_name)\
                .replace('{{sdk_version}}', sdk_version)
            content = ''.join(keep_lines) + content
            f.write(content)


def update_sample(sample_dir: str, sdk_name: str, sdk_manager_name: str):
    sample_file_dir = os.path.join(sample_dir, 'ReadmeSamples.java')
    if not os.path.exists(sample_file_dir):
        os.makedirs(sample_dir, exist_ok=True)
        with open(sample_file_dir, 'w') as f:
            content = README_SAMPLES_TEMPLATE\
                .replace('{{sdk}}', sdk_name)\
                .replace('{{sdk_manager}}', sdk_manager_name)
            f.write(content)


def main():
    for sdk_artifact in os.listdir(SDK_REPO):
        sdk_dir = os.path.join(SDK_REPO, sdk_artifact)
        if sdk_artifact.startswith('azure-resourcemanager-') \
                and not ('perf' in sdk_artifact or 'samples' in sdk_artifact or 'test' in sdk_artifact) \
                and os.path.isdir(sdk_dir):
            match = re.search('azure-resourcemanager-(.+?)$', sdk_artifact)
            if match:
                sdk_name = match.group(1)
                readme_dir = os.path.join(sdk_dir, 'README.md')
                sdk_manager_dir = os.path.join(sdk_dir, 'src', 'main', 'java', 'com', 'azure', 'resourcemanager', sdk_name)
                sample_dir = os.path.join(sdk_dir, 'src', 'samples', 'java', 'com', 'azure', 'resourcemanager', sdk_name)
                sdk_manager_name = ''
                if os.path.isdir(sdk_manager_dir):
                    for filename in os.listdir(sdk_manager_dir):
                        if filename.endswith('Manager.java'):
                            sdk_manager_name = filename.replace('.java', '')

                update_readme(readme_dir, sdk_name, sdk_manager_name)
                update_sample(sample_dir, sdk_name, sdk_manager_name)


main()
