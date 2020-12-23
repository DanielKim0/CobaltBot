# README

## Overview

CobaltBot is a discord bot that includes functionality for multiple different games, as well as some basic commands. 

Game functionality is separated into cogs, with each cog associated with a particular game and its commands. Server administrators can add and remove cogs from their servers at will, functionally limiting the commands that their users can access. Additionally, admins can set the prefixes that the server uses for a particular bot per-server as well.

## Installation and Usage

Run ```python -r requirements.txt``` to download necessary modules.

After retrieving the necessary data for the eu4 processing files, run the ```main.py``` files for the eu4 and smt processing modules, found in ```processing/```.

To run the bot itself, run ```python bot.py```, found in ```bot/```.

## Attributions and Disclaimers

Data for league's MMR system is generated using WhatIsMyMMR, and the rest of the league cog uses cassiopeia.

Data for SMT demons is taken from aqiu384's megaten-fusion-tool.

CobaltBot isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.