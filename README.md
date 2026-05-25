# PM2.5 Delta Dashboard: WUSTL vs WRF-Chem

This repository contains two HTML visualisations created for my independent study project on **Computational Air Quality Modelling**. The goal is to compare PM2.5 estimates from the **WUSTL** dataset and the **WRF-Chem** dataset over Delhi/North India.

## Files

### 1. Interactive PM2.5 Map

This HTML file shows an interactive map of PM2.5 differences between WUSTL and WRF-Chem.

Each grid-cell popup shows:

- WUSTL PM2.5 value
- WRF-Chem PM2.5 value
- Delta value: `WUSTL - WRF-Chem`
- Percentage difference
- Distance to the nearest WRF-Chem point

This map helps visually inspect where the two datasets differ spatially.

### 2. PM2.5 Delta Analysis Charts

This HTML file contains summary charts comparing WUSTL and WRF-Chem PM2.5 values.

The charts include:

- WUSTL vs WRF-Chem scatter plot
- Distribution of delta values
- Delta by region boxplot
- Mean delta by region

These charts help summarise whether one dataset is consistently estimating higher or lower PM2.5 values.

## Purpose

I essentially developed this to compare pollution estimates from the WUSTL and WRF-Chem datasets over Delhi. The purpose of this pipeline was to move beyond simply plotting the datasets separately and instead create a systematic way to evaluate how differently the two sources estimate PM₂.₅ over the same region.

The pipeline first loads and cleans the WUSTL monthly PM₂.₅ dataset and the WRF-Chem 2017 dataset. Since the original WRF-Chem file covers a larger spatial extent, it is cropped to an approximate Delhi bounding box so that the comparison remains focused on the study area. The WRF-Chem data is then aggregated by month and grid location to make it comparable with the monthly WUSTL values.

A key challenge was that WUSTL and WRF-Chem do not share identical grid structures. To address this, I used a nearest-neighbour spatial matching approach. For each month, every WUSTL point was matched to the nearest WRF-Chem grid point within a defined distance threshold. This allowed the two datasets to be compared at approximately corresponding spatial locations rather than being treated as unrelated layers.

After matching the datasets, the pipeline calculates the difference between them as:

Δ = WUSTL PM₂.₅ − WRF-Chem PM₂.₅

It also calculates the absolute difference, percentage difference, and distance to the nearest WRF-Chem grid point. These values help quantify whether WUSTL is consistently estimating higher or lower PM₂.₅ than WRF-Chem, and whether the difference appears systematic or scattered across space.

The pipeline then produces two main outputs. First, it generates an interactive HTML map where WRF-Chem grid cells are shown alongside matched WUSTL points. Each point is coloured by the delta value, making it easy to identify where WUSTL estimates are higher or lower than WRF-Chem. The popup for each point displays the WUSTL value, WRF-Chem value, delta, percentage difference, and nearest-neighbour distance. Second, the pipeline generates chart-based summaries, including a WUSTL vs WRF-Chem scatter plot, a histogram of delta values, a boxplot of delta by region, and a mean delta chart. Together, these outputs make the comparison both spatial and quantitative.

## How to View

1. Download or clone this repository.
2. Open the HTML files in a web browser such as Chrome, Edge, or Firefox.
3. No additional installation is required.

## Tools Used

Python
Pandas / GeoPandas
Plotly
Folium / Leaflet
QGIS
WUSTL PM2.5 data
WRF-Chem PM2.5 data


# BreatheSafe: Pollution-Aware Mobility Dashboard (Version 1)

BreatheSafe is a frontend prototype dashboard designed to show how pollution data can support healthier and more conscious everyday mobility decisions. The dashboard is built from the user’s point of view and focuses on how pollutant markers can be translated into simple warnings, mobility scores, and practical route choices.
This dashboard was built in collaboration with Mrinalini Jindal and Mihika Grover, with the assistance of ChatGPT.

## Project Objective

The objective of this prototype is to demonstrate how an air-pollution dashboard could look and feel before building a complete backend system. Instead of focusing on database architecture, this version prioritizes the frontend experience, user interaction, and practical usefulness.

The dashboard explores how individual pollutant markers can inform better mobility and more conscious everyday living from both a health and practical standpoint.

## Core Idea

Air pollution is often presented as raw data, which may not be immediately useful for everyday users. This dashboard essentially attempts to convert pollution-related information into clear, actionable insights.

For example, instead of only showing pollutant values, the dashboard helps users understand:

- whether it is safe to walk, cycle, or drive
- which route may be healthier
- which pollutant is contributing most to poor air quality
- what level of caution is needed
- how mobility choices can change based on pollution exposure

## Key Features

### 1. Pollution Overview

The dashboard presents a simple pollution status summary using assumed real-time values. These values represent common pollutant markers such as PM2.5, PM10, NO2, SO2, CO, and O3.

### 2. Mobility Score

A mobility score is included to help users quickly understand whether outdoor movement is advisable. The score translates pollution data into a user-friendly mobility recommendation.

### 3. Pollutant-Marker Explanation

The dashboard includes explanations of individual pollutant markers so users can understand what each pollutant means and why it matters. This helps connect raw environmental data with everyday health decisions.

### 4. Health and Practical Warnings

The dashboard provides warning-style messages to guide users in simple language. These warnings are meant to be understandable even for a non-technical user.

### 5. Route and Mobility Use Case

The prototype imagines how pollution insights could be integrated into mobility decisions, such as choosing whether to walk, cycle, take public transport, or use an alternate route.

## How to View the Dashboard
Click on "dashboard_version_1(2).html" and download the file in order to view it.

# AirWatch Dashboard (Version 2)

AirWatch is a static HTML dashboard prototype that shows how air pollution information can be presented in a simple, user-friendly way. It focuses on AQI, pollutant levels, health warnings, commute exposure, and nearby pollution hotspots. 
This dashboard was built in collaboration with Mrinalini Jindal and Mihika Grover, with the assistance of Claude.

## Objective

The goal is to test the frontend design and usefulness of a pollution dashboard from the user’s point of view before building a full backend system.

## Features

- Current AQI overview
- Pollutant breakdown: PM2.5, PM10, NO2, CO, O3, and SO2
- Nearby pollution hotspots
- Commute exposure guide
- Health recommendations
- Best times to go outside
- Seven-day air quality forecast


## How to View the Dashboard
Click on "dashboard_version_2.html" and download the file in order to view it.
