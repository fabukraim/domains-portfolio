import os
import glob

html_files = glob.glob('c:/Users/Admin/Desktop/domanid.com/**/*.html', recursive=True)

adsense_script = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3988572626513727" crossorigin="anonymous"></script>'

count = 0
for file in html_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated = False
        
        # 1. Replace placeholder if it exists
        if 'ca-pub-XXXXXXXXXXXXXXXX' in content:
            content = content.replace('ca-pub-XXXXXXXXXXXXXXXX', 'ca-pub-3988572626513727')
            updated = True
        
        # 2. If adsbygoogle.js is still not in the file, inject it before </head>
        if 'adsbygoogle.js' not in content and '</head>' in content:
            # properly indent it
            content = content.replace('</head>', f'    {adsense_script}\n</head>')
            updated = True
            
        if updated:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file}")
            count += 1
            
    except Exception as e:
        print(f"Error processing {file}: {e}")

print(f"\nSuccessfully updated {count} HTML files.")
