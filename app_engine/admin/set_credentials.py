'''
Handler to set the credentials_repository for the chatbot Facebook account.
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import credentials_repository

class HandleCredentials(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    credentials = credentials_repository.UpdateCredentials(
        self.request.get('email'), self.request.get('password'),
        self.request.get('access_token'))

    self.response.out.write('== Credentials ==\nEmail: %s\nPassword: %s\nAccess Token: %s' % 
      (credentials.email, credentials.password, credentials.access_token))


def main():
  application = webapp.WSGIApplication([('/credentials', HandleCredentials)], debug=True)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
