from setuptools import setup

setup(
    name="hermes",
    version="1.0",
    description="A jira command line interface in python",
    url="https://github.com/jkazan/hermes",
    author="Johannes Kazantzidis",
    author_email="j.kazantzidis13@alumni.imperial.ac.uk",
    license="MIT",
    packages=["hermes"],
    install_requires=["requests", "graphviz", 'pyreadline;platform_system=="Windows"'],
    zip_safe=False,
)
