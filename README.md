# Snowboard App

This project focuses on analyzing sports performance in alpine snowboarding, 
offering a unique approach by integrating competition results with historical weather data. 
By connecting these two data sources, it provides deeper insights into performance trends and external factors, pushing the boundaries of traditional sports analysis.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

## Try Here

Explore the live application now:

[**Access the demo**](https://snowboardapp.onrender.com)

## Features

**Comprehensive Data Collection**  
  Data was collected using a variety of methods, starting with web scraping from the official FIS (International Ski and Snowboard Federation) website for competition results. Weather data was then retrieved using the Meteostat API to add valuable context to the analysis.

**Data Cleaning and Integration**  
  The collected data was carefully filtered, and missing values were computed to ensure accuracy. Both datasets were merged and preprocessed to prepare them for seamless integration into the application.

**Interactive Dashboard Creation**  
  The application was built using a pandas Dash app, featuring multiple interactive elements such as graphs, information panels, and a control center. These components work together through a robust callback structure, ensuring a smooth and responsive user experience.

## Installation

Clone the repository and follow these steps      :

```bash
git clone https://github.com/otulach/AthleteApp.git
cd AthleteApp
pip install -r requirements.txt
python3 main.py
```

Then follow server's URL link and enjoy the app!
