from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cltl.combot',
    version='0.0.1',
    packages=find_namespace_packages(include=['cltl.*']),
    url="https://github.com/leolani/cltl-combot",
    license='MIT License',
    author='CLTL',
    author_email='t.baier@vu.nl',
    description='Communication Robot Framework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    install_requires=[
        "numpy~=1.19.4",
        "pillow~=8.0"
    ],
)