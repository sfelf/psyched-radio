from setuptools import find_packages, setup


def readme():
    with open('README.md') as f:
        return f.read().strip()


setup(
    name="psyched-radio",
    use_scm_version={"fallback_version": "0.1.0"},
    description="Downloads shows from Psyched Radio's RSS feed",
    long_description=readme(),
    author="Thomas Nelson",
    url="https://github.com/sfelf/psyched-radio",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    setup_requires=["setuptools-scm"],
    python_requires='>=3.7',
    install_requires=['click', 'eyed3', 'feedparser', 'requests'],
    entry_points={
        'console_scripts': ['download_feed = psyched_radio.main:download_feed']
    },
)
