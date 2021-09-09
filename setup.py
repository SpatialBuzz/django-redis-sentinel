from setuptools import setup

description = """
Plugin for django-redis that supports Redis Sentinel
"""

setup(
    name="sb-django-redis-sentinel",
    url="https://github.com/SpatialBuzz/django-redis-sentinel",
    author="Ryan Shaw",
    author_email="ryan.shaw@spatialbuzz.com",
    version="1.2.0",
    packages=[
        "django_redis_sentinel",
    ],
    description=description.strip(),
    install_requires=[
        "django-redis>=4.10.0",
        "Django>=2.2",
    ],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
