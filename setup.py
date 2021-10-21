from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="catprinter",
    version="1.0",
    packages=find_packages(),
    install_requires=required,
    project_urls={
        'Source': 'https://github.com/thyme4soup/catprinter',
        'Fork of': 'https://github.com/rbaron/catprinter'
    }
)
