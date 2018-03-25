# Lobsters vs Fishers
## Since the beginning of time...
Since the beginning of time, an epic battle has been going on between Fishers and Lobsters.

Welcome to Lobsters vs Fishers!

After centuries of lobsters being captured by fishers and being eaten, the crustacean have developed the ability of eat humans and are more powerful than ever.

In the game, you can participate in the extermination of such a terrible beast or witness the end of the human race.
The fate of humanity is up to the ability of the players and their luck. Who will be victorious?

## Rules

At the very first moment of the game, you will be assigned one of the two roles. The number of Lobsters in the game depends on the number of players, which goes between 5 to 10 people, as you can see below:

* 5 and 6 players have 2 Lobsters
* 7 and 8 players have 3 Lobsters
* 9 and 10 players have 4 Lobsters

Every player starts with 3 lives and both of the species have to work with those of the same kind to kill the other one in order to win.
Fishers don't know who is human or not but Lobsters know who is a Lobster. Therefore, the latter pretend being humans, accuse Fishers of being Lobsters and convince the rest of the group to take their lives. Fishers try to discern who is a Lobster and hunt them down.
To decide who will lose a life, all the players have a few seconds to discuss and conspire. Then, every player has to say out loud who they have chosen and the most voted player looses a life. For example: Player 3.

Every morning, fishermen check out the weather as a part of their routine. Depending on it, one event or another will happen. For example: "It's sunny! Everybody +1 live!". Sometimes one bottle from the ocean appears and makes some changes in the game, which can be public or secret. For example: "There is full moon! Two players switch species."

The game ends when the sum of the lives on one team is equal to 0.

### List of possible events

* "It's windy! Someone gets to steal a life."

* "It's raining! One player chooses a second one, who looses one life."

* "A lightning bolt struck! Someone loses 2 lives!"

* "There is a rainbow! One player discover another player's species"*

And many more exciting events!

## How we built it

The final idea is to have a master program running in a computer at the centre and clients in different phones.
The main code running in the computer is coded in python. We use two APIs, the google-cloud-api API to recognise speech and the google-translate API to transform text into speech.

The connection between the master and the clients is handled through a server deployed in a amazon-web-services machine using Flask in python.

In each client (smartphone) we programmed and android app which allows you to interact with the game.

## Challenges we ran into

Whilst requests was easy pizi in python, we had a hard time figuring out how to connect the clients (android) to the server. Sadly, this problem actually took a great amount of hours and energy and even with the help of many mentors the solution achieved.

This affected negatively on the development of the project, since the connection between server and clients is one of the most important parts.

## What we learned

This is the first time in which we have used Git & GitHub properly. With around one hundred commits in one weekend by 3 developers. 

We also managed to distribute the work efficiently. Being a team of 5 sometimes it is different to divide the work in such a way so that everyone is doing something at all times.

We divided the work in different parts: game design, master code, server code and client code.
