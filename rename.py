import os, glob

files = glob.glob('**/*.html', recursive=True) + glob.glob('**/*.js', recursive=True)
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = content.replace('DomainID', 'DomanID')
    new_content = new_content.replace('Domain<span', 'Doman<span')
    new_content = new_content.replace('Domain ID', 'Doman ID')
    
    if content != new_content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated {f}")
