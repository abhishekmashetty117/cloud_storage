from flask import Flask, abort, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from fileinput import filename
import sqlite3, os, uuid, hashlib, re, datetime, time, json, shutil
from collections import defaultdict
import disk_allocation as DA
import configparser
import mail_delivery as MD_M
import hard_disk_sync as HDS
import payment_methods

config = configparser.ConfigParser()
config.read(os.path.join('configuration','configuration.ini'))
config.read(os.path.join('configuration','mail.ini'))

app = Flask(__name__)
app.secret_key = 'dev'
app.config['MAX_CONTENT_LENGHT'] = 10 * 1024 * 1024

DEFAULT_DB = config['DEFAULT']['database']
DEFAULT_DATETIME_FORMAT = config['DATA']['datetime_format']
DEFAULT_DATETIME_FORMAT_2 = config['DATA']['datetime_format_2']
DEAFULT_MEMORY_ALLOCATION = config['DEFAULT']['default_memory_allocation']
DEFAULT_LINK_ACCESS = config['DEFAULT']['default_link_access']
DOMAIN_PREFIX = config['DEFAULT']['domain_prefix']
DEFAULT_IMAGES = ['jpeg','jpg','png']
DEFAULT_FILES = ['py','db']
DEFAULT_BACKUP_SUFFIX = '_backup'
DEFAULT_TEMP_STORAGE = config['DEFAULT']['default_temp_storage']

@app.errorhandler(405)
def page_not_found(e):
    # note that we set the 404 status explicitly
    # Create a html file and render_template
    return {'code':405,'data':'method not allowed'}, 405

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    # Create a html file and render_template
    return {'code':500,'data':'nice try'}, 500    

def disk_failure_logging(message):
    disk_failure = open("DISK_FAILURE.txt",'a')
    logg = "%s;%s;\n"%(datetime.datetime.now().strftime(DEFAULT_DATETIME_FORMAT),message)
    disk_failure.write(logg)
    disk_failure.close()

def user_default_path():
    primary_disk, secondary_disk = user_data_backup(None,None,'SELECT')
    primary_folder = os.path.join(primary_disk,session['username'])
    secondary_folder = os.path.join(secondary_disk,session['username'])
    if os.path.exists(primary_folder):
        session['c_working_path'] = primary_folder
        return primary_folder
    elif os.path.exists(secondary_folder):
        disk_failure_logging(primary_disk)
        session['c_working_path'] = secondary_folder
        return secondary_folder
    else:
        disk_failure_logging(secondary_disk)
        if not os.path.exists(os.path.join(DEFAULT_TEMP_STORAGE,session['username'])):
            os.makedirs(os.path.join(DEFAULT_TEMP_STORAGE,session['username']))
        session['c_working_path'] = os.path.join(DEFAULT_TEMP_STORAGE,session['username'])
        return os.path.join(DEFAULT_TEMP_STORAGE,session['username'])

@app.route('/home', methods  = ['GET'])
def home():
    if request.method == 'GET' and session.get('loggedin'):
        user_directory = user_default_path()  ## This Function Invocation is mandatory to set c_working_path variable in session
        user_contents = folder_content(session['c_working_path'])
        return render_template("home.html", user_contents = user_contents, user_information = session)
    else:
        return redirect(url_for('login'))

app.route('/payment_test', methods  = ['GET'])(payment_methods.payment_test)

def folder_content(directory):
    user_contents = defaultdict(dict)
    with os.scandir(directory) as it:
        for e in it:
            if "DS_Store" in e.name:  ## This is mandatory to exclude .DS_Store files created in mac in each folder
                continue
            if "trash_come_recover" in e.name: ## This is mandatory to exclude trash folder for each user
                folder_path = e.path.removeprefix(session['c_working_path'])
                print('folder_path',folder_path,e.name)
                user_contents[folder_path]['size'] = get_dir_size(e)
                user_contents[folder_path]['created'] = datetime.datetime.fromtimestamp(e.stat().st_ctime).strftime(DEFAULT_DATETIME_FORMAT_2)
                continue
            if e.is_file():
                file_path = e.path.removeprefix(session['c_working_path'])
                print('file_path',file_path,e.name)
                user_contents[file_path]['size'] = e.stat().st_size
                user_contents[file_path]['created'] = datetime.datetime.fromtimestamp(e.stat().st_ctime).strftime(DEFAULT_DATETIME_FORMAT_2)
                metadata = file_id_access(file_path[1:])
                user_contents[file_path]['link'] = metadata['link']
                user_contents[file_path]['shared'] = metadata['shared']
            else:                
                folder_path = e.path.removeprefix(session['c_working_path'])
                print('folder_path',folder_path,e.name)
                user_contents[folder_path]['size'] = get_dir_size(e)
                user_contents[folder_path]['created'] = datetime.datetime.fromtimestamp(e.stat().st_ctime).strftime(DEFAULT_DATETIME_FORMAT_2)
                metadata = file_id_access(folder_path[1:])
                user_contents[folder_path]['link'] = metadata['link']
                user_contents[folder_path]['shared'] = metadata['shared']
        else:
            return user_contents

@app.route('/<path:name>', methods  = ['GET'])
def display_file(name):
    print('display:',name)
    print(session['c_working_path'], name)
    if session.get('loggedin') and os.path.isdir(os.path.join(session.get('c_working_path'), name)):
        print(name, request.url, request.full_path, request.host)
        user_contents = folder_content(os.path.join(session['c_working_path'], name))
        return render_template("home.html", user_contents = user_contents, user_information = session['username'])
    else: ## Add elif statement with isfile(), but to make this work. Each and EVERY files should be present, i.e user_files, favicons, logos etc.
        return send_from_directory(session['c_working_path'], name)

def user_data_backup(Primary_Disk, Secondary_Disk, OPERATION):
    conn = sqlite3.connect(DEFAULT_DB)
    cursor =conn.cursor()
    if OPERATION == 'INSERT':
        date_time = datetime.datetime.now().strftime(DEFAULT_DATETIME_FORMAT)
        cursor.execute('INSERT INTO data_backup VALUES (?, ?, ?, ?, ?, ?, ?, ?)',(session['id'], Primary_Disk, Secondary_Disk, DEAFULT_MEMORY_ALLOCATION, "False",'Active',date_time, date_time))
        conn.commit()
    elif OPERATION == 'UPDATE':
        cursor.execute('UPDATE data_backup SET data_synced = ? WHERE user_id = ? and disk_status = ?',("False", session['id'], 'Active'))
        conn.commit()
    elif OPERATION == 'STOPPED':
        pass
    elif OPERATION =='CREATE_FOLDERS':
        cursor.execute('SELECT primary_disk, secondary_disk FROM data_backup WHERE user_id = ? and disk_status = ?',(session['id'],'Active'))
        result = cursor.fetchone()        
        primary_folder = os.path.join(result[0],session['username'])
        secondary_folder = os.path.join(result[1],session['username'])
        if not os.path.exists(primary_folder):
            os.makedirs(primary_folder)
            os.makedirs(os.path.join(primary_folder,'trash_come_recover'))
        if not os.path.exists(secondary_folder):
            os.makedirs(secondary_folder)
            os.makedirs(os.path.join(secondary_folder,'trash_come_recover'))
    elif OPERATION == 'SELECT':
        cursor.execute('SELECT primary_disk, secondary_disk FROM data_backup WHERE user_id = ? and disk_status = ?',(session['id'],'Active'))
        result = cursor.fetchone()
        conn.close()
        return result
    conn.close()

@app.route('/size_check', methods=['GET'])
def size_check():
    if session.get('loggedin'):
        session['user_consumed_size'] = get_dir_size(session['c_working_path'])
        return jsonify({'Size': session['user_consumed_size']})
    else:
        #session['user_consumed_size'] = 0
        abort(500)

def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

@app.route('/upload/<path:name>', methods=['POST'])
def file_upload(name):
    print("upload",name, request.url, request.full_path, request.host)
    if request.method == 'POST' and session.get('loggedin'):
        if name == 'home':
            name = ''
        _ = size_check()
        if session['user_consumed_size'] < session['total_memory_allocated']:
            user_directory = user_default_path()
            files = request.files.getlist('filename')
            for i in range(len(files)):
                _ = size_check()
                if session['user_consumed_size'] < session['total_memory_allocated']:
                    if os.path.exists(os.path.join(user_directory, name, files[i].filename)):
                        return jsonify(['Exists'])
                        continue ## File Already Exists
                    files[i].save(os.path.join(user_directory, name, files[i].filename))
                    print("Here Printing",os.path.join(name, files[i].filename))
                    creating_unique_link(os.path.join(name, files[i].filename))
                    user_data_backup(None, None, 'UPDATE')
                    HDS.user_level_backup(session['id']) ## syncing primary and secondary folder
                else:
                    return jsonify(['Storage Full, Expnad the limit, Added %s/%s files'%(i+0, len(files))])
            else:
                _ = size_check()
                return redirect(url_for('home'))
        else:
            return jsonify(['Storage Limit Reached',session['user_consumed_size']])
    else:
        return redirect(url_for('login'))

def creating_unique_link(f_name):
    conn = sqlite3.connect(DEFAULT_DB)
    cursor = conn.cursor()
    unique_file_id = ''.join(str(uuid.uuid4()).split('-'))+''.join(str(uuid.uuid4()).split('-'))
    cursor.execute('INSERT INTO data_sharing VALUES (?, ?, ?, ?)',(session['id'], f_name, unique_file_id, DEFAULT_LINK_ACCESS))
    conn.commit()
    conn.close()


#query = 'UPDATE data_sharing SET sharing_allowed = ? WHERE unique_file_id in (%s)' % ', '.join('?' for i in unique_id_list)
#cursor.execute(query,(access, *unique_id_list))
##http://192.168.1.13:1234/link_access?unique_file_id=b5df97d9e5744e69b3651023ffce76bd9c10dc610ca54636bde5aeaaced924de&access=True
@app.route('/link_access', methods=['GET'])
def link_access():
    if request.method == 'GET' and session.get('loggedin'):
        unique_file_id = request.args.get("unique_file_id")
        access = request.args.get("access")
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()                
        cursor.execute('SELECT file FROM data_sharing WHERE unique_file_id = ?', (unique_file_id, ))
        output = cursor.fetchone()
        if output:
            cursor.execute('SELECT a.username, db.primary_disk FROM data_backup db join accounts a on a.id=db.user_id WHERE db.user_id = ? and db.disk_status = ?',(session['id'],'Active'))
            disk_output = cursor.fetchone()
            directory = os.path.join(disk_output[1], disk_output[0])
            name = output[0]
            if os.path.isdir(os.path.join(directory, name)):
                cursor.execute('UPDATE data_sharing SET sharing_allowed = ? WHERE unique_file_id = ?',(access, unique_file_id))
                conn.commit()
                cursor.execute('UPDATE data_sharing SET sharing_allowed = ? WHERE user_id = ? and file like ?',(access, session['id'], os.path.join(name,'%')))
                conn.commit()
                conn.close()
                if access == 'True':
                    return jsonify(['Access to entire folder Granted'])
                else:
                    return jsonify(['Access to entire folder Revoked'])                
            else:
                cursor.execute('UPDATE data_sharing SET sharing_allowed = ? WHERE unique_file_id = ?',(access, unique_file_id))
                conn.commit()
                conn.close()
                if access == 'True':
                    return jsonify(['Access to File Granted'])
                else:
                    return jsonify(['Access to File Revoked'])
        else:            
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/new_folder/<path:name>', methods=['POST'])
def create_folder(name):
    print("create folder",name, request.url, request.full_path, request.host)
    if request.method == 'POST' and session.get('loggedin'):
        if name == 'home':
            name = ''
        folder_name_to_create = request.form.get('folder_name_to_create')
        user_directory = user_default_path()
        if not os.path.exists(os.path.join(user_directory, name, folder_name_to_create)):
            os.makedirs(os.path.join(user_directory, name, folder_name_to_create))
            creating_unique_link(os.path.join(name, folder_name_to_create))
            user_data_backup(None, None, 'UPDATE')
            HDS.user_level_backup(session['id']) ## syncing primary and secondary folder
        elif os.path.exists(os.path.join(user_directory, name, folder_name_to_create)):
            return jsonify(['Folder Already Exists'])        
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

##http://192.168.1.13:1234/get_link/DP.png
@app.route('/get_link/<path:file_name>', methods=['GET'])
def get_link(file_name):
    if request.method == 'GET' and session.get('loggedin'):
        print("get link",file_name)
        user_directory = user_default_path()
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT unique_file_id FROM data_sharing WHERE file=? and user_id = ?',(file_name, session['id']))
        result = cursor.fetchone()
        conn.close()
        if result:
            ##http://192.168.1.13:1234/shared/5a8e813e-a7a1-4d05-96ef-6e1a488832715a18be6a-0fce-4858-8f84-6a5bf3e0bccc
            return ['/'.join([DOMAIN_PREFIX, 'shared', result[0]])]
        else:
            return jsonify(['Requested File Not Found'])
    else:
        return redirect(url_for('login'))

def file_id_access(file_name):
    user_directory = user_default_path()
    conn = sqlite3.connect(DEFAULT_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT unique_file_id, sharing_allowed FROM data_sharing WHERE file = ? and user_id = ?',(file_name,session['id']))
    result = cursor.fetchone()
    conn.close()
    return {"link":result[0], "shared":result[1]}

##http://192.168.1.13:1234/shared/5a8e813e-a7a1-4d05-96ef-6e1a488832715a18be6a-0fce-4858-8f84-6a5bf3e0bccc
@app.route('/shared/<unique_id>', methods = ['GET'])
def open_link(unique_id):
    if request.method == 'GET':
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, file FROM data_sharing WHERE sharing_allowed = ? and unique_file_id = ?', ('True', unique_id, ))
        output = cursor.fetchone()
        if output:
            cursor.execute('SELECT a.username, db.primary_disk FROM data_backup db join accounts a on a.id=db.user_id WHERE db.user_id = ? and db.disk_status = ?',(output[0],'Active'))
            disk_output = cursor.fetchone()
            directory = os.path.join(disk_output[1], disk_output[0])
            name = output[1]
            print("output",output)
            print("disk_output",disk_output)
            print("directory",directory)
            print("name",name)
            print("new",disk_output[0],name)
            conn.close()
            if os.path.isdir(os.path.join(directory, name)):
                shared_contents = folder_content(os.path.join(directory, name))
                return render_template("shared_folder.html", shared_contents = shared_contents)
                ## create shared_folder display and other function
            else:
                return send_from_directory(directory, name)                        
        else:
            cursor.execute('SELECT user_id, file FROM data_sharing WHERE sharing_allowed = ? and unique_file_id = ?', ('False', unique_id, ))
            output = cursor.fetchone()
            if output:
                return jsonify(['Request Access'])
            else: 
                return jsonify(['Link not Found'])

@app.route('/delete/<path:filename_to_delete>', methods = ['GET'])
def delete(filename_to_delete):
    if request.method == 'GET' and session.get('loggedin'):
        user_directory = user_default_path()
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        if os.path.exists(os.path.join(user_directory, filename_to_delete)):            
            if os.path.isdir(os.path.join(user_directory, filename_to_delete)):
                shutil.rmtree(os.path.join(user_directory, filename_to_delete))
                cursor.execute('DELETE FROM data_sharing WHERE user_id = ? and file = ?', (session['id'], filename_to_delete))
                conn.commit()
                cursor.execute('DELETE FROM data_sharing WHERE user_id = ? and file like ?', (session['id'], os.path.join(filename_to_delete,'%')))
                conn.commit()
                conn.close()
            if os.path.isfile(os.path.join(user_directory, filename_to_delete)):
                os.remove(os.path.join(user_directory, filename_to_delete))                
                cursor.execute('DELETE FROM data_sharing WHERE user_id = ? and file = ?', (session['id'], filename_to_delete))
                conn.commit()
                conn.close()
            user_data_backup(None, None, 'UPDATE')
            HDS.user_level_backup(session['id']) ## syncing primary and secondary folder
            return redirect(url_for('home'))
        else:
            return jsonify(['File to delete not Found'])
    else:
        return redirect(url_for('home'))

@app.route('/move_to_trash/<path:filename_to_move_to_trash>', methods=['GET'])
def move_to_trash(filename_to_move_to_trash):
    if request.method == 'GET' and session.get('loggedin'):
        user_directory = user_default_path()
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        if os.path.exists(os.path.join(user_directory, filename_to_move_to_trash)):
            shutil.move(os.path.join(user_directory, filename_to_move_to_trash),os.path.join(user_directory, "trash_come_recover"))
            return jsonify(['File moved to trash folder'])
        else:
            return jsonify(['File to move to trash not Found'])
    else:
        return redirect(url_for('home'))

@app.route('/recover_from_trash/<path:filename_to_recover_from_trash>', methods=['GET'])
def recover_from_trash(filename_to_recover_from_trash):
    if request.method == 'GET' and session.get('loggedin'):
        user_directory = user_default_path()
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        if os.path.exists(os.path.join(user_directory, filename_to_recover_from_trash)):
            shutil.move(os.path.join(user_directory, filename_to_recover_from_trash),os.path.join(user_directory, ""))
            return jsonify(['File moved back from home folder'])
    else:
        return redirect(url_for('home'))

@app.route('/')
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if session.get('loggedin'):
        return redirect(url_for('home'))
    if request.method == 'POST'  and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, total_memory_allocated FROM accounts where email = ? and password = ?', (email, hash_password(password+email),))
        account = cursor.fetchone()
        conn.close()
        if account:
            ### Logged in Successfully 
            session['loggedin'] = True
            session['id'] = account[0]            
            session['username'] = account[1]
            session['total_memory_allocated'] = account[2]
            return redirect(url_for('home'))
        else:
            conn = sqlite3.connect(DEFAULT_DB)
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, total_memory_allocated FROM accounts where email = ?', (email,))
            account_u = cursor.fetchone()
            conn.close()
            if account_u:
                ### Email is correct but Password did not match
                login_msg = 'Password did not match !'
                message_type = 'password'
            else:
                ### Email is incorrect 
                login_msg = 'Email does not exist !'
                message_type = 'email'
        login_message = {
            'status_message':'failed',
            'data':{
                'message':login_msg,
                'message_type': message_type
                }
            }
        return login_message
    elif request.method == 'GET':
        return render_template('auth-sign-in.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('total_memory_allocated', None)
    session.pop('user_consumed_size', None)
    session.pop('c_working_path', None)
    return redirect(url_for('login'))

def finding_strorage_category(memory):
    ## Increase in category can be done for more storage here
    GB = 1024*1024
    if memory == DEAFULT_MEMORY_ALLOCATION :
        return 1
    elif memory >= 10*GB and memory < 25*GB :
        return 2
    elif memory >= 25*GB and memory < 50*GB :
        return 3
    elif memory >= 50*GB and memory < 75*GB :
        return 4
    elif memory >= 75*GB and memory <= 100*GB :
        return 5
    elif memory > 100*GB :
        return 5

@app.route('/change_storage/<required_storage>', methods = ['GET'])
def change_storage(required_storage):
    if request.method == 'GET' and session.get('loggedin'):
        GB = 1024*1024
        required_storage = int(required_storage)*GB
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT dm.disk_storage_category, db.primary_disk, db.secondary_disk FROM data_backup db join disk_metadata dm on db.primary_disk = dm.disk_name WHERE db.user_id = ? and db.disk_status = ?', (session['id'], 'Active', ))
        output = cursor.fetchone()
        new_storage_category = finding_strorage_category(required_storage)
        if new_storage_category == -1:
            return 'Storage Cannot be Provided'
        else:
            if output[0] == new_storage_category:
                modified_date_time = datetime.datetime.now().strftime(DEFAULT_DATETIME_FORMAT)
                cursor.execute('UPDATE data_backup SET memory_allocated = ?, modified_date = ? WHERE user_id = ? and disk_status = ?', (required_storage, modified_date_time, session['id'], 'Active', ))            
                cursor.execute('UPDATE accounts SET total_memory_allocated = ? WHERE id = ?', (required_storage, session['id'], ))
                conn.commit()
                conn.close()
                DA.updating_disk(output[1],'P')
                DA.updating_disk(output[2],'S')
                session['total_memory_allocated'] = required_storage
                return 'storage_increased to %s'%(required_storage)
            else:
                HDS.user_level_backup(session['id']) ## syncing old_primary and old_secondary folder
                New_Primary_Disk, New_Secondary_Disk = DA.allocate_disk_to_user(required_storage,new_storage_category)
                modified_date_time = datetime.datetime.now().strftime(DEFAULT_DATETIME_FORMAT)
                cursor.execute('UPDATE data_backup SET disk_status = ?, modified_date = ? WHERE user_id = ? and disk_status = ?', ('Copy', modified_date_time, session['id'], 'Active', ))
                cursor.execute('INSERT INTO data_backup VALUES (?, ?, ?, ?, ?, ?, ?, ?)',(session['id'], New_Primary_Disk, New_Secondary_Disk, required_storage, "False",'Waiting',modified_date_time, modified_date_time))
                conn.commit()
                conn.close()

                new_primary_folder = os.path.join(New_Primary_Disk,session['username'])
                new_secondary_folder = os.path.join(New_Secondary_Disk,session['username'])
                if not os.path.exists(new_primary_folder):
                    os.makedirs(new_primary_folder)
                if not os.path.exists(new_secondary_folder):
                    os.makedirs(new_secondary_folder)
        
                HDS.change_storage_backup(output[1], New_Primary_Disk, session['username'], session['id']) ## Copy old_primary to new_primary folder
                shutil.rmtree(os.path.join(output[1], session['username'])) ## delete old primary folder          
                shutil.rmtree(os.path.join(output[2], session['username'])) ## delete old secondary folder
                 
                conn = sqlite3.connect(DEFAULT_DB)
                cursor = conn.cursor()
                modified_date_time = datetime.datetime.now().strftime(DEFAULT_DATETIME_FORMAT)
                cursor.execute('UPDATE data_backup SET disk_status = ?, modified_date = ?, memory_allocated = ? WHERE user_id = ? and disk_status = ?', ('Deleted', modified_date_time, 0, session['id'], 'Copy', ))
                cursor.execute('UPDATE data_backup SET disk_status = ?, modified_date = ? WHERE user_id = ? and disk_status = ?', ('Active', modified_date_time, session['id'], 'Waiting', ))            
                cursor.execute('UPDATE accounts SET total_memory_allocated = ? WHERE id = ?', (required_storage, session['id'], ))
                conn.commit()
                conn.close()

                DA.updating_disk(New_Primary_Disk,'P')
                DA.updating_disk(New_Secondary_Disk,'S')
                DA.updating_available_users(New_Primary_Disk,'ADD_USER')
                DA.updating_available_users(New_Secondary_Disk,'ADD_USER')

                DA.updating_disk(output[1],'P')
                DA.updating_disk(output[2],'S')
                DA.updating_available_users(output[1],'REMOVE_USER')
                DA.updating_available_users(output[2],'REMOVE_USER')
                session['total_memory_allocated'] = required_storage
                return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if session.get('loggedin'):
        return redirect(url_for('home'))  
    if request.method == 'POST' and 'fullname' in request.form and 'email' in request.form and 'password' in request.form :        
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        username = request.form['email'].replace('@','').replace('.','')
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE email = ?', (email, ))
        account = cursor.fetchone()
        if account:
            message_type = 'email'
            register_msg = 'Account already exists !'
        elif len(fullname) < 1:
            message_type = 'fullname'
            register_msg = 'Invalid Fullname !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message_type = 'email'
            register_msg = 'Invalid email address !'
        elif len(password) < 8 or not re.search("[a-z]", password) or not re.search("[A-Z]", password) or not re.search("[0-9]", password):
            message_type = 'password'
            register_msg = 'Password did not meet criteria !'        
        else:
            date_time = datetime.datetime.now().strftime(DEFAULT_DATETIME_FORMAT)
            cursor.execute('INSERT INTO accounts VALUES (NULL, ?, ?, ?, ?, ?, ?)',(fullname, username, hash_password(password+email), email, DEAFULT_MEMORY_ALLOCATION, date_time))
            conn.commit()
            cursor.execute('SELECT id, username, total_memory_allocated FROM accounts WHERE email = ? and password = ? ', (email, hash_password(password+email),))
            account = cursor.fetchone()
            conn.close()
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            session['total_memory_allocated'] = account[2]             
            disk_storage_category = finding_strorage_category(DEAFULT_MEMORY_ALLOCATION)
            Primary_Disk, Secondary_Disk = DA.allocate_disk_to_user(DEAFULT_MEMORY_ALLOCATION,disk_storage_category)
            user_data_backup(Primary_Disk, Secondary_Disk, "INSERT")            
            DA.updating_disk(Primary_Disk,'P')
            DA.updating_disk(Secondary_Disk,'S')
            DA.updating_available_users(Primary_Disk,'ADD_USER')
            DA.updating_available_users(Secondary_Disk,'ADD_USER')
            user_data_backup(None, None, 'CREATE_FOLDERS')            
            return redirect(url_for('home'))
        register_message = {
            'status_message':'failed',
            'data':{
                'message':register_msg, 
                'message_type':message_type
                }
            }
        return register_message
    elif request.method == 'GET':
        return render_template('auth-sign-up.html')

@app.route('/reset_change_password', methods = ['POST', 'GET'])
def reset_change_password():
    if request.method == 'POST' and 'password' in request.form and 'confirm_password' in request.form and 'unique_token' in request.form:
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        unique_token = request.form['unique_token']
        print('password', password, confirm_password, 'token', unique_token)
        if password == confirm_password and unique_token and len(password) >= 8 and re.search("[a-z]", password) and re.search("[A-Z]", password) and re.search("[0-9]", password):
            conn = sqlite3.connect(DEFAULT_DB)
            cursor = conn.cursor()
            cursor.execute('SELECT a.email, a.id, a.username, a.total_memory_allocated FROM accounts a join reset_password rp on a.id = rp.user_id WHERE rp.token = ?', (unique_token, ))
            account = cursor.fetchone()
            cursor.execute('UPDATE accounts SET password = ? WHERE email = ?', (hash_password(password+account[0]), account[0], ))
            conn.commit()
            conn.close()
            session['loggedin'] = True
            session['id'] = account[1]
            session['username'] = account[2]
            session['total_memory_allocated'] = account[3]
            return redirect(url_for('home'))
        else:
            msg = 'Password did not meet criteria !'
            reset_message = {
                'status_message':'failed',
                'data':{
                    'message':msg
                    }
                }
            return reset_message
    elif request.method == 'GET':
        return render_template('auth-recover-password.html')
    
@app.route('/reset_change_password_request',methods = ['POST'])
def reset_change_password_request():
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM accounts WHERE email = ?', (email, ))
        account = cursor.fetchone()
        if account:   
            token = ''.join(str(uuid.uuid4()).split('-'))+''.join(str(uuid.uuid4()).split('-'))
            cursor.execute('INSERT INTO reset_password VALUES (?, ?, ?)', (account[0], token, time.time()+300, ))
            conn.commit()
            conn.close()
            action_url = '/'.join([DOMAIN_PREFIX, 'verify', token])  ## Send this to user_mail            
            MAIL_SUBJECT = config['MAIL_SUBJECTS']['password_reset']
            MAIL_TEMAPLTE =  config['MAIL_TEMPLATES']['password_reset']           
            MD_M.send_mail_to_user(MD_M.sender_email,email,MAIL_SUBJECT,MAIL_TEMAPLTE,action_url,MD_M.support_url,MD_M.smtp_server,MD_M.port,MD_M.mail_login,MD_M.mail_password)
            
            auth_confirm_path = os.path.join('templates','html_templates','auth_confirm.html')    
            auth_confirm_file = open(auth_confirm_path,'r')
            auth_confirm_file_content = auth_confirm_file.read()
            auth_confirm_file_content = auth_confirm_file_content.replace("{{email}}",email)
            auth_confirm_file.close()
            recover_password_message = {
                'status_message':'success',
                'data':{
                    'message_head':'Done !',
                    'message_para':'',
                    'message_body':auth_confirm_file_content    
                }
            }
            return recover_password_message
        else:
            msg = 'Email does not exist !'
            recover_password_message = {
                'status_message':'failed',
                'data':{
                    'message':msg
                    }
                }
            return recover_password_message

@app.route('/verify/<unique_token>', methods = ['GET'])
def verify_change_reset_link(unique_token):
    if request.method == 'GET':
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM reset_password WHERE token = ? and expiry > ?', (unique_token, time.time(), ))
        account = cursor.fetchone()
        if account:
            conn.close()
            return render_template('auth-password-reset.html', unique_token = unique_token)
        else:
            cursor.execute('SELECT user_id FROM reset_password WHERE token = ? and expiry <= ?', (unique_token, time.time(), ))
            account = cursor.fetchall()
            if account:
                conn.close()
                message_head = 'Oops!!!'
                message_para = 'Missed it'
                message_body = 'The Link you clicked has expired, Please try resetting your password again by clicking the below available button.'
                return render_template('expired_invalid_token.html', 
                        message_head = message_head,
                        message_para = message_para,
                        message_body = message_body
                    )
            else:
                message_head = 'Hey !!! Hey !!! Hey !!!'
                message_para = 'Lucky'
                message_body = 'The Link you clicked is not available, If you are looking to reset password click the below available button. If you landed on this page accidentally close the window.'
                return render_template('expired_invalid_token.html', 
                        message_head = message_head,
                        message_para = message_para,
                        message_body = message_body
                    )
                
def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()

if __name__ == "__main__":
  app.run(debug=True, host='192.168.1.13', port=1234 ) #ssl_context='adhoc'
