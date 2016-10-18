#!/usr/bin/python -u
import os
from os import walk, path
from os.path import splitext, join
import sys, getopt
import re
import glob
import csv
from sys import argv
from flask import *
from json import dumps
from werkzeug import secure_filename
import subprocess
#from flask.ext.cors import CORS
from config import *
from indicdocs import *
from oauth import *
from flask import Flask, redirect, url_for, render_template
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn

#from file import file_api
from books import books_api
#from oauthapp import oauth_api

app = Flask(__name__)

app.register_blueprint(books_api, url_prefix='/books')
#app.register_blueprint(oauth_api, url_prefix='/oauthapp')

app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1706950096293019',
        'secret': '1b2523ac7d0f4b7a73c410b2ec82586c'
    },
    'twitter': {
        'id': '3RzWQclolxWZIMq5LJqzRZPTl',
        'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    }
}

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

@app.route('/homepage')
def mainpage():
    return render_template('home.html', title='Home')

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    return render_template('index.html')
    #return render_template('home.html', title='Home')


@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully!", 'info')
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        #return redirect(url_for('index'))
        return redirect(url_for('mainpage'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('mainpage'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('mainpage'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('mainpage'))


@app.route('/<filename>')
def root(filename):
    return app.send_static_file(filename)

@app.route('/abspath/<path:filepath>')
def readabs(filepath):
    abspath="/"+filepath
    #print "final-path:",abspath
    head, tail = os.path.split(abspath)
    return send_from_directory(head,tail)

@app.route('/relpath/<path:relpath>')
def readrel(relpath):
    return (send_from_directory(workdir(), relpath))

@app.route('/browse/<path:relpath>')
def browsedir(relpath):
    fullpath = join(workdir(), relpath)
    print fullpath
    return render_template("fancytree.html", abspath=fullpath)

#@app.route('/<path:abspath>')
#def details_dir(abspath):
#	print "abspath:",abspath
#	return render_template("fancytree.html", abspath='/'+abspath)

@app.route('/dirtree/<path:abspath>')
def listdirtree(abspath):
    #print abspath
    data = list_dirtree("/" + abspath)
    #print "Data:",json.dumps(data)
    return json.dumps(data)

@app.route('/taillog/<string:nlines>/<path:filepath>')
def getlog(nlines, filepath):
    lpath = join(repodir(), filepath)
    print "get logfile " + lpath
    p = subprocess.Popen(['tail','-'+nlines,lpath], shell=False,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    p_stdout=p.stdout.read()
    #print p_stdout
    return '''
        <html>
        <meta http-equiv="refresh" content="15">
        <head>
        </head>
        <body>
        <h1>Reading log file ''' + filepath + '''...</h1>
        <div id="scbar" style="border:1px solid black;height:350px;width:600px;overflow-y:auto;white-space:pre"><p>'''+p_stdout+'''</p>
        </div>
        </body>
        </html>
        '''   

(cmddir, cmdname) = os.path.split(argv[0])
setmypath(os.path.abspath(cmddir))
print "My path is " + mypath()

def usage():
    print cmdname + " [-r] [-R] [-d] [-o <workdir>] [-l <local_wloads_dir>] <repodir1>[:<reponame>] ..."
    exit(1)

parms = DotDict({
    'reset' : False,
    'dbreset' : False,
    'dbgFlag' : False,
    'myport' : PORTNUM,
    'localdir' : None,
    'wdir' : workdir(),
    'repos' : [],
    })

def setup_app(parms):
    setworkdir(parms.wdir, parms.myport)
    print cmdname + ": Using " + workdir() + " as working directory."
    
    initworkdir(parms.reset)

    initdb(INDICDOC_DBNAME, parms.dbreset)

    for a in parms.repos:
        components = a.split(':')
        if len(components) > 1:
            print "Importing " + components[0] + " as " + components[1]
            addrepo(components[0], components[1])
        else: 
            print "Importing " + components[0]
            addrepo(components[0], "")

    if parms.localdir:
        setwlocaldir(parms.localdir)
    if not path.exists(wlocaldir()):
        setwlocaldir(DATADIR_BOOKS)
    os.chdir(workdir())

    # Import all book metadata into the IndicDocs database
    getdb().books.importAll(repodir())

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "do:l:p:rRh", ["workdir=", "wloaddir="])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ("-o", "--workdir"):
	    parms.wdir=arg
        elif opt in ("-l", "--wloaddir"):
            parms.localdir = arg
        elif opt in ("-p", "--port"):
            parms.myport = int(arg)
        elif opt in ("-r", "--reset"):
            parms.reset = True
        elif opt in ("-R", "--dbreset"):
            parms.dbreset = True
        elif opt in ("-d", "--debug"):
            parms.dbgFlag = True
    parms.repos = args

    setup_app(parms)

    print "Available on the following URLs:"
    for line in mycheck_output(["/sbin/ifconfig"]).split("\n"):
        m = re.match('\s*inet addr:(.*?) .*', line)
        if m:
            print "    http://" + m.group(1) + ":" + str(parms.myport) + "/"
    app.run(
      host ="0.0.0.0",
      port = parms.myport,
      debug = parms.dbgFlag,
      use_reloader=False
     )

if __name__ == "__main__":
   db.create_all()
   main(sys.argv[1:])
else:
    setup_app(parms)
