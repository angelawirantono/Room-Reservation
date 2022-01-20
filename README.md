# VRRA - Virtual Room Reservation Assistant
*Software Engineering Final Project by Group 21*

## Install
#### Optional 
Create a virtualenv and activate it. For **Windows cmd**: 
```
python -m venv
.\venv\Scripts\activate
```
Other platforms might require different commands.
### Dependencies
This project uses multiple Flask extensions. To install all the requirements:
```
pip install -r requirements.txt
```
### Run
Make sure to do the following while `pwd` is outside of `app` directory:
```
flask init-db
flask run
```
### Available CLI commands
- `flask init-db` Overwrites existing database, creates a new one right after.   
- `flask drop-db` Drops existing database.   
- `flask create-admin` Creates admin account.   
  - Username: admin    
  - Password: admin

The website should be accessible at *localhost* `http://127.0.0.1:5000/`
