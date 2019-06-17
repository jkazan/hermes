from setuptools import setup, find_packages


with open("README.md") as f:
    long_description = f.read()


setup(
    name="hermes",
    author="Johannes Kazantzidis",
    author_email="johannes.k@live.com",
    description="A command line interface to improve workflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jkazan/hermes",
    license="MIT",
    version="0.1.0",
    install_requires=["requests"],
    packages=find_packages(),
    include_package_data=True,
    keywords="jira",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={"console_scripts": ["hermes=hermes.hermes:main"]},
)
