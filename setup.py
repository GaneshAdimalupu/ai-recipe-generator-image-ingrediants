from setuptools import setup
from setuptools import find_packages

# Load the README file.
# with open(file="README.md", mode="r") as readme_handle:
#     long_description = readme_handle.read()

setup(
    name='be-my-chef-ai',

    author='Ganesh Adimalupu',

    author_email='ganeshadimalupu@disroot.org',

    version='0.1.0',

    description='AI recipe generator',

    # long_description=long_description,

    long_description_content_type="text/markdown",

    #url='',

    install_requires=[
        'streamlit',
        'streamlit_lottie',
        'extra_streamlit_components',
        'streamlit_option_menu',
        'trycourier',
        'streamlit_cookies_manager',
    ],

    keywords='streamlit, machine learning, AI, recipe, food, authentication, cookies',

    packages=find_packages(),


    include_package_data=True,

    python_requires='==3.10.6',

    classifiers=[

        # 'Intended Audience :: Developers',
        # 'Intended Audience :: ML Engineers',
        # 'Intended Audience :: Streamlit App Developers',

        'License :: OSI Approved :: MIT License',

        'Natural Language :: English',

        'Operating System :: OS Independent',

        # 'Programming Language :: Python :: 3.10.6',

        # 'Topic :: Streamlit',
        # 'Topic :: Authentication',
        # 'Topic :: Recipe/Food'

    ]
)