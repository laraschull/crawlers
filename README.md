# crawlers

First time running
```
virtualenv venv

source venv/bin/activate
```
```
pip3 install --upgrade -r requirements.txt
```
or
```
pip3 install requirements.txt
```

When trying to run after first time
```
source venv/bin/activate
```
Make sure that Mongo db is installed, and the correct data/db folder is initialized on your machine.
This varies by operating system, but general tutorials online may help if you are unsure of how to do this on your OS


# To run code
First, run mongo db on your localhost port 27017 (this is the default port, simply run the mongo program executable)

Then, set the FLASK_APP variable to "searchAPI" and run flask
on Windows:
```
set FLASK_APP=searchAPI
flask run
```
on Mac:
```
export FLASK_APP=searchAPI.py
flask run
```

Now that you have both Flask and Mongo running, you should be able to connect to the API endpoint with the following request
```
http://localhost:5000/api/search?state=ga&last=smith&first=george
```
make sure to set the state parameter and the first and last name that you are interested in testing. The resulting JSON will be returned

# Basic workflow
1. First, create a new branch from master for you to work on
2. Then, duplicate the CrawlerTemplate.py file, and rename it StateSearch.py, where State is the name of the state you are working on
3. Then, go through the template file, configuring the commented-out variables to match the actual names of various html features in the database
  * This part requires the most work, as each website is different.
  * the GeorgiaSearch.py file is the most complete example that we have at the moment. Use this as a model
4. Once you have configured all the fields to extract the inmate, record, and facility information, then you can write test cases in the testing.py file. (This has not yet merged to master, as I am still debugging the test process, so don't worry about this step at the moment)
5. Submit a pull request to merge the new searcher, and any changes that you needed to make to the models or utils files, back into master.
6. Notify the team of changes madel to models or util.
