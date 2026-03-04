with open('templates/schools/admin_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(open('write_dashboard_content.html', 'r', encoding='utf-8').read())
print("Done! File written.")