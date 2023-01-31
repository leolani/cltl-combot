from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setup(
    name='cltl.combot',
    version=version,
    package_dir={'': 'src'},
    packages=find_namespace_packages(include=['cltl.*', 'cltl_service.*'], where='src'),
    package_data={'cltl.commons.language_data': ["*.txt", "*.json"]},
    data_files=[('VERSION', ['VERSION'])],
    url="https://github.com/leolani/cltl-combot",
    license='MIT License',
    author='CLTL',
    author_email='t.baier@vu.nl',
    description='Communication Robot Framework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    install_requires=['emissor'],
    extras_require={
        "external": [
            "kombu"
        ],
    }
)