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

The purpose of these visualisations is to support exploratory comparison between two PM2.5 datasets. Since WUSTL and WRF-Chem are generated using different modelling approaches, their estimates can vary across space. These HTML outputs make those differences easier to inspect both visually and quantitatively.

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
