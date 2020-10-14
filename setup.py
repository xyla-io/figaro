from setuptools import setup, find_packages

setup(name='figaro',
      version='0.0.1',
      description='Xyla\'s Python Facebook Ads API client wrapper.',
      url='https://github.com/xyla-io/figaro',
      author='Xyla',
      author_email='gklei89@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
        'facebook_business >= 3.3',
        'pandas',
        'ratelimit',
      ],
      zip_safe=False)
