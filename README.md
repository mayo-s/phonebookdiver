# Phone Book Diver  
### Visualizing phonebook data
 
The project The Phone Book Diver provides several tools to analyze and visualize data from 25 years of public German telephone books. These tools can be used to display the distribution of names on a heatmap, search and merge the data across multiple editions, and perform further analysis using a Jupyter Notebook.

## Thank you
Special credits to Prof. Weber-Wulff of the University of Applied Sciences Berlin and Erdgeist for the project support and the provision of the telephone book data.

## License
Unless otherwise stated, this project is licensed under CC-BY 4.0.

## Setup instructions  
(using terminal - follow on your own risk ;-) )  
  
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

In the project directory, you can run:

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

### `npm test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: https://facebook.github.io/create-react-app/docs/code-splitting

### Analyzing the Bundle Size

This section has moved here: https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size

### Making a Progressive Web App

This section has moved here: https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app

### Advanced Configuration

This section has moved here: https://facebook.github.io/create-react-app/docs/advanced-configuration

### Deployment

This section has moved here: https://facebook.github.io/create-react-app/docs/deployment

### `npm run build` fails to minify

This section has moved here: https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify
