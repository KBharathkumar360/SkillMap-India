import plotly.express as px
import streamlit as st
import pandas as pd
import altair as alt
import ast

st.set_page_config(page_title="SkillMap India", page_icon=":briefcase:", 
                   layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_data(file_path_csv, file_path_txt):
    try:
        combined_df = pd.read_csv(file_path_csv)
        with open(file_path_txt, 'r') as file:
            valid_skills = file.read().splitlines()
        return combined_df, valid_skills
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def preprocess_data(df):
    try:
        df.dropna(subset=['Job Category', 'Location'], inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        df['Location'] = df['Location'].replace({
            'Jammu & Kashmir': 'Jammu and Kashmir',
            'Odisha': 'Orissa',
            'Uttarakhand': 'Uttaranchal',
        })
        df['Employment Type'] = df['Employment Type'].astype(str).str.lower()
        for col in ['Job Count', 'Skill Count']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Error preprocessing data: {e}")
        return pd.DataFrame()

def preprocess_skills(skills):
    if pd.isna(skills):
        return []
    try:
        skills_list = ast.literal_eval(skills)
        if isinstance(skills_list, list):
            return [skill.strip().lower() for skill in skills_list]
    except ValueError:
        return [skill.strip().lower() for skill in skills.split(',')]
    return []

def merge_location_data(df, column_name, states_df):
    location_counts = df['Location'].value_counts().reset_index()
    location_counts.columns = ['Location', column_name]
    location_counts = pd.merge(states_df[['Location']], location_counts, on='Location', how='left').fillna(0)
    location_counts[column_name] = location_counts[column_name].astype(int)
    return location_counts[location_counts['Location'] != 'Remote']

def adjust_color_intensity(scale, intensity):
    color_schemes = {
        'Reds': ['#ffcccc', '#ff9999', '#ff6666', '#ff3333', '#ff0000', '#cc0000', '#990000'],
        'Blues': ['#cceeff', '#99ddff', '#66ccff', '#33bbff', '#00aaff', '#0088cc', '#006699'],
        'Greens': ['#ccffcc', '#99ff99', '#66ff66', '#33ff33', '#00ff00', '#00cc00', '#009900'],
        'Purples': ['#f3e5f5', '#e1bee7', '#ce93d8', '#ba68c8', '#ab47bc', '#8e24aa', '#6a1b9a'],
        'Oranges': ['#ffe0b2', '#ffcc80', '#ffb74d', '#ffa726', '#ff9800', '#fb8c00', '#ef6c00'],
        'Teals': ['#e0f7fa', '#b2ebf2', '#80deea', '#4dd0e1', '#26c6da', '#00acc1', '#00838f'],
        'Yellows': ['#fff9c4', '#fff59d', '#fff176', '#ffee58', '#ffeb3b', '#fdd835', '#fbc02d'],
        'Pinks': ['#f8bbd0', '#f48fb1', '#f06292', '#ec407a', '#e91e63', '#d81b60', '#c2185b'],
        'Browns': ['#d7ccc8', '#bcaaa4', '#a1887f', '#8d6e63', '#795548', '#6d4c41', '#5d4037'],
        'Grays': ['#f5f5f5', '#eeeeee', '#e0e0e0', '#bdbdbd', '#9e9e9e', '#757575', '#616161']
    }
    return color_schemes[scale][:intensity + 1]

def generate_heatmap(data, column_name, title):
    heatmap = alt.Chart(geojson_data).mark_geoshape().encode(
        color=alt.Color(f'{column_name}:Q', scale=alt.Scale(range=adjust_color_intensity(color_scheme, heatmap_intensity))),
        tooltip=[alt.Tooltip('properties.NAME_1:N', title='Location'), 
                 alt.Tooltip(f'{column_name}:Q', title=column_name)]
    ).transform_lookup(
        lookup='properties.NAME_1',
        from_=alt.LookupData(data, 'Location', [column_name])
    ).properties(
        title=title,
        width=800,
        height=600
    ).project(type='mercator')
    return heatmap

file_path_csv = 'Job Clusters.csv'
file_path_txt = 'Data_Job_Skillsets.txt'
combined_df, valid_skills = load_data(file_path_csv, file_path_txt)
if combined_df is not None:
    combined_df = preprocess_data(combined_df)
    combined_df['Skills'] = combined_df['Skills'].apply(preprocess_skills)

# Constants
all_states = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa',
    'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
    'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland',
    'Orissa', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttaranchal', 'West Bengal', 'Jammu and Kashmir', 'Ladakh',
    'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
    'Lakshadweep', 'Delhi', 'Puducherry'
]
all_states_df = pd.DataFrame(all_states, columns=['Location'])
all_states_df['Job Count'] = 0
all_states_df['Skill Count'] = 0

# GeoJSON data
india_states_url = 'https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson'
geojson_data = alt.Data(url=india_states_url, format=alt.DataFormat(property='features', type='json'))

# Sidebar Navigation
st.sidebar.header('Navigation')
nav_items = [
    (":bar_chart: Job Distribution", "job-distribution"),
    (":hammer_and_wrench: Skill Distribution", "skill-distribution"),
    (":earth_asia: Regional Employment Trends", "regional-employment-trends"),
    (":deciduous_tree: :world_map: Skills Treemap", "skills-treemap"),
    (":top: Top Companies Hiring", "top-companies-hiring"),
]

if 'selected_page' not in st.session_state:
    st.session_state.selected_page = nav_items[0][1]

for label, key in nav_items:
    if st.sidebar.button(label, key=key):
        st.session_state.selected_page = key

# Additional customization options in sidebar
st.sidebar.header('Customization')
heatmap_intensity = st.sidebar.slider('Adjust Heatmap Color Intensity:', min_value=0, max_value=10, value=5)
color_scheme = st.sidebar.selectbox(
    'Select Chart Color Scheme:', 
    ['Reds', 'Blues', 'Greens', 'Purples', 'Oranges', 'Teals', 'Yellows', 'Pinks', 'Browns', 'Grays'], 
    key='color_scheme'
)

selected_page = st.session_state.selected_page

def job_distribution(df, states_df):
    st.header('Job Distribution')
    job_roles = df['Job Category'].unique()
    selected_job_role = st.selectbox('Select a Job Role:', job_roles)
    with st.spinner('Loading, please wait...'):
        filtered_df = df[df['Job Category'] == selected_job_role]
        total_count = len(filtered_df)
        st.write(f"Total {selected_job_role} Job Postings in India: {total_count}")
        location_counts = merge_location_data(filtered_df, 'Job Count', states_df)
        heatmap = generate_heatmap(location_counts, 'Job Count', f'Job Distribution for {selected_job_role} Across India')
        st.altair_chart(heatmap, use_container_width=True)

def skill_distribution(df, valid_skills, states_df):
    st.header('Geographical Skill Demand Map')
    selected_skills = st.multiselect('Select Skills:', valid_skills)
    if selected_skills:
        with st.spinner('Loading, please wait...'):
            skill_filtered_df = df[df['Skills'].apply(lambda x: any(skill in x for skill in selected_skills))]
            skill_location_counts = merge_location_data(skill_filtered_df, 'Skill Count', states_df)
            skill_heatmap = generate_heatmap(skill_location_counts, 'Skill Count', f'Skill Distribution for {", ".join(selected_skills)} Across India')
            st.altair_chart(skill_heatmap, use_container_width=True)
    else:
        st.write("Please select at least one skill to view the distribution map.")

def regional_employment_trends(df, states_df):
    st.header('Regional Employment Trends')
    employment_types = ['full-time', 'part-time', 'contract']
    with st.spinner('Loading, please wait...'):
        employment_data = df[df['Employment Type'].isin(employment_types)]
        employment_counts = employment_data.groupby(['Location', 'Employment Type']).size().reset_index(name='Count')
        for employment_type in employment_types:
            employment_type_data = employment_counts[employment_counts['Employment Type'] == employment_type]
            employment_type_data = pd.merge(states_df[['Location']], employment_type_data, on='Location', how='left').fillna(0)
            employment_type_data['Count'] = employment_type_data['Count'].astype(int)
            employment_chart = generate_heatmap(employment_type_data, 'Count', f'Employment Type: {employment_type.capitalize()} Across India')
            st.altair_chart(employment_chart, use_container_width=True)
        industries = df['Industries'].dropna().unique()
        selected_industry = st.selectbox('Select an Industry:', industries)
        industry_data = df[df['Industries'] == selected_industry]
        industry_counts = merge_location_data(industry_data, 'Count', states_df)
        industry_chart = generate_heatmap(industry_counts, 'Count', f'Job Trends for {selected_industry} Industry Across India')
        st.altair_chart(industry_chart, use_container_width=True)

def skills_treemap(df, valid_skills):
    st.header('Skills Treemap')
    problematic_schemes = ['Teals', 'Yellows', 'Pinks', 'Browns', 'Grays']
    
    if color_scheme in problematic_schemes:
        st.error(f"""The selected color scheme '{color_scheme}' is not supported for this chart. 
                 Please select only Reds, Blues, Greens, Purples, or Oranges for this chart.""")
        return
    
    with st.spinner('Loading, please wait...'):
        skills_expanded_df = df.explode('Skills')
        skills_expanded_df = skills_expanded_df[skills_expanded_df['Skills'].isin(valid_skills)]
        skills_expanded_df.dropna(subset=['Skills'], inplace=True)
        skill_counts = skills_expanded_df['Skills'].value_counts().reset_index()
        skill_counts.columns = ['Skill', 'Count']

        fig = px.treemap(skill_counts, path=['Skill'], values='Count', title='Distribution of in Demand Skills')
        fig.update_traces(
            marker=dict(colorscale=color_scheme, cmid=0.5),
            hovertemplate='<b>Skill:</b> %{label}<br><b>Count:</b> %{value}',
            texttemplate="<b>%{label}</b>",
            textfont=dict(size=14)
        )
        fig.update_layout(
            margin=dict(t=50, l=25, r=25, b=25),
            title_font_size=20,
            title_x=0.5,
            width=1500, 
            height=600  
        )

        st.plotly_chart(fig, use_container_width=True)

def top_companies_hiring(df):
    st.header('Top Companies Hiring')
    with st.spinner('Loading, please wait...'):
        job_roles = df['Job Category'].unique()
        selected_job_role = st.selectbox('Select a Job Role:', job_roles, key='top_companies_job_role')
        locations = ['All States'] + df['Location'].unique().tolist()
        selected_location = st.selectbox('Select a Location:', locations, key='top_companies_location')
        
        if selected_location == 'All States':
            filtered_df = df[df['Job Category'] == selected_job_role]
        else:
            filtered_df = df[(df['Job Category'] == selected_job_role) & (df['Location'] == selected_location)]
        
        top_companies = filtered_df['Company Name'].value_counts().reset_index()
        top_companies.columns = ['Company Name', 'Job Count']
        top_companies = top_companies.head(20)
        
        total_jobs = top_companies['Job Count'].sum()
        top_companies['Percentage'] = (top_companies['Job Count'] / total_jobs * 100).round(1).astype(str) + '%'
        
        colors = adjust_color_intensity(color_scheme, heatmap_intensity)
        
        bar_chart = alt.Chart(top_companies).mark_bar(cornerRadius=5).encode(
            x=alt.X('Job Count:Q', title='Job Count'),
            y=alt.Y('Company Name:N', sort='-x', title='Company Name'),
            color=alt.Color('Job Count:Q', scale=alt.Scale(domain=[top_companies['Job Count'].min(), top_companies['Job Count'].max()], range=colors), legend=None),
            tooltip=['Company Name', 'Job Count', 'Percentage']
        )
        
        text = bar_chart.mark_text(
            align='left',
            baseline='middle',
            dx=5,  
            fontSize=18,
            fontWeight='bold',
            color='white'
        ).encode(
            text='Percentage'
        )

        combined_chart = (bar_chart + text).properties(
            title=f'Top Companies Hiring for {selected_job_role} in {selected_location}',
            width=1000,  
            height=1000
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14,
            grid=False  
        ).configure_title(
            fontSize=16,
            anchor='middle'
        )

        st.altair_chart(combined_chart, use_container_width=True)

def main():
    if selected_page == "job-distribution":
        job_distribution(combined_df, all_states_df)
    elif selected_page == "skill-distribution":
        skill_distribution(combined_df, valid_skills, all_states_df)
    elif selected_page == "regional-employment-trends":
        regional_employment_trends(combined_df, all_states_df)
    elif selected_page == "skills-treemap":
        skills_treemap(combined_df, valid_skills)
    elif selected_page == "top-companies-hiring":
        top_companies_hiring(combined_df)

if __name__ == '__main__':
    main()
