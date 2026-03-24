$path = "c:\Users\Admin\Desktop\domanid.com"
$files = Get-ChildItem -Path $path -Recurse -Filter *.html
$adsense = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3988572626513727" crossorigin="anonymous"></script>'

foreach($file in $files) {
    # Skip template file just in case
    if ($file.Name -eq "article_template.html") { continue }
    
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $updated = $false
    
    if($content -match 'ca-pub-XXXXXXXXXXXXXXXX') {
        $content = $content -replace 'ca-pub-XXXXXXXXXXXXXXXX', 'ca-pub-3988572626513727'
        $updated = $true
    }
    
    if($content -notmatch 'adsbygoogle\.js' -and $content -match '</head>') {
        $content = $content -replace '</head>', "    $adsense`n</head>"
        $updated = $true
    }
    
    if($updated) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8
        Write-Host "Updated: $($file.Name)" -ForegroundColor Green
    }
}
Write-Host "تم تحديث جميع الملفات بنجاح!" -ForegroundColor Cyan
