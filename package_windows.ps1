$dir = "plugin.video.maltracker"
$zip = "plugin.video.maltracker.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path $dir -DestinationPath $zip
Write-Host "Addon empaquetado en $zip"
