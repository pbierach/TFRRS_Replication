# TFRRS_Replication
  Patrick Bierach (Ithaca College '24)

# About 
Python code to replicate the underlying database used on the TFFRS.org website. 
TFFRS.org is a website that hosts collegiate cross country and track-and-field results going back to the early 2010s. 

# Technology Used
  - Python3
    - Selenium
    - BeautifulSoup4
  - SQL
  - JSON
  
# Additional Information
This was a final project for Ithaca College's databases class (COMP375). The purpose of the project was to reverse engineer the database used by TFRRS.org. The code for this project is split into two python files: one dedicated to scraping certain TFFRS.org pages and another to normalizing and inserting the data into a SQL database. Selenium and BeuatifulSoup were utilized for webscraping and the contents of the scrape were stored in JSON files. The data was normalized and inserted into a SQL database hosted by GoogleCloudServices. 

A link to the project poster: https://docs.google.com/presentation/d/1P8yPdcQ5fzVDgG7VSmjHE-_UWwiM5lJ6hsd9K6a3UEM/edit?usp=sharing

# Future Work
As it stands, the database table linking athletes to their individual results remains unpopulated. The method for that in the 'normalize_to_sql.py' file is implemented, but has not yet been run. 

# Contact
For any additional questions please email me at: pbierach@ithaca.edu
