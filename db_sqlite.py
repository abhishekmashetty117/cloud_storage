import sqlite3
import datetime
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join('configuration','configuration.ini'))
DEFAULT_DB = config['DEFAULT']['database']

conn = sqlite3.connect(DEFAULT_DB)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
fullname TEXT NOT NULL,
username TEXT NOT NULL UNIQUE,
password TEXT NOT NULL UNIQUE,
email TEXT NOT NULL UNIQUE,
total_memory_allocated INTEGRER NOT NULL,
created_on TIMESTAMP NOT NULL)''')
conn.close()

conn = sqlite3.connect(DEFAULT_DB)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS data_sharing (
user_id INTEGER,
file TEXT NOT NULL,
unique_file_id TEXT NOT NULL,
sharing_allowed TEXT NOT NULL,
FOREIGN KEY(user_id) REFERENCES accounts(id))''')
conn.close()

conn = sqlite3.connect(DEFAULT_DB)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS reset_password (
user_id INTEGER,
token TEXT NOT NULL,
expiry TIMESTAMP NOT NULL,
FOREIGN KEY(user_id) REFERENCES accounts(id))''')
conn.close()

conn = sqlite3.connect(DEFAULT_DB)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS data_backup (
user_id INTEGER,
primary_disk TEXT NOT NULL,
secondary_disk TEXT NOT NULL,
memory_allocated INTEGER NOT NULL,
data_synced TEXT NOT NULL,
disk_status TEXT NOT NULL,
created_date TIMESTAMP NOT NULL,
modified_date TIMESTAMP NOT NULL,
FOREIGN KEY(user_id) REFERENCES accounts(id))''')
conn.close()

conn = sqlite3.connect(DEFAULT_DB)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS disk_metadata (
row_id INTEGER PRIMARY KEY AUTOINCREMENT,
disk_name TEXT NOT NULL UNIQUE,
disk_id TEXT NOT NULL UNIQUE,
disk_category TEXT NOT NULL,
disk_storage_category INTEGER NOT NULL,
physical_space INTEGER NOT NULL,
used_space INTEGER NOT NULL,
available_space INTEGER NOT NULL,
mirror_disk_name TEXT NOT NULL,
max_users INTEGER NOT NULL,
available_users INTEGET NOT NULL,
status TEXT NOT NULL,
installed_date TIMESTAMP NOT NULL)''')
conn.close()
GB = 1024*1024
conn = sqlite3.connect(DEFAULT_DB)
cursor = conn.cursor()
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'S1','a-w-s','P',1,?,?,?,'D1',?,?,'Active','Today')",(1000*GB,0,1000*GB,1000,1000))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'D1','f-w-s','S',1,?,?,?,'S1',?,?,'Active','Today')",(1000*GB,0,1000*GB,1000,1000))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'S2','b-w-s','P',2,?,?,?,'D2',?,?,'Active','Today')",(1000*GB,0,1000*GB,40,40))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'D2','g-w-s','S',2,?,?,?,'S2',?,?,'Active','Today')",(1000*GB,0,1000*GB,40,40))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'S3','c-w-s','P',3,?,?,?,'D3',?,?,'Active','Today')",(1000*GB,0,1000*GB,20,20))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'D3','h-w-s','S',3,?,?,?,'S3',?,?,'Active','Today')",(1000*GB,0,1000*GB,20,20))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'S4','d-w-s','P',4,?,?,?,'D4',?,?,'Active','Today')",(1000*GB,0,1000*GB,13,13))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'D4','i-w-s','S',4,?,?,?,'S4',?,?,'Active','Today')",(1000*GB,0,1000*GB,13,13))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'S5','e-w-s','P',5,?,?,?,'D5',?,?,'Active','Today')",(1000*GB,0,1000*GB,10,10))
cursor.execute("INSERT INTO disk_metadata VALUES(NULL,'D5','j-w-s','S',5,?,?,?,'S5',?,?,'Active','Today')",(1000*GB,0,1000*GB,10,10))
conn.commit()
conn.close()
               

