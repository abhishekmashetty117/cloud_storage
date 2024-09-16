import sqlite3
import datetime
import subprocess
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join('configuration','configuration.ini'))
DEFAULT_DB = config['DEFAULT']['database']

config.read('new_disk.ini')
disk_name = config['DISK']['disk_name']
mirror_disk_name = config['DISK']['mirror_disk_name']
disk_category = config['DEFAULT']['disk_category']
mirror_disk_category = config['DEFAULT']['mirror_disk_category']
datetime_format = config['DATA']['datetime_format']

def attaching_new_disk(disk_name,disk_category,mirror_disk_name):
    disk_info = subprocess.Popen(['diskutil','info',disk_name],stdout=subprocess.PIPE)
    disk_info_ = str(disk_info.communicate())
    disk_info_ = disk_info_.replace("(b'",'')

    p = [list(map(str.strip,x.split(":"))) for x in disk_info_.split('\\n')]
    disk_info = dict()
    for x in disk_info_.split("\\n"):
        if x != '' and 'None' not in x:
            disk_info[x.split(":")[0].strip(' ')] = x.split(":")[1].strip(' ')

    disk_name = disk_info['Volume Name']
    disk_id = disk_info['Device Identifier']
    p_space = int(disk_info['Volume Total Space'].split(" (")[1].replace(' Bytes)',''))
    u_space = 0
    a_space = p_space - u_space
    status = 'Active'
    max_users = 1000
    available_users = 1000
    disk_storage_category = 1
    conn = sqlite3.connect(DEFAULT_DB)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO disk_metadata VALUES (NULL, ?,?,?,?,?,?,?,?,?,?,?,?)',(disk_name,disk_id,disk_category,disk_storage_category,p_space,u_space,a_space,mirror_disk_name,max_users,available_users,status,datetime.datetime.now().strftime(datetime_format)))
    conn.commit()
    conn.close()
    
#attaching_new_disk(disk_name,disk_category,mirror_disk_name)
#attaching_new_disk(mirror_disk_name,mirror_disk_category,disk_name)
