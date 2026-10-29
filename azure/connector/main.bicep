targetScope = 'resourceGroup'

@description('Existing Function App; its hosting, storage, and application settings are preserved.')
param functionAppName string
param office365ConnectionName string
param githubConnectionName string
param workflowName string
param location string = resourceGroup().location
@allowed(['probe', 'test', 'production'])
param mode string = 'test'
param enabled bool = false
param mailbox string
param folderName string
@description('Optional opaque folder ID for a folder nested deeper than Inbox.')
param folderId string = ''
param repository string
param allowedAuthor string
param listAddress string
@minValue(1)
@maxValue(3650)
param lookbackDays int = 90
@minValue(1)
@maxValue(1000)
param messageLimit int = 100
@secure()
param functionKey string
@secure()
param healthchecksPingUrl string = ''
@secure()
@description('Snapshot of existing Function settings, supplied privately by the deployment tool.')
param existingAppSettings object

resource processor 'Microsoft.Web/sites@2023-12-01' existing = {
  name: functionAppName
}
resource outlook 'Microsoft.Web/connections@2016-06-01' existing = {
  name: office365ConnectionName
}
resource github 'Microsoft.Web/connections@2016-06-01' existing = {
  name: githubConnectionName
}

// OAuth grants are stateful and must not be redeployed or exported into source.
// Only the publishing configuration is merged into the existing Function settings.
resource settings 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: processor
  name: 'appsettings'
  properties: union(existingAppSettings, {
    SDC_ALLOWED_AUTHOR: allowedAuthor
    SDC_LIST_ADDRESS: listAddress
    SDC_GITHUB_REPOSITORY: repository
  })
}

resource workflow 'Microsoft.Logic/workflows@2019-05-01' = {
  name: workflowName
  location: location
  tags: {
    purpose: 'SmartDrivingCars newsletter reconciliation'
    mode: mode
  }
  properties: {
    state: enabled ? 'Enabled' : 'Disabled'
    definition: shallowMerge([loadJsonContent('workflow.definition.json'), {
      triggers: mode == 'production' ? loadJsonContent('workflow.definition.json').triggers : {
        Poll: {
          type: 'Request'
          kind: 'Http'
          inputs: { schema: { type: 'object', additionalProperties: false } }
          runtimeConfiguration: { concurrency: { runs: 1 } }
        }
      }
    }])
    parameters: {
      '$connections': {
        value: {
          office365: {
            connectionId: outlook.id
            connectionName: office365ConnectionName
            id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'office365')
          }
          github: {
            connectionId: github.id
            connectionName: githubConnectionName
            id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'github')
          }
        }
      }
      processorUrl: { value: 'https://${functionAppName}.azurewebsites.net/api/prepare-connector-batch' }
      processorKey: { value: functionKey }
      mode: { value: mode }
      mailbox: { value: mailbox }
      folderName: { value: folderName }
      folderId: { value: folderId }
      repository: { value: repository }
      lookbackDays: { value: lookbackDays }
      messageLimit: { value: messageLimit }
      healthchecksPingUrl: { value: healthchecksPingUrl }
    }
  }
}

output workflowId string = workflow.id
output mode string = mode
output existingOffice365ConnectionId string = outlook.id
output existingGitHubConnectionId string = github.id
