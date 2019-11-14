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
    #    'edgegateway': '',
    'eventhubs': 'eventhub',
    'features': 'resources',
    'kusto': 'azure-kusto',
    'locks': 'resources',
    'loganalytics': 'operationalinsights',
    #    'mixedreality': 'mixedreality',
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

LIBRARIES = '''advisor/resource-manager/v2017_04_19
apimanagement/resource-manager/v2018_06_01_preview
apimanagement/resource-manager/v2019_01_01
appconfiguration/resource-manager/v2019_02_01_preview
appconfiguration/resource-manager/v2019_10_01
applicationinsights/resource-manager/v2015_05_01
appplatform/resource-manager/v2019_05_01_preview
appservice/resource-manager/v2016_03_01
appservice/resource-manager/v2016_08_01
appservice/resource-manager/v2016_09_01
appservice/resource-manager/v2018_02_01
authorization/resource-manager/v2015_06_01
authorization/resource-manager/v2015_07_01
authorization/resource-manager/v2018_07_01_preview
authorization/resource-manager/v2018_09_01_preview
automation/resource-manager/v2015_10_31
automation/resource-manager/v2018_06_30
azurestack/resource-manager/v2017_06_01
batchai/resource-manager/v2017_09_01_preview
batchai/resource-manager/v2018_03_01
batchai/resource-manager/v2018_05_01
cognitiveservices/resource-manager/v2016_02_01_preview
cognitiveservices/resource-manager/v2017_04_18
compute/resource-manager/v2017_03_30
compute/resource-manager/v2017_09_01
compute/resource-manager/v2017_12_01
compute/resource-manager/v2018_04_01
compute/resource-manager/v2018_09_30
containerinstance/resource-manager/v2017_08_01_preview
containerinstance/resource-manager/v2017_10_01_preview
containerinstance/resource-manager/v2017_12_01_preview
containerinstance/resource-manager/v2018_02_01_preview
containerinstance/resource-manager/v2018_04_01
containerinstance/resource-manager/v2018_10_01
containerregistry/resource-manager/v2016_06_27_preview
containerregistry/resource-manager/v2017_03_01
containerregistry/resource-manager/v2017_06_01_preview
containerregistry/resource-manager/v2017_10_01
containerregistry/resource-manager/v2018_02_01_preview
containerregistry/resource-manager/v2018_09_01
containerregistry/resource-manager/v2019_04_01
containerregistry/resource-manager/v2019_06_01_preview
containerservice/resource-manager/v2017_07_01
containerservice/resource-manager/v2017_08_31
containerservice/resource-manager/v2017_09_30
containerservice/resource-manager/v2018_09_30_preview
containerservice/resource-manager/v2019_02_01
containerservice/resource-manager/v2019_04_01
containerservice/resource-manager/v2019_06_01
containerservice/resource-manager/v2019_08_01
cosmosdb/resource-manager/v2015_04_08
cosmosdb/resource-manager/v2019_08_01
cosmosdb/resource-manager/v2019_08_01_preview
costmanagement/resource-manager/v2018_05_31
datalakeanalytics/resource-manager/v2015_10_01_preview
datalakeanalytics/resource-manager/v2016_11_01
datalakestore/resource-manager/v2015_10_01_preview
datalakestore/resource-manager/v2016_11_01
datamigration/resource-manager/v2017_11_15_preview
datamigration/resource-manager/v2018_03_31_preview
datamigration/resource-manager/v2018_07_15_preview
devspaces/resource-manager/v2018_06_01_preview
devtestlabs/resource-manager/v2018_09_15
dns/resource-manager/v2016_04_01
dns/resource-manager/v2017_10_01
edgegateway/resource-manager/v2019_03_01
eventgrid/resource-manager/v2018_01_01
eventgrid/resource-manager/v2018_05_01_preview
eventgrid/resource-manager/v2018_09_15_preview
eventgrid/resource-manager/v2019_01_01
eventgrid/resource-manager/v2019_06_01
eventgrid/resource-manager/v2020_01_01_preview
eventhubs/resource-manager/v2015_08_01
eventhubs/resource-manager/v2017_04_01
eventhubs/resource-manager/v2018_01_01_preview
features/resource-manager/v2015_12_01
hanaonazure/resource-manager/v2017_11_03_preview
hdinsight/resource-manager/v2018_06_01_preview
iotcentral/resource-manager/v2017_07_01_privatepreview
iotcentral/resource-manager/v2018_09_01
iothub/resource-manager/v2018_04_01
iothub/resource-manager/v2018_12_01_preview
iothub/resource-manager/v2019_03_22_preview
kusto/resource-manager/v2018_09_07_preview
kusto/resource-manager/v2019_05_15
kusto/resource-manager/v2019_09_07
labservices/resource-manager/v2018_10_15
locks/resource-manager/v2016_09_01
loganalytics/resource-manager/v2015_03_20
logic/resource-manager/v2016_06_01
logic/resource-manager/v2018_07_01_preview
machinelearningservices/resource-manager/v2019_05_01
mariadb/resource-manager/v2018_06_01
marketplaceordering/resource-manager/v2015_06_01
mediaservices/resource-manager/v2015_10_01
mediaservices/resource-manager/v2018_03_30_preview
mediaservices/resource-manager/v2018_06_01_preview
mediaservices/resource-manager/v2018_07_01
mixedreality/resource-manager/v2019_02_28_preview
monitor/resource-manager/v2015_04_01
monitor/resource-manager/v2015_07_01
monitor/resource-manager/v2016_03_01
monitor/resource-manager/v2017_03_01_preview
monitor/resource-manager/v2017_04_01
monitor/resource-manager/v2017_05_01_preview
monitor/resource-manager/v2018_01_01
monitor/resource-manager/v2018_03_01
monitor/resource-manager/v2018_04_16
monitor/resource-manager/v2018_09_01
mysql/resource-manager/v2017_12_01
mysql/resource-manager/v2017_12_01_preview
netapp/resource-manager/v2017_08_15
netapp/resource-manager/v2019_05_01
netapp/resource-manager/v2019_06_01
netapp/resource-manager/v2019_07_01
netapp/resource-manager/v2019_08_01
network/resource-manager/v2017_10_01
network/resource-manager/v2018_04_01
network/resource-manager/v2018_06_01
network/resource-manager/v2018_07_01
network/resource-manager/v2018_08_01
network/resource-manager/v2018_12_01
network/resource-manager/v2019_02_01
network/resource-manager/v2019_04_01
network/resource-manager/v2019_06_01
network/resource-manager/v2019_07_01
network/resource-manager/v2019_08_01
network/resource-manager/v2019_09_01
notificationhubs/resource-manager/v2014_09_01
notificationhubs/resource-manager/v2016_03_01
notificationhubs/resource-manager/v2017_04_01
operationsmanagement/resource-manager/v2015_11_01_preview
peering/resource-manager/v2019_08_01_preview
policyinsights/resource-manager/v2018_04_04
policyinsights/resource-manager/v2018_07_01_preview
policy/resource-manager/v2016_12_01
policy/resource-manager/v2018_03_01
policy/resource-manager/v2018_05_01
policy/resource-manager/v2019_06_01
postgresql/resource-manager/v2017_12_01
postgresql/resource-manager/v2017_12_01_preview
privatedns/resource-manager/v2018_09_01
recoveryservices.backup/resource-manager/v2016_06_01
recoveryservices.backup/resource-manager/v2016_08_10
recoveryservices.backup/resource-manager/v2016_12_01
recoveryservices.backup/resource-manager/v2017_07_01
recoveryservices/resource-manager/v2016_06_01
recoveryservices.siterecovery/resource-manager/v2018_01_10
redis/resource-manager/v2018_03_01
relay/resource-manager/v2017_04_01
resourcegraph/resource-manager/v2019_04_01
resourcehealth/resource-manager/v2015_01_01
resourcehealth/resource-manager/v2017_07_01
resources/resource-manager/v2016_06_01
resources/resource-manager/v2016_09_01
resources/resource-manager/v2018_02_01
resources/resource-manager/v2018_05_01
resources/resource-manager/v2019_05_01
resources/resource-manager/v2019_06_01
resources/resource-manager/v2019_07_01
search/resource-manager/v2015_02_28
servicebus/resource-manager/v2015_08_01
servicebus/resource-manager/v2017_04_01
servicebus/resource-manager/v2018_01_01_preview
servicefabric/resource-manager/v2018_02_01
signalr/resource-manager/v2018_03_01_preview
signalr/resource-manager/v2018_10_01
sql/resource-manager/v2014_04_01
sql/resource-manager/v2015_05_01_preview
sql/resource-manager/v2017_03_01_preview
sql/resource-manager/v2017_10_01_preview
sql/resource-manager/v2018_06_01_preview
sqlvirtualmachine/resource-manager/v2017_03_01_preview
storagecache/resource-manager/v2019_08_01
storagecache/resource-manager/v2019_11_01
storageimportexport/resource-manager/v2016_11_01
storage/resource-manager/v2016_01_01
storage/resource-manager/v2017_10_01
storage/resource-manager/v2018_02_01
storage/resource-manager/v2018_03_01_preview
storage/resource-manager/v2018_07_01
storage/resource-manager/v2018_11_01
storage/resource-manager/v2019_04_01
storage/resource-manager/v2019_06_01
streamanalytics/resource-manager/v2016_03_01
vmwarecloudsimple/resource-manager/v2019_04_01
'''
