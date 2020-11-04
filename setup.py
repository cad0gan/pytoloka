import setuptools

setuptools.setup(
    name='pytoloka',
    version='0.1.0',
    author='Philip Minakov',
    author_email='sir.cadogan@protonmail.com',
    description='An async library for Yandex.Toloka',
    url='https://github.com/cad0gan/pytoloka',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'aiohttp==3.6.2',
        'pytz==2020.1',
    ]
)
