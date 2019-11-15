CLEAN_REPO = True

SPEC_REPO = '/mnt/c/github_fork/azure-rest-api-specs'

SDK_REPO = '/mnt/c/github/azure-sdk-for-java'

# SDK_TO_UPDATE = ['keyvault']

SDK_TO_UPDATE = ['advisor', 'apimanagement', 'appconfiguration', 'applicationinsights', 'appplatform', 'appservice',
                 'authorization', 'automation', 'azurestack', 'batchai', 'cognitiveservices', 'compute',
                 'containerinstance', 'containerregistry', 'containerservice', 'cosmosdb', 'costmanagement',
                 'datalakeanalytics', 'datalakestore', 'datamigration', 'devspaces', 'devtestlabs', 'dns',
                 'edgegateway', 'eventgrid', 'eventhubs', 'features', 'hanaonazure', 'hdinsight', 'iotcentral',
                 'iothub', 'kusto', 'labservices', 'locks', 'loganalytics', 'logic', 'machinelearningservices',
                 'mariadb', 'marketplaceordering', 'mediaservices', 'mixedreality', 'monitor', 'mysql', 'netapp',
                 'network', 'notificationhubs', 'operationsmanagement', 'peering', 'policyinsights', 'policy',
                 'postgresql', 'privatedns', 'recoveryservices.backup', 'recoveryservices',
                 'recoveryservices.siterecovery', 'redis', 'relay', 'resourcegraph', 'resourcehealth', 'resources',
                 'search', 'servicebus', 'servicefabric', 'signalr', 'sql', 'sqlvirtualmachine', 'storagecache',
                 'storageimportexport', 'storage', 'streamanalytics', 'vmwarecloudsimple'
]

SDK_SPEC_MAP = {
    'appservice': 'web',
    'cosmosdb': 'cosmos-db',
    'costmanagement': 'cost-management',
    'datalakeanalytics': 'datalake-analytics',
    'datalakestore': 'datalake-store',
    # 'edgegateway': '',
    'eventhubs': 'eventhub',
    'features': 'resources',
    'kusto': 'azure-kusto',
    'locks': 'resources',
    'loganalytics': 'operationalinsights',
    # 'mixedreality': 'mixedreality',
    'policy': 'resources',
    'resources': 'resources',
    'recoveryservices.backup': 'recoveryservicesbackup',
    'recoveryservices.siterecovery': 'recoveryservicessiterecovery'
}

POM_TEMPLATE = r'''<!-- Copyright (c) Microsoft Corporation. All rights reserved.
     Licensed under the MIT License. -->
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.azure</groupId>
  <artifactId>azure-{service}-management</artifactId>
  <packaging>pom</packaging>
  <version>1.0.0</version>  <!-- Need not change for every release-->
  <modules>
{modules}  </modules>
</project>
'''

EXCLUDE_DIRS_PREFIX = [
    'azure-data',
    'azure-messaging',
    'azure-storage',
    'azure-security',
    'microsoft-azure',
    'ms-azure'
]

YAML_TEMPLATE = r'''resources:
  repositories:
    - repository: azure-sdk-build-tools
      type: git
      name: internal/azure-sdk-build-tools

trigger:
  branches:
    include:
      - master
      - feature/*
      - hotfix/*
      - release/*
  paths:
    include:
      - sdk/{service}/
{excludes}
pr:
  branches:
    include:
      - master
      - feature/*
      - hotfix/*
      - release/*
  paths:
    include:
      - sdk/{service}/
{excludes}

variables:
  BuildOptions: '--batch-mode -Dgpg.skip -Dmaven.wagon.http.pool=false'
  ServiceDirectory: {service}
  ProfileFlag: ''

jobs:
  - job: 'Build'

    variables:
      - template: ../../eng/pipelines/templates/variables/globals.yml

    strategy:
      matrix:
        Java 8:
          ArtifactName: 'packages'
          JavaVersion: '1.8'
        Java 7:
          ArtifactName: 'packages'
          JavaVersion: '1.7'

    pool:
      vmImage: 'ubuntu-16.04'

    steps:
      - task: Maven@3
        displayName: 'Build'
        inputs:
          mavenPomFile: sdk/$(ServiceDirectory)/pom.mgmt.xml
          goals: 'compile'
          options: '$(BuildOptions) $(ProfileFlag) "-DpackageOutputDirectory=$(Build.ArtifactStagingDirectory)" -DskipTests'
          mavenOptions: '$(MemoryOptions) $(LoggingOptions)'
          javaHomeOption: 'JDKVersion'
          jdkVersionOption: $(JavaVersion)
          jdkArchitectureOption: 'x64'
          publishJUnitResults: false

      - task: PublishTestResults@2
        condition: succeededOrFailed()
        inputs:
          mergeTestResults: true
          testRunTitle: 'On Java $(JavaVersion)'
'''
