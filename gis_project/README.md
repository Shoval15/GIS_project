# UrbanGreenSpace Analyzer

## Overview

UrbanGreenSpace Analyzer is an innovative decision support system for urban planning, focusing on the analysis and management of public open spaces (POS) in cities. This system addresses the growing challenge of efficient urban planning while meeting legal requirements for allocating open spaces to residents.

## Features

- Import and analyze precise geographical data
- Calculate real walking distances between buildings and public open spaces
- Automatically allocate buildings to POS considering capacity and distance constraints
- Interactive visualization of analysis results on a map
- Detailed statistics on POS accessibility in a selected area

## Technology Stack

- Backend: Python with Flask
- Frontend: React.js with Leaflet for interactive maps
- Data Processing: GeoPandas, Shapely, OSMNX
- Data Source: Jerusalem Municipality GIS system

## Installation

1. Clone the repository: https://github.com/Shoval15/GIS_project.git
2. Install backend dependencies: 
    cd gis_project/api
    pip install -r requirements.txt
3. Install frontend dependencies:
    cd ..
    npm install


## Usage

1. Start the backend server:
    cd gis_project/api
    python app.py
2. Start the frontend development server:
    cd ..
    npm start
3. Open your browser and navigate to `http://localhost:3000`

## API Endpoints

- `POST /api/bounds`: Analyze an area based on given bounds and parameters

## Testing

To run the tests:
    python -m unittest discover tests

## Acknowledgments And Idea

- Dr. Asaf Spanier for project guidance (JCE)
- Jerusalem Municipality for providing access to their GIS data
