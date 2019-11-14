import re

CLASS_OUTPUT = r'''
Code	File	Line	Column	Project
public partial class WebSiteManagementClient : FluentServiceClientBase<WebSiteManagementClient>, IWebSiteManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\AppService\Generated\WebSiteManagementClient.cs	28	26	Microsoft.Azure.Management.AppService.Fluent (net452)
public partial class BatchManagementClient : FluentServiceClientBase<BatchManagementClient>, IBatchManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Batch\Generated\BatchManagementClient.cs	23	26	Microsoft.Azure.Management.Batch.Fluent (net452)
public partial class BatchAIManagementClient : FluentServiceClientBase<BatchAIManagementClient>, IBatchAIManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\BatchAI\Generated\BatchAIManagementClient.cs	26	26	Microsoft.Azure.Management.BatchAI.Fluent (net452)
public partial class CdnManagementClient : FluentServiceClientBase<CdnManagementClient>, ICdnManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Cdn\Generated\CdnManagementClient.cs	30	26	Microsoft.Azure.Management.Cdn.Fluent (net452)
public partial class ComputeManagementClient : FluentServiceClientBase<ComputeManagementClient>, IComputeManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Compute\Generated\ComputeManagementClient.cs	27	26	Microsoft.Azure.Management.Compute.Fluent (net452)
public partial class ContainerInstanceManagementClient : FluentServiceClientBase<ContainerInstanceManagementClient>, IContainerInstanceManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\ContainerInstance\Generated\ContainerInstanceManagementClient.cs	23	26	Microsoft.Azure.Management.ContainerInstance.Fluent (net452)
public partial class ContainerRegistryManagementClient : FluentServiceClientBase<ContainerRegistryManagementClient>, IContainerRegistryManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\ContainerRegistry\Generated\ContainerRegistryManagementClient.cs	23	26	Microsoft.Azure.Management.ContainerRegistry.Fluent (net452)
public partial class ContainerServiceManagementClient : FluentServiceClientBase<ContainerServiceManagementClient>, IContainerServiceManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\ContainerService\Generated\ContainerServiceManagementClient.cs	26	26	Microsoft.Azure.Management.ContainerService.Fluent (net452)
public partial class CosmosDB : FluentServiceClientBase<CosmosDB>, ICosmosDB, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\CosmosDB\Generated\CosmosDB.cs	26	26	Microsoft.Azure.Management.CosmosDB.Fluent (net452)
public partial class DnsManagementClient : FluentServiceClientBase<DnsManagementClient>, IDnsManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Dns\Generated\DnsManagementClient.cs	26	26	Microsoft.Azure.Management.Dns.Fluent (net452)
public partial class EventHubManagementClient : FluentServiceClientBase<EventHubManagementClient>, IEventHubManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\EventHub\Generated\EventHubManagementClient.cs	26	26	Microsoft.Azure.Management.EventHub.Fluent (net452)
public partial class AuthorizationManagementClient : FluentServiceClientBase<AuthorizationManagementClient>, IAuthorizationManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Graph.RBAC\Generated\AuthorizationManagementClient.cs	31	26	Microsoft.Azure.Management.Graph.RBAC.Fluent (net452)
public partial class GraphRbacManagementClient : FluentServiceClientBase<GraphRbacManagementClient>, IGraphRbacManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Graph.RBAC\Generated\GraphRbacManagementClient.cs	26	26	Microsoft.Azure.Management.Graph.RBAC.Fluent (net452)
public partial class KeyVaultManagementClient : FluentServiceClientBase<KeyVaultManagementClient>, IKeyVaultManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\KeyVault\Generated\KeyVaultManagementClient.cs	27	26	Microsoft.Azure.Management.KeyVault.Fluent (net452)
internal class KeyVaultClientInternal : KeyVaultClient	D:\github\azure-libraries-for-net\src\ResourceManagement\KeyVault\KeyVaultClientInternal.cs	16	20	Microsoft.Azure.Management.KeyVault.Fluent (net452)
public partial class ManagementLockClient : FluentServiceClientBase<ManagementLockClient>, IManagementLockClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Locks\Generated\ManagementLockClient.cs	27	26	Microsoft.Azure.Management.Locks.Fluent (net452)
public partial class MonitorManagementClient : FluentServiceClientBase<MonitorManagementClient>, IMonitorManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Monitor\Generated\MonitorManagementClient.cs	26	26	Microsoft.Azure.Management.Monitor.Fluent (netstandard1.4)
public partial class ManagedServiceIdentityClient : FluentServiceClientBase<ManagedServiceIdentityClient>, IManagedServiceIdentityClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Msi\Generated\ManagedServiceIdentityClient.cs	26	26	Microsoft.Azure.Management.Msi.Fluent (net452)
public partial class NetworkManagementClient : FluentServiceClientBase<NetworkManagementClient>, INetworkManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Network\Generated\NetworkManagementClient.cs	28	26	Microsoft.Azure.Management.Network.Fluent (net452)
public partial class RedisManagementClient : FluentServiceClientBase<RedisManagementClient>, IRedisManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\RedisCache\Generated\RedisManagementClient.cs	26	26	Microsoft.Azure.Management.Redis.Fluent (net452)
public partial class FeatureClient : FluentServiceClientBase<FeatureClient>, IFeatureClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\ResourceManager\Generated\FeatureClient.cs	31	26	Microsoft.Azure.Management.ResourceManager.Fluent (net452)
public partial class ResourceManagementClient : FluentServiceClientBase<ResourceManagementClient>, IResourceManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\ResourceManager\Generated\ResourceManagementClient.cs	26	26	Microsoft.Azure.Management.ResourceManager.Fluent (net452)
public partial class SubscriptionClient : FluentServiceClientBase<SubscriptionClient>, ISubscriptionClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\ResourceManager\Generated\SubscriptionClient.cs	29	26	Microsoft.Azure.Management.ResourceManager.Fluent (net452)
public partial class SearchManagementClient : FluentServiceClientBase<SearchManagementClient>, ISearchManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Search\Generated\SearchManagementClient.cs	29	26	Microsoft.Azure.Management.Search.Fluent (net452)
public partial class ServiceBusManagementClient : FluentServiceClientBase<ServiceBusManagementClient>, IServiceBusManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\ServiceBus\Generated\ServiceBusManagementClient.cs	28	26	Microsoft.Azure.Management.ServiceBus.Fluent (netstandard1.4)
public partial class SqlManagementClient : FluentServiceClientBase<SqlManagementClient>, ISqlManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Sql\Generated\SqlManagementClient.cs	29	26	Microsoft.Azure.Management.Sql.Fluent (net452)
public partial class StorageManagementClient : FluentServiceClientBase<StorageManagementClient>, IStorageManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\Storage\Generated\StorageManagementClient.cs	26	26	Microsoft.Azure.Management.Storage.Fluent (net452)
public partial class TrafficManagerManagementClient : FluentServiceClientBase<TrafficManagerManagementClient>, ITrafficManagerManagementClient, IAzureClient	D:\github\azure-libraries-for-net\src\ResourceManagement\TrafficManager\Generated\TrafficManagerManagementClient.cs	26	26	Microsoft.Azure.Management.TrafficManager.Fluent (net452)
'''

TEMPLATE = r'''else if (client is {class_name})
{{
    Assert.Equal(new Uri(environment.ResourceManagerEndpoint).Host, (client as {class_name}).BaseUri.Host);
}}'''

CLASS_NAME_IGNORE = [
    'AuthorizationManagementClient',
    'GraphRbacManagementClient',
    'ManagedServiceIdentityClient',
    'SubscriptionClient'
]

CLASS_NAME_MAP = {
    'WebSiteManagementClient': 'AppService',
    'ManagementLockClient': 'Locks',
    'FeatureClient': 'ResourceManager',
    'ResourceManagementClient': 'ResourceManager'
}


class_name_regex = re.compile(r'.*class (?P<class_name>[a-zA-z]+) : FluentServiceClientBase.*')
class_names = []
for line in CLASS_OUTPUT.splitlines():
    if 'FluentServiceClientBase' in line:
        class_names.append(class_name_regex.findall(line))
print('Classes: ' + str(class_names) + '\n')

for class_name in class_names:
    if class_name in CLASS_NAME_IGNORE:
        continue
    elif class_name in CLASS_NAME_MAP:
        full_class_name = 'Microsoft.Azure.Management.' + CLASS_NAME_MAP[class_name] + '.Fluent.' + class_name
    elif 'ManagementClient' in class_name:
        full_class_name = 'Microsoft.Azure.Management.' + class_name.replace('ManagementClient', '') + '.Fluent.' + class_name
    else:
        full_class_name = 'Microsoft.Azure.Management.' + class_name + '.Fluent.' + class_name
    print(TEMPLATE.format(class_name=full_class_name))
