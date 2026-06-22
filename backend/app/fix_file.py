import re

with open('admin_page.py', 'r') as f:
    content = f.read()

# 1. Remove duplicate viewDetail functions (keep the first complete one)
print("=== Removing duplicate viewDetail functions ===")
vd_pattern = r'async function viewDetail\(id\)\{'
vd_positions = [m.start() for m in re.finditer(vd_pattern, content)]
print("Found at:", vd_positions)

if len(vd_positions) > 1:
    # Remove from 2nd occurrence onwards
    start_2 = vd_positions[1]
    # Find end of 2nd function
    end_2 = content.find('\nasync function openConcMod', start_2)
    if end_2 == -1:
        end_2 = content.find('\nlet logPg', start_2)
    if end_2 == -1:
        end_2 = len(content)
    
    print("  Removing 2nd viewDetail:", start_2, "to", end_2)
    content = content[:start_2] + content[end_2:]
    
    # Find and remove 3rd if still exists
    vd_positions_new = [m.start() for m in re.finditer(vd_pattern, content)]
    if len(vd_positions_new) > 1:
        start_3 = vd_positions_new[1]
        end_3 = content.find('\nasync function openConcMod', start_3)
        if end_3 == -1:
            end_3 = content.find('\nlet logPg', start_3)
        if end_3 == -1:
            end_3 = len(content)
        print("  Removing 3rd viewDetail:", start_3, "to", end_3)
        content = content[:start_3] + content[end_3:]

# 2. Remove duplicate detailMod modals (keep the first one)
print("\n=== Removing duplicate detailMod modals ===")
dm_pattern = r'<div class="mo" id="detailMod">'
dm_positions = [m.start() for m in re.finditer(dm_pattern, content)]
print("Found at:", dm_positions)

if len(dm_positions) > 1:
    for i in range(1, len(dm_positions)):
        start = dm_positions[i]
        end = content.find('\n<!-- 并发设置', start)
        if end == -1:
            end = content.find('\n<div class="mo" id="concMod"', start)
        if end == -1:
            end = content.find('\n\n\n<!-- Excel', start)
        if end == -1:
            end = len(content)
        
        print("  Removing detailMod #" + str(i+1) + ":", start, "to", end)
        content = content[:start] + content[end:]

with open('admin_page.py', 'w') as f:
    f.write(content)

# Final verification
with open('admin_page.py', 'r') as f:
    content = f.read()

print("\n=== Final counts ===")
print("viewDetail:", content.count('async function viewDetail'))
detailmod_count = content.count('detailMod')
print("detailMod references:", detailmod_count)
