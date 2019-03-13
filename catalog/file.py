from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_Setup import Base, GameType, GameName, GmailUser
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///games.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "GameStore"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
value = session.query(GameType).all()


# login


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    value = session.query(GameType).all()
    vg = session.query(GameName).all()
    return render_template('login.html',
                           STATE=state, value=value, vg=vg)
# return render_template('myhome.html', STATE=state
# value=value,vg=vg)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = GmailUser(name=login_session['username'], email=login_session[
                   'email'])
    session.add(User1)
    session.commit()
    user = session.query(GmailUser).filter_by(
                                            email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(GmailUser).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(GmailUser).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


# Home
@app.route('/')
@app.route('/home')
def home():
    value = session.query(GameType).all()
    return render_template('myhome.html', value=value)


# Game Category for admins


@app.route('/GameStore')
def GameStore():
    try:
        if login_session['username']:
            name = login_session['username']
            value = session.query(GameType).all()
            video = session.query(GameType).all()
            vg = session.query(GameName).all()
            return render_template('myhome.html', value=value,
                                   video=video, vg=vg, uname=name)
    except:
        return redirect(url_for('showLogin'))


# Showing game based on game category
@app.route('/GameStore/<int:veid>/AllCompanys')
def showGames(veid):
    value = session.query(GameType).all()
    video = session.query(GameType).filter_by(id=veid).one()
    vg = session.query(GameName).filter_by(gametypeid=veid).all()
    try:
        if login_session['username']:
            return render_template('showGames.html', value=value,
                                   video=video, vg=vg,
                                   uname=login_session['username'])
    except:
        return render_template('showGames.html',
                               value=value, video=video, vg=vg)


# Add New Game
@app.route('/GameStore/addGameName', methods=['POST', 'GET'])
def addGameName():
    if request.method == 'POST':
        game = GameType(name=request.form['name'],
                        user_id=login_session['user_id'])
        session.add(game)
        session.commit()
        return redirect(url_for('GameStore'))
    else:
        return render_template('addGameName.html', value=value)


# Edit Game Category
@app.route('/GameStore/<int:veid>/edit', methods=['POST', 'GET'])
def editGameName(veid):
    editGame = session.query(GameType).filter_by(id=veid).one()
    creator = getUserInfo(editGame.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Game Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('GameStore'))
    if request.method == "POST":
        if request.form['name']:
            editGame.name = request.form['name']
        session.add(editGame)
        session.commit()
        flash("Game Category Edited Successfully")
        return redirect(url_for('GameStore'))
    else:
        # value is global variable we can them in entire application
        return render_template('editGameName.html',
                               ve=editGame, value=value)

# Delete Game Category


@app.route('/GameStore/<int:veid>/delete', methods=['POST', 'GET'])
def deleteGameName(veid):
    ve = session.query(GameType).filter_by(id=veid).one()
    creator = getUserInfo(ve.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Game Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('GameStore'))
    if request.method == "POST":
        session.delete(ve)
        session.commit()
        flash("Game Category Deleted Successfully")
        return redirect(url_for('GameStore'))
    else:
        return render_template('deleteGameName.html', ve=ve, value=value)


# Add New Game Name Details


@app.route('/GameStore/addCompany/addGameDetails/<string:vename>/add',
           methods=['GET', 'POST'])
def addGameDetails(vename):
    video = session.query(GameType).filter_by(name=vename).one()
    # See if the logged in user is not the owner of Game
    creator = getUserInfo(video.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new game edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGames', veid=video.id))
    if request.method == 'POST':
        name = request.form['name']
        year = request.form['year']
        developer = request.form['developer']
        publisher = request.form['publisher']
        mode = request.form['mode']
        gameprogrammer = request.form['gameprogrammer']
        gamedetails = GameName(name=name,
                               year=year,
                               developer=developer,
                               publisher=publisher,
                               mode=mode,
                               gameprogrammer=gameprogrammer,
                               gametypeid=video.id,
                               gmailuser_id=login_session['user_id'])
        session.add(gamedetails)
        session.commit()
        return redirect(url_for('showGames', veid=video.id))
    else:
        return render_template('addGameDetails.html',
                               vename=video.name, value=value)


# Edit Game details


@app.route('/GameStore/<int:veid>/<string:vogname>/edit',
           methods=['GET', 'POST'])
def editGame(veid, vogname):
    ve = session.query(GameType).filter_by(id=veid).one()
    gamedetails = session.query(GameName).filter_by(name=vogname).one()
    # See if the logged in user is not the owner of Game
    creator = getUserInfo(ve.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this game edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGames', veid=ve.id))
    # POST methods
    if request.method == 'POST':
        gamedetails.name = request.form['name']
        gamedetails.year = request.form['year']
        gamedetails.developer = request.form['developer']
        gamedetails.publisher = request.form['publisher']
        gamedetails.mode = request.form['mode']
        gamedetails.gameprogrammer = request.form['gameprogrammer']
        session.add(gamedetails)
        session.commit()
        flash("Game Edited Successfully")
        return redirect(url_for('showGames', veid=veid))
    else:
        return render_template('editGame.html',
                               veid=veid, gamedetails=gamedetails,
                               value=value)


# Delte Game Edit


@app.route('/GameStore/<int:veid>/<string:vogname>/delete',
           methods=['GET', 'POST'])
def deleteGame(veid, vogname):
    ve = session.query(GameType).filter_by(id=veid).one()
    gamedetails = session.query(GameName).filter_by(name=vogname).one()
    # See if the logged in user is not the owner of Game
    creator = getUserInfo(ve.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this game edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGames', veid=ve.id))
    if request.method == "POST":
        session.delete(gamedetails)
        session.commit()
        flash("Deleted game Successfully")
        return redirect(url_for('showGames', veid=veid))
    else:
        return render_template('deleteGame.html',
                               veid=veid, gamedetails=gamedetails,
                               value=value)


# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'}
                  )[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
                                'Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('home'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Json


@app.route('/GameStore/JSON')
def allGamesJSON():
    gamecategories = session.query(GameType).all()
    category_dict = [c.serialize for c in gamecategories]
    for c in range(len(category_dict)):
        games = [i.serialize for i in session.query(
                 GameName).filter_by(gametypeid=category_dict[c]["id"]).all()]
        if games:
            category_dict[c]["game"] = games
    return jsonify(GameType=category_dict)

####


@app.route('/GameStore/gameCategories/JSON')
def categoriesJSON():
    games = session.query(GameType).all()
    return jsonify(gameCategories=[c.serialize for c in games])

####


@app.route('/GameStore/game/JSON')
def itemsJSON():
    items = session.query(GameName).all()
    return jsonify(game=[i.serialize for i in items])


@app.route('/GameStore/<path:game_name>/game/JSON')
def categoryItemsJSON(game_name):
    gameCategory = session.query(GameType).filter_by(name=game_name).one()
    games = session.query(GameName).filter_by(gamename=gameCategory).all()
    return jsonify(gameEdtion=[i.serialize for i in games])

#####


@app.route('/GameStore/<path:game_name>/<path:edition_name>/JSON')
def ItemJSON(game_name, edition_name):
    gameCategory = session.query(GameType).filter_by(name=game_name).one()
    gameEdition = session.query(GameName).filter_by(
           name=edition_name, gamename=gameCategory).one()
    return jsonify(gameEdition=[gameEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
