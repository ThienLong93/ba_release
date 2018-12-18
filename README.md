# ba_release
This is the source code for the Bachelor Thesis: "An intuitive Scraper with Django and Scrapy"

At least Python 3.4 is needed for Scrapy. Python can be installed here: https://www.python.org/downloads/
After the installation Python should be included in PATH otherwise this should be done to enable "pip" in the command prompt.

Following the installation of Python, a virtual environment should be set up. 

This can be done with the following two commands: 

      pip install virtualenvwrapper -win

      mkvirtualenv <name>
      
After setting up the virtual environment all needed Python packages can be safely installed inside the environment:
    
      pip install django
    
      pip install selenium
    
      pip install Scrapy
    
      pip install scrapyd
    
      pip install scrapyd-api-client
    
      pip install uuid
    
      pip install pywin32
      
After all the preparations can the Webserver and Scrapy now start.
To do that, we need 3 commands prompts: 

      1 for running the server on port 8000, 

      1 for running scrapyd service on 6800 and 

      1 for deploying spiders to the scrapyd-service
      
Web server: The command prompt must be in the same directory as the manage.py file. After that the following command starts the webserver:

      python manage.py runserver
      
Scrapyd:  The command prompt must be in the directory of the Scrapy application. After that the following command starts the scrapyd-service:

      scrapyd
      
Deploying spiders to scrapyd: The command prompt must be in the directory of the Scrapy application. After that the following command will sign up a spider for scrapyd to use:

      scrapyd-client deploy
