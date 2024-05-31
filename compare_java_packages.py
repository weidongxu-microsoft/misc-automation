import dataclasses
import logging
import csv
import re
import os
from typing import List, Dict
from urllib.request import urlopen

import yaml

try:
    import pyodbc
except ImportError:
    pyodbc = None
    pass  # pyodbc is required only when KPI_CONNECTION_STRING is set in environment variables


CSV_URL = "https://raw.githubusercontent.com/Azure/azure-sdk/main/_data/releases/latest/java-packages.csv"
TRACK1_PACKAGE_PREFIX = "azure-mgmt-"
TRACK2_PACKAGE_PREFIX = "azure-resourcemanager-"

MAVEN_RESOURCE_MANGER_GROUP_URL = "https://repo1.maven.org/maven2/com/azure/resourcemanager/"

CSV_FILENAME = "compare_java_packages.csv"

SWAGGER_SDK_URL = "https://raw.githubusercontent.com/Azure/azure-sdk-for-java/main/eng/mgmt/automation/api-specs.yaml"

SWAGGER_METADATA_FILENAME = "swagger_metadata.csv"
REST_KPI_FILENAME = "kpi_7d.csv"
REST_KPI_CONNECTION_STRING_ENV = "KPI_CONNECTION_STRING"


@dataclasses.dataclass
class SdkInfo:
    sdk: str
    track1: bool = False
    track1_stable: bool = False
    track1_api_version: str = None
    track2: bool = False
    track2_stable: bool = False
    track2_api_version: str = None

    ring: str = None
    traffic: int = None
    completeness: float = None
    correctness: float = None

    def to_row(self) -> List[str]:
        return [
            self.sdk,
            ("GA" if self.track1_stable else "beta") if self.track1 else None,
            ("GA" if self.track2_stable else "beta") if self.track2 else None,
            self.track1_api_version,
            self.track2_api_version,
        ]


@dataclasses.dataclass
class KpiInfo:
    namespace: str
    name: str
    ring: str
    traffic: int = None
    completeness: float = None
    correctness: float = None


@dataclasses.dataclass
class AggregatedInfo:
    count_track1: int
    count_track2: int
    count_track1_but_no_track2: int


def process_java_packages_csv() -> List[SdkInfo]:
    sdk_info = {}

    logging.info(f"query csv: {CSV_URL}")
    with urlopen(CSV_URL) as csv_response:
        csv_data = csv_response.read()
        csv_str = csv_data.decode("utf-8")
        csv_reader = csv.DictReader(csv_str.split("\n"), delimiter=",", quotechar='"')
    for row in csv_reader:
        package = row["Package"]
        namespace = row["GroupId"]
        version = row["VersionGA"]
        if package.startswith(TRACK1_PACKAGE_PREFIX) and not version.startswith("0."):
            sdk = package[len(TRACK1_PACKAGE_PREFIX) :]
            if sdk not in sdk_info:
                sdk_info[sdk] = SdkInfo(sdk)
            sdk_info[sdk].track1 = True
            if not version == "":
                sdk_info[sdk].track1_stable = True
            # update version, take the latest
            sdk_info[sdk].track1_api_version = compare_version(
                namespace.split(".")[-1], sdk_info[sdk].track1_api_version
            )
        if package.startswith(TRACK2_PACKAGE_PREFIX) and package != TRACK2_PACKAGE_PREFIX + "parent":
            sdk = package[len(TRACK2_PACKAGE_PREFIX) :]
            if sdk not in sdk_info:
                sdk_info[sdk] = SdkInfo(sdk)
            sdk_info[sdk].track2 = True
            if not version == "":
                sdk_info[sdk].track2_stable = True
            sdk_info[sdk].track2_api_version = get_track2_version(
                package, row["VersionPreview"] if version == "" else version
            )

    add_java_packages_maven(sdk_info)

    sdk_info_list = [item for item in sdk_info.values()]
    sdk_info_list.sort(key=lambda r: ("a." if r.track2_api_version else "b.") + r.sdk)

    return sdk_info_list


def add_java_packages_maven(sdk_info: Dict[str, SdkInfo]):
    sdk_list = []
    logging.info(f"query html: {MAVEN_RESOURCE_MANGER_GROUP_URL}")
    with urlopen(MAVEN_RESOURCE_MANGER_GROUP_URL) as html_response:
        html_data = html_response.read()
        html_str = html_data.decode("utf-8")
        for package in re.findall(r'<a href="azure-resourcemanager-[-\w]+/"', html_str):
            package = package[9:-2]
            if package != TRACK2_PACKAGE_PREFIX + "parent":
                sdk = package[len(TRACK2_PACKAGE_PREFIX) :]
                sdk_list.append(sdk)

    for sdk in sdk_list:
        if sdk not in sdk_info or not sdk_info[sdk].track2:
            maven_metadata_url = MAVEN_RESOURCE_MANGER_GROUP_URL + TRACK2_PACKAGE_PREFIX + sdk + "/maven-metadata.xml"
            logging.info(f"query xml: {maven_metadata_url}")
            with urlopen(maven_metadata_url) as xml_response:
                xml_data = xml_response.read()
                xml_str = xml_data.decode("utf-8")
                matched = re.search(r"<latest>(.*)</latest>", xml_str, re.MULTILINE)
                if matched:
                    version = matched.group(1)
                    if sdk not in sdk_info:
                        sdk_info[sdk] = SdkInfo(sdk)
                    sdk_info[sdk].track2 = True
                    if "-beta." not in version:
                        sdk_info[sdk].track2_stable = True
                    sdk_info[sdk].track2_api_version = get_track2_version(TRACK2_PACKAGE_PREFIX + sdk, version)


def join_kpi_csv(sdk_info_list: List[SdkInfo]):
    if not os.path.isfile(SWAGGER_METADATA_FILENAME):
        return

    swagger_sdk_map = {}
    logging.info(f"query yml: {SWAGGER_SDK_URL}")
    with urlopen(SWAGGER_SDK_URL) as yaml_response:
        yaml_data = yaml_response.read()
        yaml_str = yaml_data.decode("utf-8")
        swagger_sdk = yaml.safe_load(yaml_str)
        for key in swagger_sdk:
            value = swagger_sdk[key]
            if "service" in value:
                swagger_sdk_map[key] = value["service"]

    sdk_namespace_map = {}
    with open(SWAGGER_METADATA_FILENAME, "r", newline="", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f, delimiter=",", quotechar='"')
        for row in csv_reader:
            namespace = row["ProviderNamespace"].strip().upper()
            if namespace.startswith("MICROSOFT."):
                swagger_name = row["specRootFolderName"]
                if swagger_name in swagger_sdk_map:
                    sdk_name = swagger_sdk_map[swagger_name]
                else:
                    sdk_name = swagger_name
                sdk_namespace_map[sdk_name] = namespace

    kpi_info: Dict[str, List[KpiInfo]] = query_kpi_info()

    for item in sdk_info_list:
        kpi_item = find_kpi(item.sdk, sdk_namespace_map, kpi_info)
        if kpi_item:
            item.ring = kpi_item.ring
            item.traffic = kpi_item.traffic
            item.completeness = kpi_item.completeness
            item.correctness = kpi_item.correctness


def query_kpi_info() -> Dict[str, List[KpiInfo]]:
    kpi_info: Dict[str, List[KpiInfo]] = {}

    if REST_KPI_CONNECTION_STRING_ENV in os.environ and pyodbc:
        logging.info(f"query database")
        connection_string = os.environ[REST_KPI_CONNECTION_STRING_ENV]
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "select resourceProviderName, ServiceName, ServiceRing, trafficCount, completeness, correctness"
                "  from MonthlySwaggerKPI"
                "  join resourceProvidersMetadata"
                "    on MonthlySwaggerKPI.serviceId = resourceProvidersMetadata.ServiceId"
                "    and MonthlySwaggerKPI.resourceProviderName = resourceProvidersMetadata.[Namespace]"
                "  where month = 'last7days' and environment = 'prod' and validatorId = 'default'"
                "  order by resourceProviderName asc"
            )
            for row in cursor:
                namespace = row[0].strip().upper()
                if namespace.startswith("MICROSOFT."):
                    kpi_item = KpiInfo(
                        namespace, row[1].strip(), row[2].strip(), int(row[3]), float(row[4]), float(row[5])
                    )
                    if namespace not in kpi_info:
                        kpi_info[namespace] = []
                    kpi_info[namespace].append(kpi_item)
    else:
        if os.path.isfile(REST_KPI_FILENAME):
            with open(REST_KPI_FILENAME, "r", newline="", encoding="utf-8") as f:
                csv_reader = csv.DictReader(f, delimiter=",", quotechar='"')
                for row in csv_reader:
                    namespace = row["resourceProviderName"].strip().upper()
                    if namespace.startswith("MICROSOFT."):
                        kpi_item = KpiInfo(
                            namespace,
                            row["ServiceName"].strip(),
                            row["ServiceRing"].strip(),
                            int(row["trafficCount"]),
                            float(row["completeness"]),
                            float(row["correctness"]),
                        )
                        if namespace not in kpi_info:
                            kpi_info[namespace] = []
                        kpi_info[namespace].append(kpi_item)

    return kpi_info


def find_kpi(sdk: str, sdk_namespace_map: Dict[str, str], kpi_info: Dict[str, List[KpiInfo]]) -> KpiInfo or None:
    sdk_service_name_map = {
        "healthcareapis": "FHIR Server",
        "hybridcompute": "Hybrid Resource Provider",
        "mixedreality": "Azure Object Anchors",  # 'Remote Rendering'
        "powerbidedicated": "Power BI",
        "authorization": "Policy Administration Service",
        "containerservice": "Azure Kubernetes Service",
        "privatedns": "Azure DNS Private Zones",
        "recoveryservices": "Backup (MAB)",
        "resources": "Azure Resource Manager",
        "trafficmanager": "WATM",
        "dns": "Azure DNS - Public Zones",
        "redis": "Redis Cache",
        "network": "Regional Network Manager",
        "monitor": "Azure Notification Service",
    }

    if sdk in sdk_namespace_map:
        namespace = sdk_namespace_map[sdk]
        if namespace in kpi_info:
            kpi_items = kpi_info[namespace]

            if len(kpi_items) > 1:
                if sdk in sdk_service_name_map:
                    service_name = sdk_service_name_map[sdk]
                    for kpi_item in kpi_items:
                        if service_name == kpi_item.name:
                            return kpi_item
                else:
                    for kpi_item in kpi_items:
                        if sdk.replace("-", "") in kpi_item.name.lower().replace(" ", ""):
                            return kpi_item

                logging.info("sdk: " + sdk)
                logging.warning("multiple service candidates: " + str([r.name for r in kpi_items]))

            return kpi_items[0]
    else:
        return None


def print_stdout(sdk_info_list: List[SdkInfo]):
    xround = lambda r, n: None if r is None else round(r, n)
    xstr = lambda s: "" if s is None else str(s)

    aggregated_info = aggregate_info(sdk_info_list)

    print(f"Number of track1 packages: {str(aggregated_info.count_track1)}")
    print(f"Number of track2 packages: {str(aggregated_info.count_track2)}")
    print(f"Number of track1 packages not having track2: {str(aggregated_info.count_track1_but_no_track2)}")
    print()

    print(
        "{0: <32}{1: <16}{2: <16}{3: <16}{4: <16}{5: <16}{6: <16}{7: <16}{8: <16}".format(
            "service", "track1", "track2", "track1 api", "track2 api", "ring", "traffic", "completeness", "coverage"
        )
    )
    print()

    for item in sdk_info_list:
        print(
            "{0: <32}{1: <16}{2: <16}{3: <16}{4: <16}{5: <16}{6: <16}{7: <16}{8: <16}".format(
                item.sdk,
                ("GA" if item.track1_stable else "beta") if item.track1 else "",
                ("GA" if item.track2_stable else "beta") if item.track2 else "",
                xstr(item.track1_api_version),
                xstr(item.track2_api_version),
                xstr(item.ring),
                f"{item.traffic:,}" if item.traffic else "",
                xstr(xround(item.completeness, 2)),
                xstr(xround(item.correctness, 2)),
            )
        )


def write_html(sdk_info_list: List[SdkInfo]):
    xround = lambda r, n: None if r is None else round(r, n)
    xstr = lambda s: "" if s is None else str(s)

    aggregated_info = aggregate_info(sdk_info_list)

    response = "<!DOCTYPE html><html><head><title>Java Packages</title></head><body>"

    response += f"<p>Number of track1 packages: {str(aggregated_info.count_track1)}</p>"
    response += f"<p>Number of track2 packages: {str(aggregated_info.count_track2)}</p>"
    response += f"<p>Number of track1 packages not having track2: {str(aggregated_info.count_track1_but_no_track2)}</p>"

    response += '<table style="width:100%"><caption>Java Packages</caption>'
    response += (
        "<thead><tr><th>Service</th><th>Track1</th><th>Track2</th><th>Track1 API</th><th>Track2 API</th>"
        "<th>Service Ring</th><th>Traffic</th><th>Completeness</th><th>Correctness</th></tr></thead>"
    )

    response += "<tbody>"
    for item in sdk_info_list:
        track1_str = ("GA" if item.track1_stable else "beta") if item.track1 else ""
        track2_str = ("GA" if item.track2_stable else "beta") if item.track2 else ""
        traffic_str = f"{item.traffic:,}" if item.traffic else ""
        response += (
            f"<tr><th>{item.sdk}</th><th>{track1_str}</th><th>{track2_str}</th>"
            f"<th>{xstr(item.track1_api_version)}</th><th>{xstr(item.track2_api_version)}</th>"
            f"<th>{xstr(item.ring)}</th><th>{traffic_str}</th><th>{xstr(xround(item.completeness, 2))}</th>"
            f"<th>{xstr(xround(item.correctness, 2))}</th></tr>"
        )
    response += "</tbody>"
    response += "</table>"

    response += "</body></html>"

    return response


def write_csv(sdk_info_list: List[SdkInfo]):
    logging.info(f"write csv: {CSV_FILENAME}")
    with open(CSV_FILENAME, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(["service", "track1", "track2", "track1 api", "track2 api"])
        for item in sdk_info_list:
            writer.writerow(item.to_row())


def aggregate_info(sdk_info_list: List[SdkInfo]) -> AggregatedInfo:
    known_track1_alias = [
        "cosmosdb",  # cosmos
        "datalake-analytics",
        "datalake-store",
        "dbformariadb",  # mariadb
        "documentdb",  # cosmos
        "eventhub",  # eventhubs
        "features",
        "graph-rbac",  # authentication
        "insights",  # applicationinsights
        "locks",
        "media",  # mediaservices
        "policy",
        "subscriptions",
        "website",  # appservice
    ]

    count_track1 = len(
        [item for item in sdk_info_list if item.track1 and (item.track1_api_version or item.track1_stable)]
    )
    count_track2 = len([item for item in sdk_info_list if item.track2])
    count_track1_but_no_track2 = len(
        [
            item
            for item in sdk_info_list
            if item.track1
            and (item.track1_api_version or item.track1_stable)
            and (not item.track2 and item.sdk not in known_track1_alias)
        ]
    )
    return AggregatedInfo(count_track1, count_track2, count_track1_but_no_track2)


def get_track2_version(package: str, version: str) -> str or None:
    if re.match(r"^2.\d{1,2}.\d{1,2}$", version):
        return "premium"

    group_url = "https://repo1.maven.org/maven2/com/azure/resourcemanager"
    pom_url = f"{group_url}/{package}/{version}/{package}-{version}.pom"

    logging.info(f"query pom: {pom_url}")
    pom_data = urlopen(pom_url).read()
    pom_str = pom_data.decode("utf-8")

    matched = re.search(r"Package tag (.+)\.<", pom_str, re.MULTILINE)
    tag = None
    if matched:
        tag = matched.group(1)
    else:
        matched = re.search(r"Package tag (.+)\. For ", pom_str, re.MULTILINE)
        if matched:
            tag = matched.group(1)
    if tag:
        version = tag.replace("package-", "").replace("-", "_").replace("_preview", "")

        # delete prefix before year
        if re.match(r".*_20\d{2}_\d{2}", version):
            loc = version.find("_20")
            version = version[loc + 1 :]

        if re.match(r"^\d{4}_\d{2}$", version):
            version = version + "_01"
        return version
    else:
        return None


def compare_version(current_ver: str, exist_ver: str) -> str:
    current_ver = current_ver.replace("_preview", "")

    if current_ver.startswith("v") and (not exist_ver or current_ver > exist_ver):
        return current_ver[1:]
    else:
        return exist_ver


def run():
    logging.basicConfig(level=logging.INFO)
    sdk_info_list = process_java_packages_csv()
    join_kpi_csv(sdk_info_list)
    print_stdout(sdk_info_list)
    write_csv(sdk_info_list)


if __name__ == "__main__":
    run()
