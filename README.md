# DenisBrogniart

## General infos
Denis Brogniart is a multitasking discord bot.
Its goal is to manage the Koh Lanta Discord game as game master, without requiring a physical person dedicated to this role.
Thus, its missions are diverse: management of votes, results, fight against cheating, moderation, management of secret alliances, etc.

## Technologies
Project is created with:
* Python 3.10.11
* [Discord Dev Portal](https://discord.com/developers/)
* [MongoDb](https://mongodb.com)
* [Amazon Web Services](https://aws.amazon.com)

## Setup
To run this project, install it locally, Complete the "EnvExample/.env" file with the unique ids and tokens specific to your server. Then rename this file to exactly ".env" (nothing before the dot) and move it to the root of the project.

## Discord server architecture
### The server must meet a certain architecture for the bot to function properly.

It should have the following list of chat channels, which can be placed however you like:
* votes : in which there will be the messages to vote
* results : in which there will be the results of the different votes
* registration: in which new players will be able to identify
* general: in which players can discuss
* eliminated: in which the eliminated can discuss
* bot: in which Denis Brogniart can send messages to admins

But also two categories:
* Help:
    * alliance-creation
    * alliance-add-a-member
    * alliance-remove-a-member
    * another-question
    * robot-schedules
    * robot-github

* Alliances:
    * This entire category is entirely controlled by Denis Brogniart, it is here that he will create the text and audio channels of the alliances and manage their access.