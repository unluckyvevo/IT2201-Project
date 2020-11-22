# Readbit Learning System 

## Setup

##### Python 3.9.0

This app is developed on Python3.9.0 (Release Date: Oct. 5, 2020) so we should install that version. Below are CLI commands to install it on Ubuntu / OpenSUSE. You can check out [this tutorial](https://www.python.org/downloads/) if you are using Windows 10.

1. `sudo add-apt-repository ppa:deadsnakes/ppa`
1. `sudo apt update`
1. `sudo apt install python3.9`

1. Set Python3.9.0 to be the default runtime
`sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8`
`sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9`
1. `sudo update-alternatives --config python3`
1. `sudo rm /usr/bin/python3; sudo ln -s python3.8 /usr/bin/python3`



## Quick Start
- Clone this repo
`git clone https://github.com/unluckyvevo/IT2201-Project/`

- Change folder
`cd IT2201-Project/`

- Install required dependencies
`python3 -m pip install -r requirements.txt `

- Start the Flask server
`python3 run.py`

Go to `http://127.0.0.1:5000/` to view the web application


#### Account credentials (student):
* Email: student1@readbit.com 
* Password: student

#### Account credentials (instructor):
- Email: instructor1@readbit.com 
- Password: instructor

## Bugs and Issues

Found a bug or problem in implementation? [Open a new issue](https://github.com/unluckyvevo/IT2201-Project/issues/new/choose) here on GitHub.


## Wireframe
You can view the wireframe at [InvisionApp](https://ict2x01team33.invisionapp.com/freehand/ReadBit-UaooBiBzh).
