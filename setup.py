from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Automatically generate DRF API components for Django apps"

setup(
    name='django-magicapi',
    version='0.1.0',
    author='Prashant Karna',
    author_email='prashantkarna21@gmail.com',
    description='Automatically generate DRF API components for Django apps',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/imprashant98/magicapi',
    project_urls={
        'Bug Reports': 'https://github.com/imprashant98/magicapi/issues',
        'Source': 'https://github.com/imprashant98/magicapi',
    },
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'django_magicapi': ['templates/*.txt'],
    },
    install_requires=[
        'Django>=3.2',
        'djangorestframework>=3.12',
        'django-filter>=2.4',
        'djangorestframework-simplejwt>=5.0',
    ],
    extras_require={
        'swagger': ['drf-yasg>=1.20.0'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='django drf api generator rest framework magicapi',
    python_requires='>=3.8',
)