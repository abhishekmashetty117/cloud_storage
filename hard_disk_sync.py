from dirsync import sync
import sqlite3, os
import time
from time import sleep
import configparser
x = time.time()

config = configparser.ConfigParser()
config.read(os.path.join('configuration','configuration.ini'))
DEFAULT_DB = config['DEFAULT']['database']

def user_level_backup(user_id = ''):
    conn =  sqlite3.connect(DEFAULT_DB)
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT db.user_id, a.username, db.primary_disk, db.secondary_disk FROM data_backup db JOIN accounts a on db.user_id = a.id WHERE db.data_synced=? and db.disk_status = ? and db.user_id = ?",('False','Active',user_id))
    else:
        cursor.execute("SELECT db.user_id, a.username, db.primary_disk, db.secondary_disk FROM data_backup db JOIN accounts a on db.user_id = a.id WHERE db.data_synced=? and db.disk_status = ?",('False','Active',))
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        source = os.path.join(row[2],row[1])
        backup = os.path.join(row[3],row[1])
        sync(source,backup,'sync',purge=True)
        cursor.execute('UPDATE data_backup SET data_synced = ? WHERE user_id = ? and disk_status = ?',("True", row[0], 'Active'))
        conn.commit()
    conn.close()

def change_storage_backup(old_primary_disk, new_primary_disk, username, user_id):
    conn =  sqlite3.connect(DEFAULT_DB)
    cursor = conn.cursor()
    source = os.path.join(old_primary_disk,username)
    backup = os.path.join(new_primary_disk,username)
    sync(source,backup,'sync',purge=True)
    cursor.execute('UPDATE data_backup SET data_synced = ? WHERE user_id = ? and disk_status = ?',("True", user_id, 'Waiting'))
    conn.commit()
    conn.close()
    
## This is for disk_failure andhence backup after new_disk
def disk_level_backup(DISK_CATEGORY, DISK_NAME):
    conn =  sqlite3.connect(DEFAULT_DB)
    cursor = conn.cursor()
    if DISK_CATEGORY == 'P':
        cursor.execute("SELECT db.user_id, a.username, db.primary_disk, db.secondary_disk FROM data_backup db JOIN accounts a on db.user_id=a.id WHERE db.primary_disk=?",(DISK_NAME,))
    elif DISK_CATEGORY == 'S':
        cursor.execute("SELECT db.user_id, a.username, db.primary_disk, db.secondary_disk FROM data_backup db JOIN accounts a on db.user_id=a.id WHERE db.secondary_disk=?",(DISK_NAME,))
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        source = os.path.join(row[2],row[1])
        if not os.path.exists(source):
            os.makedirs(source)
        backup = os.path.join(row[3],row[1])
        if not os.path.exists(backup):
            os.makedirs(backup)
        if DISK_CATEGORY == 'P':
            sync(backup,source,'sync',purge=True)
        elif DISK_CATEGORY == 'S':
            sync(source,backup,'sync',purge=True)
        cursor.execute('UPDATE data_backup SET data_synced = ? WHERE user_id = ?',("True", row[0]))
        conn.commit()
    conn.close()
