from setuptools import find_packages, setup

requirements = []
with open("requirements.txt") as f:
    for line in f:
        requirements.append(line.strip())

setup(
    name='dangie website',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
)
