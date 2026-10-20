# Phone Book Diver

### Visualizing phonebook data

The project The Phone Book Diver provides several tools to analyze and visualize data from 25 years of public German
telephone books. These tools can be used to display the distribution of names on a heatmap, search and merge the data
across multiple editions, and perform further analysis using a Jupyter Notebook.

## Thank you

Special credits to Prof. Weber-Wulff of the University of Applied Sciences Berlin and Erdgeist for the project support
and the provision of the telephone book data.

## License

Unless otherwise stated, this project is licensed under CC-BY 4.0.

## Setup instructions

(using terminal - follow on your own risk ;-) )

Python dependencies for api/, tools/ and jupyter/ are managed with [pipenv](https://pipenv.pypa.io) in a single
`Pipfile` at the project root.

(- install python 3.14 and pipenv if not already done `> brew install python@3.14 pipenv`)

- move to your project directory `> cd "path/projectName"`
- install dependencies for api/ and tools/ `> pipenv install --dev`
- additionally install the jupyter/ dependencies `> pipenv install --categories="packages notebook"`
- run a single command in the environment, e.g. `> cd tools && pipenv run python main.py`
- or open a shell within the environment `> pipenv shell` (leave it with `> exit`)

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

## Heatmap geocoding

Coordinates for the heatmap come from the `geodata` collection. Places not in there yet are looked up once
via [Nominatim](https://nominatim.org) (OpenStreetMap, at most one request per second) and saved.

New Nominatim results are checked for plausibility before they are saved. A result is rejected if it lies

- outside Germany, or
- more than 35 km away from the nearest known place with the same zip code (`MAX_KM_TO_SAME_ZIP` in
  `api/hm_requester.py`).

Rejected results and places Nominatim doesn't know are kept in `geodata_not_found` with a `reason` (and the rejected
coordinates), so they aren't requested again.

### Cleaning up existing geodata (`api/scripts/geodata_cleanup.py`)

The plausibility check only applies to new results. To find and fix wrongly geocoded entries already in `geodata`, run
the cleanup script from within `api/` (`> cd api`). It works in two steps:

1. **plan** – reads `geodata`, asks Nominatim for the centre of every suspicious zip code and writes a CSV plan. Nothing
   in the database is changed. Takes a while (one Nominatim request per second).
   `> pipenv run python -m scripts.geodata_cleanup plan --report geodata_cleanup_plan.csv`
2. **apply** – executes exactly the reviewed CSV, without new Nominatim requests.
   `> pipenv run python -m scripts.geodata_cleanup apply geodata_cleanup_plan.csv`

An entry counts as wrong if it lies more than 35 km from its zip code's centre. It is re-geocoded with zip code + city;
if the new result is close to the centre, the entry is updated, otherwise it is moved to `geodata_not_found` (with its
old coordinates).

Back up first, e.g. `> mongodump --db phonebookdiver --collection geodata --out <backup dir>`, and restore if needed
with `> mongorestore --drop --nsInclude 'phonebookdiver.geodata*' <backup dir>`.
