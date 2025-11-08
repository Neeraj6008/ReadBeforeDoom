from setuptools import setup, find_packages

setup(
    name="readbeforedoom",
    version="0.1.0",
    author="Neeraj",
    description="A tool to analyze Terms & Conditions",
    long_description=open('https://github.com/Neeraj6008/ReadBeforeDoom/README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Neeraj6008/ReadBeforeDoom",
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml',
        'spacy'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'readbeforedoom=readbeforedoom.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'readbeforedoom': ['*.db'],
    },
)
