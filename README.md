# Go Development Environment
An easy to install AI development environment for the game of Go.

## Table of Contents
1. [Installation](#Installation)
2. [Using the Virtual Environment](#Using-the-Virtual-Environment)
3. [Development](#Development)
4. [Purpose](#Purpose)

## Installation
Installation is relatively straightforward. Clone this repository and then run the installation script.
```bash
$ git clone git@github.com:RITificialIntelligence/go_development_env.git
$ cd go_development_env
$ ./scripts/install.sh
```
The install script should take about a minute to run and will both set up a python virtual environment as well as install OpenAI's Go development environment.

## Using the Virtual Environment
Each time you start a new session, you must activate the python virtual environment.
```bash
$ source rit_go_venv/bin/activate
```
Once done with development, deactivating the environment can be done like so.
```bash
$ deactivate
```
Using this virtual environment will allow for the installation of python packages even if you are not developing on a machine in which you have root user priveleges.

## Development
Once the installation script has been run and the virtual environment has been activated, you should be able to run the following python script without error.
```python
import gym
env = gym.make('Go9x9-v0')
env.reset()
env.render()
```
[For information on developing your Go AI read this documentation on the framerwork provided by OpenAI.](https://gym.openai.com/docs).

## Purpose
This repository exists to provide competitors in RITficialIntelligence's Annual Go Tournament a means to easily set up a development environment for their agents. It is likely that not all competitors will have their own working \*nix distro so all scripts are executable on any machine regardless of user privilege level. Given that the vast majority of RIT students in computing have access to university provided machines that run some variation of \*nix, this should resolve any compatibility issues.
