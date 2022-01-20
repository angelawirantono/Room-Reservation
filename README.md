# Room-Reservation

## Installing dependencies
This project uses multiple Flask extensions. To install all the requirements, run   
`pip install -r requirements.txt`

## Before running
The database must be initialized before running the app. 
There exists several `CLI commands` to directly modify the database.
> `flask init-db` Overwrites existing database, creates a new one right after.   
> `flask drop-db` Drops existing database.   
> `flask create-admin` Creates admin account.   
  
## How to run
Make sure to do the following while pwd is outside of `project` directory
1. Type `$env:FLASK_ENV = "development"`
2. Type `flask run`

The website should be accessible in the localhost `http://127.0.0.1:5000/`
