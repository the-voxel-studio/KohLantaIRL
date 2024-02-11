# DenisBrogniart

## General infos
Denis Brogniart is a multitasking discord bot.
Its goal is to manage the Koh Lanta Discord game as game master, without requiring a physical person dedicated to this role.
Thus, its missions are diverse: management of votes, results, fight against cheating, moderation, management of secret alliances, etc.

## Technologies
Project is created with:
* Python 3.10.11
    * match/case syntax support is required (min 3.10)
* [Discord Dev Portal](https://discord.com/developers/)
* [MongoDb](https://mongodb.com)
* [Amazon Web Services](https://aws.amazon.com)

## Setup
To run this project:
1. Download it
2. Setup a Python Virtual Environnement with the [requirements.txt file](/requirements.txt).
3. Create the Server [Discord architecture](#discord-server-architecture) as defined below.
4. Create the [roles](#discord-roles-architecture) as defined below.
5. Configure a discord bot on the [Discord Dev Portal](https://discord.com/developers/).
6. Create an empty database en [MongoDb](https://mongodb.com) and copy/create the connection url.
7. Complete the [.example.env](/Example/.example.env) file with the unique ids and tokens specific to your server. Then move it to the root of the project and rename it ".env" (without ".example").
8. Complete the discussion channels with templates from the [Templates](/Templates/) folder

> [!NOTE]  
> Some functions, names and variables are written in French. You are free to change them to their English equivalent or any other language. Just be careful that the operation of the robot is not affected, especially in the channel names and roles.

## Discord server roles and architecture
### The server channels and roles must meet a certain architecture for the bot to function properly.

You have to follow this model : [KohLanta on Discord Model](https://discord.new/FswZkfz7qjuE)
Please pay attention to the following points
* It is imperative to respect the order of roles below.
* The example provided includes many alliances (text and voice channels). They only have a demonstrative role. You must empty the "Alliance" category, because this entire category is entirely controlled by Denis Brogniart, it is here that he will create the text and voice channels of each alliance and manage their access.

> [!NOTE]
> “anciens” roles and channels are used for people who have already participated in a previous season. Their use is therefore in no way obligatory.

> [!WARNING]
> The robot (and therefore the Game Master role) must have administrator rights.