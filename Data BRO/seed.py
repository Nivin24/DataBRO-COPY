# seed.py

from app import app, db
from models import Topic, TopicContent  # Adjust the import if your models are in another module

def seed_data():
    with app.app_context():
        # Optional: clear existing data
        db.session.query(TopicContent).delete()
        db.session.query(Topic).delete()
        db.session.commit()

        # Create dummy Topic
        topic = Topic(
            name="Python Basics",
            slug="python-basics",
            description="Introduction to Python programming language.",
            display_order=1
        )
        db.session.add(topic)
        db.session.commit()

        # Create associated TopicContent
        content = TopicContent(
            topic_id=topic.id,
            theory="""
                Python is a versatile, high-level programming language known for its readability and simplicity.
                It's widely used in data science, web development, automation, and more.
            """,
            quiz="""
                1. What is Python?
                2. What is the difference between a list and a tuple?
            """,
            flashcards="""
                Q: What is a variable in Python?
                A: A container for storing data values.

                Q: How do you create a function?
                A: Using the 'def' keyword.
            """,
            resources="""
                - https://docs.python.org/3/
                - https://realpython.com/
            """,
            certifications="""
                - Python for Everybody (Coursera)
                - Google IT Automation with Python
            """,
            practical="""
                - Write a program to reverse a string.
                - Create a calculator using basic operators.
            """
        )
        db.session.add(content)
        db.session.commit()

        print("✅ Seed data inserted successfully.")

if __name__ == "__main__":
    seed_data()