from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("version.txt", "r") as fh:
    version = fh.read()

setup(
    name='cltl.combot',
    version=version,
    packages=find_namespace_packages(include=['cltl.*']),
    url="https://github.com/leolani/cltl-combot",
    license='MIT License',
    author='CLTL',
    author_email='t.baier@vu.nl',
    description='Communication Robot Framework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    install_requires=["numpy", "pillow", "kombu"],
)