# Create a file named setup.py in your project root
# with the following content:

from setuptools import setup, find_packages

setup(
    name="my_cv_agent_backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        # Add other dependencies here
    ],
)