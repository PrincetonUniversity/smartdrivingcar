# Run in PowerShell 7 with ExchangeOnlineManagement and an Exchange administrator session.
# -WhatIf previews changes. No Mail.Send or Mail.ReadWrite permission is assigned.
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][guid]$ClientId,
    [Parameter(Mandatory)][guid]$EnterpriseObjectId,
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+$')][string]$Mailbox,
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+$')][string]$OtherMailbox
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($Mailbox -eq $OtherMailbox) { throw 'The negative control mailbox must be different' }
$scopeName = "SDC-MailRead-$ClientId"
$assignmentName = "SDC-Publisher-$ClientId"
$filter = "PrimarySmtpAddress -eq '$Mailbox'"
$principal = Get-ServicePrincipal | Where-Object { $_.AppId -eq $ClientId }
if (-not $principal -and $PSCmdlet.ShouldProcess('Exchange service principal', 'Create')) {
    New-ServicePrincipal -AppId $ClientId -ObjectId $EnterpriseObjectId -DisplayName "SDC Publisher $ClientId" | Out-Null
}
$scope = Get-ManagementScope | Where-Object { $_.Name -eq $scopeName }
if ($scope -and $scope.RecipientFilter -ne "(PrimarySmtpAddress -eq '$Mailbox')" -and $scope.RecipientFilter -ne $filter) {
    throw 'Existing scope differs. Inspect it manually before proceeding.'
}
if (-not $scope -and $PSCmdlet.ShouldProcess('Single mailbox scope', 'Create')) {
    New-ManagementScope -Name $scopeName -RecipientRestrictionFilter $filter | Out-Null
}
$assignment = Get-ManagementRoleAssignment | Where-Object { $_.Name -eq $assignmentName }
if (-not $assignment -and $PSCmdlet.ShouldProcess('Application Mail.Read in single mailbox scope', 'Assign')) {
    New-ManagementRoleAssignment -Name $assignmentName -Role 'Application Mail.Read' -App $EnterpriseObjectId -CustomResourceScope $scopeName | Out-Null
}
if (-not $WhatIfPreference) {
    $allowed = @(Test-ServicePrincipalAuthorization -Identity $EnterpriseObjectId -Resource $Mailbox)
    $denied = @(Test-ServicePrincipalAuthorization -Identity $EnterpriseObjectId -Resource $OtherMailbox)
    if (-not ($allowed | Where-Object { $_.RoleName -eq 'Application Mail.Read' -and $_.InScope })) {
        throw 'Positive authorization check failed'
    }
    if ($denied | Where-Object { $_.InScope }) { throw 'Negative authorization check failed' }
    Write-Output 'PASS: Exchange RBAC allows target mailbox and excludes negative control.'
    Write-Output 'Also verify live Graph denial and absence of tenant-wide Entra Mail grants before enabling.'
} else {
    Write-Output 'PASS: mailbox permission dry run complete; no changes applied.'
}
