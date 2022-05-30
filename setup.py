from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name='mtgflask',
        version='0.1.0',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'flask',
            'pymongo',
            'schematics'
        ]
    )
