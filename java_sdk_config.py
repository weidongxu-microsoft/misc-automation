CLEAN_REPO = True

SDK_REPO = "c:/github_fork/azure-sdk-for-java"

POM_TEMPLATE = r"""<!-- Copyright (c) Microsoft Corporation. All rights reserved.
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
"""

MGMT_DIRS_PREFIX = "mgmt-v"

EXCLUDE_DIRS_PREFIX = ["azure", "microsoft-azure", "ms-azure"]

YAML_TEMPLATE = r"""resources:
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
    exclude:
      - sdk/{service}/azure
      - sdk/{service}/microsoft-azure
      - sdk/{service}/ms-azure

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
    exclude:
      - sdk/{service}/azure
      - sdk/{service}/microsoft-azure
      - sdk/{service}/ms-azure

stages:
  - template: ../../eng/pipelines/templates/stages/archetype-sdk-management.yml
    parameters:
      ServiceDirectory: {service}
"""
