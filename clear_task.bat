@echo off
cd /d d:\大学录取信息整理系统\backend
python -c "import sqlite3; conn = sqlite3.connect('data/admission_system.db'); c = conn.cursor(); c.execute('DELETE FROM admission_records_staging WHERE article_url LIKE ?', ('%%Z10iL5ZpGpEEPs_YZEABpg%%',)); c.execute('DELETE FROM collection_tasks WHERE article_url LIKE ?', ('%%Z10iL5ZpGpEEPs_YZEABpg%%',)); conn.commit(); print(f'Deleted staging: {c.rowcount}'); conn.close(); print('Done')"
pause
