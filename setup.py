from setuptools import find_packages
from setuptools import setup


try:
    README = open("README.rst").read()
except IOError:
    README = None

setup(
    name="guillotina_dynamictablestorage",
    version="1.1.4",
    description="Dynamic storages based on tables " "instead of databases",
    long_description=README,
    install_requires=["guillotina>=5,<6", "typing_extensions"],
    author="Nathan Van Gheem",
    author_email="vangheem@gmail.com",
    url="https://github.com/guillotinaweb/guillotina_dynamictablestorage",
    packages=find_packages(exclude=["demo"]),
    include_package_data=True,
    extras_require={
        "test": [
            "pytest<=3.1.0",
            "docker",
            "backoff",
            "psycopg2-binary",
            "pytest-asyncio<0.10.0",
            "pytest-cov<=2.5.1",
            "coverage>=4.0.3",
            "pytest-docker-fixtures",
            "prometheus_client",
        ]
    },
    classifiers=[],
    entry_points={},
)
