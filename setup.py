"""
BDR AI - Business Development Representative Automation Tool

A comprehensive B2B lead generation and outreach automation system that integrates
Apollo API, Airtable, OpenAI, and Gmail to create personalized outreach campaigns.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bdr-ai",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="B2B Lead Generation and Outreach Automation Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bdr-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Sales/Marketing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "aws": [
            "boto3>=1.26.0",
            "serverless>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bdr-ai=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.json", "*.md"],
    },
    keywords="b2b, sales, automation, lead generation, outreach, apollo, airtable, openai, gmail",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/bdr-ai/issues",
        "Source": "https://github.com/yourusername/bdr-ai",
        "Documentation": "https://github.com/yourusername/bdr-ai#readme",
    },
)
