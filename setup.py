from setuptools import setup, find_packages

setup(
    name='analise_ilpi',
    version='0.1',
    description='Ferramentas para análise de dados de ILPIs',
    author='MJRS',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'seaborn'
    ],
    python_requires='=>3.13',
)
