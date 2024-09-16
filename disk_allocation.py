import sqlite3
import random
import datetime
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join('configuration','configuration.ini'))
DEFAULT_DB = config['DEFAULT']['database']
datetime_format = config['DATA']['datetime_format']

def new_disk_replace_old():
	f = open('DISK_FAILURE.txt','r')
	for line in f.readlines():
		failed_disk = line.split(";")[1]

	conn = sqlite3.connect(DEFAULT_DB)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM disk_metadata WHERE disk_name=? and status=?',(failed_disk,'Active'))
	result = cursor.fetchone()

	column = {cursor.description[i][0]:i for i in range(len(cursor.description))}
	mirror_disk_name = result[column['mirror_disk_name']]

	NEW_DISC_CATEGORY =result[column['disk_category']]
	NEW_DISK = 'F'
	NEW_DISK_CODE = 'a-w-s'
	NEW_DISK_STORAGE_CATEGORY = 1
	cursor.execute('INSERT INTO disk_metadata VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(NEW_DISK,NEW_DISK_CODE,NEW_DISC_CATEGORY,NEW_DISK_STORAGE_CATEGORY,100*1024*1024,0,100*1024*1024,mirror_disk_name,'Active',datetime.datetime.now().strftime(datetime_format)))
	cursor.execute('UPDATE disk_metadata SET status = ? WHERE disk_name = ?',("Fault", failed_disk))
	cursor.execute('UPDATE disk_metadata SET mirror_disk_name = ? WHERE disk_name = ?',(NEW_DISK, mirror_disk_name))
	conn.commit()

	if result[column['disk_category']] == 'P':
		cursor.execute('UPDATE data_backup SET primary_disk = ?, data_synced = ? WHERE primary_disk = ?',(NEW_DISK, "False", failed_disk))
	elif result[column['disk_category']] == 'S':
		cursor.execute('UPDATE data_backup SET secondary_disk = ?, data_synced = ? WHERE secondary_disk = ?',(NEW_DISK, "False", failed_disk))
	conn.commit()
	conn.close()

##memory_requirement = 1000*1024*1024*1024
def allocate_disk_to_user(memory_requirement,disk_storage_category):
	conn = sqlite3.connect(DEFAULT_DB)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM disk_metadata WHERE disk_category= ? and status= ? and disk_storage_category = ? and available_users > ?",('P','Active',disk_storage_category, 0))
	result = cursor.fetchall()
	conn.close()

	column = {cursor.description[i][0]:i for i in range(len(cursor.description))}
	potential_disks = list()
	for row in result:
		if (row[column['available_space']] > int(memory_requirement)):
			potential_disks.append(row[column['disk_name']])
	else:
		if len(potential_disks) > 0:
			print(potential_disks)
			PRIMARY_DISK = random.choice(potential_disks)

			for row in result:
				if (row[column['disk_name']] == PRIMARY_DISK):
					SECONDARY_DISK = row[column['mirror_disk_name']]
					break
			print(PRIMARY_DISK,SECONDARY_DISK)
			return PRIMARY_DISK,SECONDARY_DISK
		else:
			print("Memory Not Available")

def updating_disk(disk_name,disk_category):
    conn = sqlite3.connect(DEFAULT_DB)
    cursor = conn.cursor()
    
    if disk_category == 'P':
        cursor.execute('update disk_metadata SET used_space = t.used_space_r FROM (select sum(db.memory_allocated) as used_space_r from data_backup db where db.primary_disk = ?) t where disk_metadata.disk_name = ?',(disk_name,disk_name))
        conn.commit()

    elif disk_category == 'S':
        cursor.execute('update disk_metadata SET used_space = t.used_space_r FROM (select sum(db.memory_allocated) as used_space_r from data_backup db where db.secondary_disk = ?) t where disk_metadata.disk_name = ?',(disk_name,disk_name))
        conn.commit()
            
    cursor.execute('update disk_metadata SET available_space = physical_space-used_space where disk_metadata.disk_name = ?',(disk_name,))
    conn.commit()
    conn.close()

##This below function will be called from regisrtation route
#updating_disk(disk_name,'P')
#updating_disk(mirror_disk_name,'S')

def updating_available_users(disk_name,operation):
    conn = sqlite3.connect(DEFAULT_DB)
    cursor = conn.cursor()    
    if operation == 'ADD_USER':
        cursor.execute('update disk_metadata SET available_users = available_users - 1 where disk_metadata.disk_name = ?',(disk_name,))
        conn.commit()
    elif operation == 'REMOVE_USER':
        cursor.execute('update disk_metadata SET available_users = available_users + 1 where disk_metadata.disk_name = ?',(disk_name,))
        conn.commit()
    conn.close()


##This below function will be called from regisrtation route, add_storage route, delete_storage route
#updating_available_users(disk_name,'ADD_USER')
#updating_available_users(mirror_disk_name,'REMOVE_USER')
