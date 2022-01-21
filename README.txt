# VRRA - Virtual Room Reservation Assistant
*Software Engineering Final Project by Group 21*

## Documents
All required documents including: SRS, SAD, SDD and User Guide can be found on the `Documents` folder.

## Source Code
Main project source code can be found in `SourceCode` folder.

### Install
#### Optional virtual environment 
Create a virtualenv and activate it. For **Windows cmd**: 
```
python -m venv
.\venv\Scripts\activate
```
Other platforms might require different commands. Check https://docs.python.org/3/library/venv.html for more details.

#### Run
Make sure to do the following while the present working directory is right outside of the `app` directory:
```
# install all requirements (packages)
pip install -r requirements.txt

# initializes database
flask init-db

# run program
flask run
```
`py -m` or `python -m` might be needed for some platforms.   
The website should now be accessible at *localhost* `http://127.0.0.1:5000/`

#### Available CLI commands
- `flask init-db` Overwrites existing database, creates a new one right after.   
- `flask drop-db` Drops existing database.   
- `flask create-admin` Creates admin account.   
  - Username: admin    
  - Password: admin

## Presentation Video Link
System explanation: https://youtu.be/zJpvm7IQ6cY
