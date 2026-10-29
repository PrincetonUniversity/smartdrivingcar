// Recovery/greenfield foundation only. The normal main.bicep adoption path does
// not redeploy these resources or replace their existing OAuth authorization.
targetScope = 'resourceGroup'
param location string = 'canadacentral'
param storageAccountName string
param hostingPlanName string = 'CanadaCentralLinuxDynamicPlan'
param functionAppName string
param insightsName string
param workspaceName string
param office365ConnectionName string
param githubConnectionName string

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}
resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: hostingPlanName
  location: location
  kind: 'linux'
  sku: { name: 'Y1', tier: 'Dynamic' }
  properties: { reserved: true }
}
resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  properties: { retentionInDays: 30, sku: { name: 'PerGB2018' } }
}
resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: insightsName
  location: location
  kind: 'web'
  properties: { Application_Type: 'web', WorkspaceResourceId: workspace.id }
}
resource processor 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      appSettings: [
        { name: 'AzureWebJobsStorage', value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${storage.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}' }
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'python' }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'SCM_DO_BUILD_DURING_DEPLOYMENT', value: 'true' }
        { name: 'ENABLE_ORYX_BUILD', value: 'true' }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: insights.properties.ConnectionString }
      ]
    }
  }
}
resource outlook 'Microsoft.Web/connections@2016-06-01' = {
  name: office365ConnectionName
  location: location
  properties: {
    displayName: 'SmartDrivingCar O365 Newsletter'
    api: { id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'office365') }
  }
}
resource github 'Microsoft.Web/connections@2016-06-01' = {
  name: githubConnectionName
  location: location
  properties: {
    displayName: 'SmartDrivingCar GitHub'
    api: { id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'github') }
  }
}
output functionAppId string = processor.id
output outlookConnectionId string = outlook.id
output githubConnectionId string = github.id
