# cloud_storage
This repo is for Cloud Storage Application.

* Users can Sign Up / Login, use a storage space, and pay accordingly.
   
* The user can upload file, folder, create a new folder, share the file with a user.
   
* The revoke access to shared file, delete a file, folder, retrieve the file, folder from deleted state back to original path in 30 days
  
* The pricing plans are continuous, thereby allowing users to choose any discrete storage 10 Gb, 11G, 12GB etc...
  
* Users have the flexibility to increase or decrease there storage plan any time in discrete of 1 GB.
  
* In the backend
  
   * Flask is the underlying framework used in Python for building the API's
     
   * Disk allocation to a particular user involves allocating some space in hard-disk and tracking the used space against the plan purchased
     
   * SQLLite is the Database used to store the accounts, harddisk metadata, user space usage metadata, file/folder shared metadata etc
 
   * For the front end, I have extensively used Javascript with Ajax to load the page without refreshing the page and to reduce data flow from server to client.
     
   * Hard-disk needs to attached when an existing disk is nearing its full capacity.
     
   * Allocation of memory to user is based on the alogirthm of categorization, where in there are 5 category of disks, A, B, C, D & E
     
   * Category A disk is used while allocating space to a new user who gets 1 GB of free space on Sign-Up
     
   * Category B disk is used to allocate any user who chooses to subscribe for the range of 10-24GB
     
   * Category C disk is used to allocate any user who chooses to subscribe for the range of 25-49GB
     
   * Category D disk is used to allocate any user who chooses to subscribe for the range of 50-74GB
     
   * Category E disk is used to allocate any user who chooses to subscribe for the range of 75-100GB
     
   * A job runs daily to clear the trash/bin of each user against the 30-day limit to recover the deleted items.
     
   * The SMPT server is used to send emails to users on sign-up, and account recovery processes i.e forgot password, and reset password with long tokens to prevent fraud.
     
   * disk recovery ensures that any disk failure does not impact the user and he/she still has the data in other backup disks
     
   * disk mapping is done to ensure the backup of each disk is done properly and API endpoints automatically connect to the backup disk.
  
* app.py is the file where the program starts
  
* configuration files contains the configuration for each of the services i.e email, accounts, disk utilization etc...
