from setuptools import find_packages, setup

setup(
    name='akiapplier',
    packages=['akiapplier.data','akiapplier.features','akiapplier.models','akiapplier.visualization'],
    package_dir={"akiapplier": "src"},
    py_modules=["akiapplier"],
    install_requires=[
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "python-dotenv",
    "plotly",
    "scikit-learn"
    ],
    version='0.1.0',
    description='Applying KDIGO guidelines to creatinine data',
    author='Huibert-Jan Joosse',
    license='MIT',
)
    