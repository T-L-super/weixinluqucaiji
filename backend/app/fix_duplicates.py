import re

with open('admin_page.py', 'r') as f:
    content = f.read()

# 1. Fix viewDetail - keep only the first one (the most complete version)
vd_pattern = r'async function viewDetail\(id\)\{'
vd_matches = list(re.finditer(vd_pattern, content))
print(f"Found {len(vd_matches)} viewDetail functions")

if len(vd_matches) > 1:
    # Remove from the 2nd to the end
    start_remove = vd_matches[1].start()
    # Find where the 2nd function ends - look for the next function definition
    next_func = re.search(r'\nasync function |\nfunction loadUsers|\nfunction openAddUser|\nlet logPg|\n/\* ===== REVIEW', content[start_remove + 10:])
    if next_func:
        end_remove = start_remove + 10 + next_func.start()
    else:
        end_remove = len(content)
    
    print(f"  Removing from position {start_remove} to {end_remove}")
    content = content[:start_remove] + content[end_remove:]
    print("  Removed duplicate viewDetail functions")

# 2. Fix detailMod - keep only the first one
dm_pattern = r'<div class="mo" id="detailMod">'
dm_matches = list(re.finditer(dm_pattern, content))
print(f"Found {len(dm_matches)} detailMod modals")

if len(dm_matches) > 1:
    # Remove from the 2nd to the end
    start_remove = dm_matches[1].start()
    # Find where the 2nd modal ends
    next_modal = re.search(r'\n<div class="mo" id="concMod"|\n<!-- 并发设置|\n\n\n<!-- 并发', content[start_remove + 10:])
    if next_modal:
        end_remove = start_remove + 10 + next_modal.start()
    else:
        end_remove = len(content)
    
    print(f"  Removing from position {start_remove} to {end_remove}")
    content = content[:start_remove] + content[end_remove:]
    print("  Removed duplicate detailMod modals")

with open('admin_page.py', 'w') as f:
    f.write(content)

# Verify
with open('admin_page.py', 'r') as f:
    content = f.read()

vd_count = content.count('async function viewDetail')
dm_count = content.count('id="detailMod"')
print(f"\nVerification:")
print(f"  viewDetail: {vd_count}")
print(f"  detailMod: {dm_count}")
