# SIDC-HDSS

SIDC-HDSS is a system application with features designed to aid Sorosoro Ibaba Development Cooperative with farm biosecurity management, hogs health monitoring, disease monitoring, and decision support for their farms in Batangas, Philippines. The system is intended to address the problem of SIDC in its decrease of shared profit with its members. This is due to one of their biggest threats today: hogs diseases such as African Swine Fever (ASF).

## System Modules

#### 1. Hog Farms Management
Performs data collection and management of farm records. Important features include management of internal and external biosecurity (i.e. creation, editing, and display of biosecurity checklists), recording of farm activities (e.g. inspection, monthly inventory, etc.), and sending of member announcements as SMS to the hog raisers.

#### 2. Hogs Health Analysis
Performs data collection and management of the hogs’ health records. Important features include symptoms monitoring wherein incident cases are recorded and monitored until there is a tentative diagnosis, and disease monitoring wherein confirmed cases are monitored and updated regularly. Diseases that are monitored through the system include frequent hog diseases that the organization encounters, which include: ASF, CSF, Swine Influenza, Pseudorabies, PRRS, and PED.

#### 3. Action Recommendation
Performs analysis of all data collected and managed in the previous modules to produce data visualization and descriptive reports. It also generates a disease intervention plan that will oversee all disease prevention and control initiatives. Important features include predictive analytics which uses the SEIRD model, and action recommendation in which directed action plans are stated according to current mortality rates, biosecurity rates, and SEIRD outputs.

> Throughout the three modules, the concepts of data management, disease triangle (environment, host, and agent), and disease surveillance are applied.

## System Architecture

| Web User Interface | Web Server | Web Application | Database |
| ------------------ | ---------- | --------------- | -------- |
| HTML 5, CSS 3, Javascript, Bootstrap, Highcharts | Nginx, uWSGI | Python, Django, OpenStreetMap, Geopandas | PostgreSQL, PostGIS |

## Installation and Running of Project
The Technical Manual and User Manual of this system are for client use only.

## Authors

Catahan, Anna Kumiko  
Go, Kurt Patrick  
Latorre, Kayla Dwynett  
Manzano, Ninna Robyn

> This is a Capstone Project that is in partial fulfillment of the requirements for the degree of Bachelor of Science in Information Systems
