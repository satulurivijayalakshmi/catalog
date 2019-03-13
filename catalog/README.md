# Item Catalog Web App
By SATULURI VIJAYA LAKSHMI
This web app is a project for the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## About
This project is a RESTful web application utilizing the Flask framework which accesses a SQL database that populates game categories and their editions. OAuth2 provides authentication for further CRUD functionality on the application. Currently OAuth2 is implemented for Google Accounts.

## In This Project
This project has one main Python module `file.py` which runs the Flask application. A SQL database is created using the `db_Setup.py` module and you can populate the database with test data using `init.py`.
The Flask application uses stored HTML templates in the tempaltes folder to build the front-end of the application.

## Skills Required
1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework
6.DataBaseModels
## Installation
There are some dependancies and a few instructions on how to run the application.
Seperate instructions are provided to get GConnect working also.

## Dependencies
- [Vagrant](https://www.vagrantup.com/)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)



## How to Install
1. Install Vagrant & VirtualBox
2. Clone the Udacity Vagrantfile
3. Go to Vagrant directory and either clone this repo or download and place zip here
3. Launch the Vagrant VM (`vagrant up`)
4. Log into Vagrant VM (`vagrant ssh`)
5. Navigate to `cd /vagrant` as instructed in terminal
6. The app imports requests which is not on this vm. Run pip install requests

Or you can simply Install the dependency libraries (Flask, sqlalchemy, requests,psycopg2 and oauth2client) by running 
`pip install -r requirements.txt`

7. Setup application database `python /games/db_Setup.py`
8. *Insert sample data `python /games/init.py`
9. Run application using `python /games/file.py`
10. Access the application locally using http://localhost:8000

*Optional step(s)

## Using Google Login
To get the Google login working there are a few additional steps:

1. Go to [Google Dev Console](https://console.developers.google.com)
2. Sign up or Login if prompted
3. Go to Credentials
4. Select Create Crendentials > OAuth Client ID
5. Select Web application
6. Enter name 'GameStore'
7. Authorized JavaScript origins = 'http://localhost:8000'
8. Authorized redirect URIs = 'http://localhost:8000/login' && 'http://localhost:8000/gconnect'
9. Select Create
10. Copy the Client ID and paste it into the `data-clientid` in login.html
11. On the Dev Console Select Download JSON
12. Rename JSON file to client_secrets.json
13. Place JSON file in Gamestore directory that you cloned from here
14. Run application using `python /games/main.py`

## JSON Endpoints
The following are open to the public:

Games Catalog JSON: `/GameStore/JSON`
    - Displays the whole Games models catalog. Game Categories and all models.

Game Categories JSON: `/GameStore/GameCategories/JSON`
    - Displays all Game categories
All Game Editions: `/gameStore/editions/JSON`
	- Displays all Game Models

Game Edition JSON: `/gameStore/<path:gamename>/editions/JSON`
    - Displays Game models for a specific Game category

Game Category Edition JSON: `/gameStore/<path:gamename>/<path:edition_name>/JSON`
    - Displays a specific Game category Model.

## Miscellaneous

This project is inspiration from [gmawji](https://github.com/gmawji/item-catalog).
