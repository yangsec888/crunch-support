from setuptools import setup
import re, os

def get_property(prop):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    ini_file = cur_dir + "/__init__.py"
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), open(ini_file).read())
    return result.group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="crunch_support",
    version=get_property("__version__"),
    author="Sam Li",
    author_email="yang.li@owasp.org",
    description= "Python Package to Support 42crunch System Deployment",
    long_description_content_type='text/markdown',
    long_description=long_description,
    keywords = "DIY Python 42crunch Support Deployment",
    #long_description_content_type="text/markdown",
    url="https://github.com/yangsec888/crunch-support",
    packages=['crunch_support'],
    package_dir={'crunch_support': 'src'},
    include_package_data=True,
    scripts=['src/bin/api-audit','src/bin/api-scan','src/bin/api-protect'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.25.1',
        'ruamel.yaml==0.17.21',
        'lxml==4.9.1',
        'selenium==4.0.0a6.post2',
        'selenium-wire'
    ]
)
