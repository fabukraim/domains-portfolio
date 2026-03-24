$path = "c:\Users\Admin\Desktop\domanid.com"
$files = Get-ChildItem -Path $path -Recurse -Filter *.html
$meta_tag = '<meta name="google-adsense-account" content="ca-pub-3988572626513727">'

foreach($file in $files) {
    if ($file.Name -eq "article_template.html") { continue }
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $updated = $false
    
    if($content -notmatch 'google-adsense-account' -and $content -match '</head>') {
        $content = $content -replace '</head>', "    $meta_tag`r`n</head>"
        $updated = $true
    }
    
    if($updated) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8
        Write-Host "Updated: $($file.Name)" -ForegroundColor Green
    }
}
Write-Host "Meta tag added successfully!" -ForegroundColor Cyan
