import configparser
import os
config = configparser.ConfigParser()
db_path = os.path.join('db','cloud_storage.db')
config['DEFAULT'] = {'database' : db_path,
                     'default_memory_allocation': 1024*1024,
                     'default_link_access' : 'False',
                     'domain_prefix' : 'http://192.168.1.13:1234',
                     'default_temp_storage' : 'MASTER'
                     }
config['DATA'] = {'datetime_format': '%%d_%%m_%%Y_%%H_%%M_%%S.%%f',
                  'datetime_format_2': '%%d %%B %%Y %%H:%%M:%%S'
                  }
with open(os.path.join('configuration','configuration.ini'), 'w') as configfile:
  config.write(configfile)

###########
###########
config = configparser.ConfigParser()
config['DEFAULT'] = {'disk_category' : 'P',
                     'mirror_disk_category' : 'S'
                     }
config['DISK'] = {'disk_name' : 'SSD',
                  'mirror_disk_name' : 'disk',
                  }
with open(os.path.join('configuration','new_disk.ini'), 'w') as configfile:
  config.write(configfile)

###########
###########
config = configparser.ConfigParser()
config['DEFAULT'] = {'mail_server' : 'smtp.gmail.com',
                     'mail_port' : '587',
                     'mail_use_tls' : 'False',
                     'mail_use_ssl' : 'True'
                     }
config['CREDENTIALS'] = {'mail_username' : 'xx@yy.com',
                        'mail_password' : 'xxyyzzz',
                         'sender' : 'xx@yy.com',
                         'reply_to' : 'aa@bb.cc' 
                        }
config['MAIL_SUBJECTS'] = {'password_reset' : "Reset Change Password Request"
                           }
config['MAIL_TEMPLATES'] = {'password_reset' : "reset_password_mail.html"
                           }
with open(os.path.join('configuration','mail.ini'), 'w') as configfile:
  config.write(configfile)
