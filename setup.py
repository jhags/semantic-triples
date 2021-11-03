from setuptools import setup, find_packages

# requirement file
with open('requirements.txt') as f:
    required = f.read().splitlines()

# readme file
with open('README.md') as f:
    readme = f.read()


setup(
    name='semnet',
    version='0.0.1',
    description='Turn text into a network of semantic triples.',
    long_description=readme,
    long_description_content_type="text/md",
    url='https://github.com/jhags/semantic-triples',
    author='J Hagstrom',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(include=['semnet', 'semnet.*']),
    package_data={},
    install_requires=required,
    tests_require=['pytest', 'pytest-cov'],
    python_requires='>=3.7',
)
