from models import db
from models import Topic

db.create_all()

topics = [
    {"name": "Python", "description": "Learn Python programming from basics to advanced."},
    {"name": "DSA", "description": "Practice Data Structures and Algorithms."},
    {"name": "Libraries", "description": "Explore libraries like Numpy, Pandas, Matplotlib, and more."},
    {"name": "Data Wrangling", "description": "Master data cleaning and preprocessing techniques."},
    {"name": "Statistics", "description": "Understand statistical concepts for data analysis."},
    {"name": "Probability", "description": "Dive into probability theory and its applications."},
    {"name": "Linear Algebra", "description": "Learn linear algebra for machine learning and data science."},
    {"name": "Calculus", "description": "Understand calculus concepts for optimization."},
    {"name": "Tableau", "description": "Learn Tableau for data visualization."},
    {"name": "Power BI", "description": "Master Power BI for business intelligence."},
    {"name": "Power Query", "description": "Master Power Query for Data Cleaning."},
    {"name": "Design Principles", "description": "Master Design Principles for creating professional dashboards."},
    {"name": "Interactive Dashboards", "description": "Learn how to create beautiful and informative data visualizations."},
    {"name": "D3.js ", "description": "Master D3.js for interactive visualizations."},
    {"name": "Plotly & Dash", "description": "Master Plotly and Dash"}
    # Add more topics here

]

for index, t in enumerate(topics):
    slug = t['name'].lower().strip().replace(" ", "-")
    db.session.add(Topic(name=t['name'], slug=slug, description=t['description'], display_order=index))

db.session.commit()
print("Topics seeded successfully.")