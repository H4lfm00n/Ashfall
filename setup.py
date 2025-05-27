from setuptools import setup, find_packages

setup(
    name="emotionless_options",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yfinance==0.2.36",
        "pandas==2.2.0",
        "numpy==1.26.3",
        "requests==2.31.0",
        "beautifulsoup4==4.12.3",
        "tweepy==4.14.0",
        "python-dotenv==1.0.1",
        "scikit-learn==1.4.0",
        "nltk==3.8.1",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered options trading predictor",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/emotionless_options",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 