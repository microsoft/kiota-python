Param(
     [Parameter(Mandatory=$true, Position=0, HelpMessage="Command to execute")]
     [string]$command
   )

$rootPath = Get-Location
$projectsInfo = Get-Content -Raw -Encoding UTF-8 ".\projects-config.json" | ConvertFrom-Json
$availableCommands = $projectsInfo | Select-Object -ExpandProperty commands

$commandFound = $false
$availableCommands | ForEach-Object {
    if ($($_.name) -eq $command) {
        $commandFound = $true
        $selectedCommand = $($_.command)
    }
}

if (-not $commandFound) {
    Write-Host "Command '$command' not found in the available commands" -ForegroundColor Red
    $availableCommands | ForEach-Object {
        Write-Host "Command : '$($_.name)'"
        Write-Host "Description : '$($_.description)'"
        Write-Host "---------------------------------------------"
    }
    exit
}

Write-Host "Executing '$selectedCommand' for all projects in '$rootPath' " -ForegroundColor Green

foreach ($project in $projectsInfo.projects) {
    $projectName = $project.name
    $projectName = $project.packageName
    $projectPath = Join-Path -Path $rootPath -ChildPath $project.path
    $commandToRun = $selectedCommand.Replace("{projectName}", $projectName)
    Write-Host "Executing '$commandToRun' for '$projectName' " -ForegroundColor Blue
    Set-Location -Path $projectPath

    Invoke-Expression -Command $commandToRun
    Set-Location -Path $rootPath
    Write-Host "Finished executing '$commandToRun' for '$projectName'" -ForegroundColor Blue
    Write-Host "---------------------------------------------" -ForegroundColor Blue
}
