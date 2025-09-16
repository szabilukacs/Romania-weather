# Romania-weather
[![Python CI](https://github.com/szabilukacs/Romania-weather/actions/workflows/python-tests.yml/badge.svg)](https://github.com/szabilukacs/Romania-weather/actions/workflows/python-tests.yml)
![Docker](https://img.shields.io/badge/docker-build-blue?logo=docker)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue?logo=python)
![Postgres](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)

![Tests](https://img.shields.io/badge/tests-passing-brightgreen?logo=pytest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Lint](https://img.shields.io/badge/lint-flake8-blue)](https://flake8.pycqa.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


---

## 📌 Overview

**Romania-weather** is a **data engineering learning project**, built to practice modern ETL pipelines and later extend to **cloud deployment**.  

The goal is to simulate a real-world scenario:
- Extract weather data from the [Meteostat API](https://dev.meteostat.net/).  
- Store both **historical** and **fresh/current** weather data from all meteorological stations in Romania.  
- Load the data into a **PostgreSQL database**.  
- Provide an **interactive Streamlit dashboard** to explore, summarize, and visualize the results.  

This project demonstrates **ETL pipelines, orchestration, containerization, and visualization**.

---

## 🎯 Motivation & Learning Goals

- Learn how to build **end-to-end ETL pipelines**.  
- Practice **containerization with Docker**.  
- Work with **relational databases (PostgreSQL)** in a production-like setup.  
- Explore **Airflow** for workflow orchestration.  
- Experiment with **PySpark** for scalable data processing.  
- Eventually deploy to **cloud platforms (AWS/GCP/Azure)**.  

This project is **not just about weather data** – it’s about practicing the **core skills of a data engineer**.

---

## 🚀 Features

- ✅ **Historical data ingestion** → Load all past weather data for Romania’s stations.  
- ✅ **Incremental updates** → Periodically fetch and append new weather observations.  
- ✅ **PostgreSQL integration** → Data stored in structured, queryable format.  
- ✅ **Streamlit dashboard** → Visualize trends, statistics, and comparisons.  
- ✅ **Dockerized setup** → Reproducible environment for local development.  
- 🔜 **Airflow DAGs** → Orchestrate historical + current data pipelines.  
- 🔜 **PySpark refactor** → Transform data with distributed processing.  
- 🔜 **Cloud deployment** → Run pipelines and dashboard in the cloud.  

---

## 🏗️ Architecture

- **main.py** → One-time job for historical data.  
- **current_data.py** → Scheduled job for fresh data.  
- **dashboard/app.py** → Streamlit dashboard to explore results.  

---

# 🖼️ Screenshots (Streamlit App)

Below are a few screenshots of the **Streamlit dashboard**.  
These demonstrate how historical and current weather data are displayed, compared, and summarized.

👉 Note: In the `constants.py` file you can configure which regions are included.  
For the examples below, only the **Hargita** region was selected.

---

### 🌦 Station Selection Dropdown
Romania Map with selected meteo stations.

![Map with current data](https://github.com/szabilukacs/Romania-weather/tree/main/img/map.png)

---

### 📈 Historical vs Current Weather
Monthly comparison of past trends with the latest fetched data.

![Historical vs Current](https://github.com/szabilukacs/Romania-weather/tree/main/img/monthly.png)

---

### 📊 Aggregated Statistics
Summaries such as averages, min/max values, and long-term weather patterns.

![Aggregated Stats](https://github.com/szabilukacs/Romania-weather/tree/main/img/yearly.png)


## 🔧 Tech Stack

- **Python 3.11+**  
- **PostgreSQL 15**  
- **Streamlit** (dashboard)  
- **Docker & Docker Compose** (containers)  
- **Airflow** (optional, orchestration)  
- **PySpark** (optional, scalable ETL)  

---

# 📅 Roadmap

- [x] Add data quality checks before loading  
- [x] Deploy to a cloud environment (AWS / GCP / Azure)  
- [x] Integrate with PySpark for scalable transformations  
- [ ] Add Airflow DAGs for production scheduling  
- [ ] Extend dashboard with forecasting models  
- [ ] Add user authentication for dashboard access  

---

# 🛠 Development Notes

- Built with **Python**, **PostgreSQL**, and **Streamlit**  
- Uses **Meteostat API** for historical & **OpenWeatherMap API** for current weather data  
- ETL pipeline includes:  
  - Extract: fetch weather data for all stations in Romania  
  - Transform: clean & validate raw data  
  - Load: insert into Postgres with COPY and INSERT strategies  
- Dockerized setup for reproducible local environment  
- Airflow (Docker-based) used for scheduling and orchestration  

---

# 🎓 Learning Outcomes

This project is primarily educational, focusing on **Data Engineering** concepts:

- Designing ETL pipelines with Python & SQL  
- Working with **API data ingestion** (Meteostat)  
- Practicing **data validation & transformation**  
- Using **Docker & Docker Compose** for environment management  
- Setting up **Airflow** for scheduling workflows  
- Building dashboards with **Streamlit** for visualization  
- Preparing for **Cloud & Big Data tools** (PySpark, AWS/GCP/Azure)  



