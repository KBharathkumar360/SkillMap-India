# SkillMap India

![SkillMap India](https://github.com/KBharathkumar360/SkillMap-India/blob/main/Preview%20Image.png?raw=true)

[**SkillMap India - Live App**](https://skillmap-india-2chhyipaogaopx45mie3kh.streamlit.app/)

SkillMap India is a data visualization tool built with Streamlit that provides insights into job distribution, skill demands, and employment trends across different states of India. This tool is designed to help job seekers, employers, and policymakers make data-driven decisions by analyzing job market trends.

## 🚀 Features

- **Job Distribution Analysis**: Visualize the distribution of different job roles across Indian states.
- **Skill Demand Mapping**: Identify geographical areas with high demand for specific skills.
- **Regional Employment Trends**: Explore full-time, part-time, and contract employment trends across regions.
- **Skills Treemap**: Discover the most in-demand skills with an interactive treemap.
- **Top Companies Hiring**: Find out which companies are leading in job postings for specific roles and locations.

## 📊 Data Sources and Methodology

### Data Collection

- **Job_Clusters.csv**: This dataset was created by web scraping job posting data from LinkedIn, Glassdoor, and Indeed. Selenium was used to automate the scraping process.

### Data Processing

- **NLP for Skill Extraction**: Natural Language Processing (NLP) techniques were applied to extract the required skills from job descriptions (JDs). This involved identifying and standardizing the skill names mentioned in the job postings.
- The scraped data was cleaned and preprocessed before being grouped into **10 clusters** using the **K-Means** clustering algorithm.
- **Optimal Number of Clusters**: The optimal number of clusters was determined using the **Elbow Method** and the **Silhouette Score**, ensuring meaningful groupings of job roles.

### Skills Dataset

- **Data_Job_Skillsets.txt**: This file contains a list of valid skillsets associated with various job categories. The skills were standardized to ensure consistency and accuracy in analysis.

## 🛠️ Tech Stack

- **Streamlit**: For building the web application.
- **Pandas**: For data manipulation and analysis.
- **Plotly**: For interactive visualizations.
- **Altair**: For creating data-driven visualizations.
- **Selenium**: For web scraping data from job boards.
- **NLP**: For extracting and standardizing skills from job descriptions.
