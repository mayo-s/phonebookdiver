# Phone Book Diver  
### Visualizing phonebook data
 
The project The Phone Book Diver provides several tools to analyze and visualize data from 25 years of public German telephone books. These tools can be used to display the distribution of names on a heatmap, search and merge the data across multiple editions, and perform further analysis using a Jupyter Notebook.

## Thank you
Special credits to Prof. Weber-Wulff of the University of Applied Sciences Berlin and Erdgeist for the project support and the provision of the telephone book data.

## License
Unless otherwise stated, this project is licensed under CC-BY 4.0.

## Setup instructions 
(using terminal - follow on your own risk ;-) )  

These steps must be performed separately for each tool.  
These folders are api/, jupyter/ and tools/.  
  
( - install python3 if not already done `> brew install python`)  
( - or upgrade current version `> brew upgrade python`)  
- move to your project directory `> cd "path/projectName"`  
- create virtual environment within project directory `> python3 -m venv .env --copies`  
- activate virtual environment `> source .env/bin/activate`  
- install requirements `> pip install -r requirements`  

- when done working - deactivate virtual environment `> deactivate`  



## React-App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

To start the project, in the project directory, run:

### `npm start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `npm run-script start-api`  
  
Runs the API for database requests  
Open [http://localhost:5000](http://localhost:5000) to view in browser.  
Examples for API requests:  
1. http://localhost:5000/search?collection=2020&key=lastname&value=Schmidt  
Used for Heatmap requests - will return a list of Latitude and Longitude  
2. http://localhost:5000/search?start=1990&end=2020&key=lastname&value=Schmidt  
Will return all entries within the search range (similar entries will appear once with list of appearance)  

