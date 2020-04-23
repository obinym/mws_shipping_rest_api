from setuptools import setup, find_packages

setup(
    name='mwsshippingrestapi',
    version='1.0.3',
    url='https://github.com/obinym/mws_shipping_rest_api.git',
    author='obinym',
    author_email='obiny@com',
    description='see above',
    packages=['mwsshippingrestapi'],
    include_package_data=True,
    install_requires=['flask','connexion[swagger-ui]'],
)
