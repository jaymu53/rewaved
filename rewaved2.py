import uuid
import cgi
import datetime
import urllib
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os


#Creates a string that can be inputed into the html() function which will appear in the body of the compose page

def composeString():
	return """
		<div>Create a Wave, we'll give you a code and you can share it with Your Friends!!</div>
        	
		Subject:
                <form action="/compose" method="post">
                <div style = "width: 100%; height: 5%;"><textarea name="subject" rows="150" cols="200" style="width: 130%; height: 90%;"></textarea></div>
		<div><input type="submit" value="Create Wave"></div>
                </form>

"""
#Creates a string that can be inputed into the html() function which will appear in the body of the find page

def findString():
        return """
                <div>Find a wave and join the conversation!!</div>
                
                Waveid:
                <form action="/find" method="post">
                <div style = "width: 100%; height: 5%;"><textarea name="code" rows="150" cols="200" style="width: 130%; height: 90%;"></textarea></div>
                <div><input type="submit" value="Find Wave"></div>
                </form>

"""



#The main html code, that serves as the body for all the pages, takes the users nickname and inserts into top right corner and content which it displays in its body
#Part of the code was taken from the twitter bootstrap project on github
def html(nickname, content):
	return """
<head>
<link rel="stylesheet" href="http://twitter.github.com/bootstrap/1.4.0/bootstrap.min.css">
</head>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
   <title>Rewaved</title>
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le HTML5 shim, for IE6-8 support of HTML elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

<!-- Le styles -->
    <link href="../1.3.0/bootstrap.css" rel="stylesheet">
    <style type="text/css">
      /* Override some defaults */
      html, body {
        background-color: #eee;
      } 
      body {
        padding-top: 40px; /* 40px to make the container go all the way to the bottom of the topbar */
      }   
      .container > footer p { 
       text-align: center; /* center align it with the container */
      }
      .container {
        width: 820px; /* downsize our container to make the content feel a bit tighter and more cohesive. NOTE: this removes two full columns from the grid, meaning you only go to 14 columns and not 16. */
      }
    
      /* The white background content wrapper */ 
      .content {
        background-color: #fff;
        padding: 20px;
       margin: 0 -20px; /* negative indent the amount of the padding to maintain the grid system */
        -webkit-border-radius: 0 0 6px 6px;
           -moz-border-radius: 0 0 6px 6px;
                border-radius: 0 0 6px 6px;
-webkit-box-shadow: 0 1px 2px rgba(0,0,0,.15);
           -moz-box-shadow: 0 1px 2px rgba(0,0,0,.15);
                box-shadow: 0 1px 2px rgba(0,0,0,.15);
      }

      /* Page header tweaks */
      .page-header {
        background-color: #f5f5f5;
        padding: 20px 20px 10px;
        margin: -20px -20px 20px;
      }

      /* Styles you shouldn't keep as they are for displaying this base example only */
      .content .span10,
      .content .span4 {
        min-height: 500px;
      }
      /* Give a quick and non-cross-browser friendly divider */
      .content .span4 {
        margin-left: 0;
        padding-left: 19px;
        border-left: 1px solid #eee;
      }

      .topbar .btn {
        border: 0;
      }
#sidebar{float:left;margin-top:165px;}
#sidebar p{margin-bottom: 11px !important;}
    </style>

<link rel="shortcut icon" href="images/favicon.ico">
    <link rel="apple-touch-icon" href="images/apple-touch-icon.png">
    <link rel="apple-touch-icon" sizes="72x72" href="images/apple-touch-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="114x114" href="images/apple-touch-icon-114x114.png">
  </head>
<div id = "sidebar">
          <ul>
              <p><a href = "/"    class="btn primary large">Inbox</a></p>
              <p><a href = "/compose"  class="btn primary large">Compose</a></p>
              <p><a href = "/find" class="btn primary large">Find</a></p>
          </ul>
      </div>


  <body>

    <div class="topbar">
      <div class="topbar-inner">
        <div class="container-fluid">
          <a class="brand" href="/">Rewaved</a>
          <ul class="nav">
            <li class="active"><a href="/">Home</a></li>
          </ul>
          <p class="pull-right">Logged in as""" + nickname + """ </a></p>
        </div>
      </div>
    </div>
<div class="container" style = "margin-top: 50px;">

      <div class="content">
        <div class="page-header">
        </div>
        <div class="row">
          <div class="span10" style="width: 100%; height:100%;">
	<p style=\"text-align: center; color: #000000; font-size: 3em\">""" + content + """</p>
      </div>


    </div> <!-- /container -->
 </body>


</html>
"""


#Creates a class Wave, which maps a unique waveid to a subject of the wave
class Wave(db.Model):
        waveid = db.StringProperty()
        subject = db.StringProperty()


#the message class models a message with author, content, the time and unique waveid
class Message(db.Model):
        author = db.StringProperty()
        content = db.StringProperty(multiline=True)
        dateTime = db.DateTimeProperty(auto_now_add=True)
        waveid = db.StringProperty()

#This displays the main page mapped to the url "/". It displays all the waves in which the current user jas authored a message
class MainPage(webapp.RequestHandler):
    def get(self):

        user = users.get_current_user() # gets the current user, signed in with a google account

        if user:
            self.response.headers['Content-Type'] = 'text/html'
	    #queries the Message instances for which the current user is an author
	    query = db.GqlQuery("SELECT * FROM Message WHERE author = :author", author = str(user.nickname()))
	    waves = [] #list of all the waves the current user is a part of, the for loop fills this list
	    newString = ""
	    for q in query:
		if q.waveid not in waves:
			waves.append(q.waveid)
	    for w in waves:
		#creates a link for every waveid that appears in waves
	     	newString += "<a href=\""+"/messages?id="+w+"\">"+w+"</a><br/>"
 
		
            #writes the html code
            self.response.out.write(html(str(user.nickname()), newString))
        else:
            self.redirect(users.create_login_url(self.request.uri))




#this class is mapped to the url "/compose". 
class ComposePage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
	    self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(html(str(user.nickname()), composeString()))

        else:
            self.redirect(users.create_login_url(self.request.uri))
    def post(self):
	user = users.get_current_user()
	
        if user:
            self.response.headers['Content-Type'] = 'text/html'
	    subject = cgi.escape(self.request.get('subject'))
	    newWave = Wave() #creates a new instance of the wave class
	    newWave.waveid = uuid.uuid4().hex # creates a unique waveid- 32 character hexadecimal string. 16^32 possibilities
	    
	    newWave.subject = subject
	    newWave.put() #stores the wave instance in the database
	    
	    self.response.out.write(html(str(user.nickname()), newWave.waveid))
	else:
            self.redirect(users.create_login_url(self.request.uri))

	
#maps to the url "/find". Finds a waveid if searched by the user
class FindPage(webapp.RequestHandler):
    def get(self):
	user = users.get_current_user()
	if user:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(html(str(user.nickname()),findString()))
	else:
            self.redirect(users.create_login_url(self.request.uri))
    def post(self):
	user = users.get_current_user()

        if user:
            self.response.headers['Content-Type'] = 'text/html'
	    #cgi gets the input from the user
	    waveID = cgi.escape(self.request.get('code'))
	    #returns an object of the wave class (get())
	    query = db.GqlQuery("SELECT * FROM Wave WHERE waveid = :waveid", waveid = waveID).get()
	    if query != None:
	    	self.redirect('/messages?id=' + waveID)
	    else:
		self.redirect('/find')

        else:
            self.redirect(users.create_login_url(self.request.uri))


#maps to the url "/message" and displays the messages
class MessagePage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
	     		self.response.headers['Content-Type'] = 'text/html'
			waveID = self.request.get("id") #gets the waveid from the url after id=
			#this query is used to get the subject, since we already know the waveid
			query = db.GqlQuery("SELECT * FROM Wave WHERE waveid = :waveid", waveid = waveID).get()
			#queries the messages and gets all the messages with the same waveid in ascending order by time
			messages = db.GqlQuery("SELECT * FROM Message WHERE waveid = :waveid ORDER BY dateTime ASC", waveid = waveID)
			newString = "" #stores the messages which is inputed into the html function
			
			if messages != None:
				for message in messages:
					newString += "<div style=\"color: red;\">%s wrote:</div><br/>" % (message.author)
					newString += "<div style=\"color: blue;\"><p style=\"word-wrap:break-word;\">%s</p></div><br/>" % (message.content)

			 
			a = query.subject + newString + """ 
			
                	<form action="/messages" method="post">
                	<div style = " width: 100%; height: 25%;"><textarea name="message" rows="1200" cols="200" style="width: 100%; height: 90%;"></textarea></div>
			<div style = 'display: none;'><textarea name="message_id">""" + waveID + """</textarea></div>
                	<div style="margin-top: 50px;"><input type="submit" value="Send Message"></div>
			</form>
			"""
			self.response.out.write(html(str(user.nickname()),a))
		else:
        	        self.redirect(users.create_login_url(self.request.uri))
	
	def post(self):
		user = users.get_current_user()
                if user:
                        self.response.headers['Content-Type'] = 'text/html'
			newMessage = Message() #creates an instance of the message class and stores that information in the database
			newMessage.author = str(user.nickname())
			newMessage.content = cgi.escape(self.request.get('message'))
			newMessage.waveid = cgi.escape(self.request.get('message_id'))
			newMessage.put()
			self.redirect('/messages?id='+newMessage.waveid) #redirects to the same page	

		else:
                        self.redirect(users.create_login_url(self.request.uri))




#maps the urls to their respective classes
application = webapp.WSGIApplication(
                                     [('/', MainPage),("/compose", ComposePage), ("/find", FindPage),("/messages", MessagePage)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

