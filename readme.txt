
-----------------| READ ME |-----------------

=============================================
|        W2 Team Project - FilmFlick        |
=============================================
---------------------------------------------
   Contents:
---------------------------------------------
1. What is FilmFlick?
2. How to install pip3
3. How to install the required libraries
4. How to run the server 
5. FilmFlick's Database


---------------------------------------------
   1. What is FilmFlick?
---------------------------------------------
FilmFlick is a python 3 (3.8) based film suggestion web application achieved via flask.
It serves to reduce the amount of time individuals spend looking for films to watch.
This is obtained via an algorithm which queries a movie database for a randomly generated film based upon criteria provided by the user.
[Alternatively, the user is free to not specify any criteria and receive a completely random film.]

FilmFlick is unlike other film suggestion services as it does not present a bias towards certain films depending on a user's viewing habits.
This design point was introduced to better present new media to the user.
If a user dislikes a film, they can mark it as disliked and prevent the algorithm from suggesting it again.
Likewise, if a user likes a specific film, they can mark it as liked for quick access via their profile.

FilmFlick also implements a user review system where users can leave reviews on films to assist others in their selection process.


---------------------------------------------
   2. How to install pip3
---------------------------------------------
FilmFlick utilises some non-standard python 3.8 packages which need to be installed using pip3.
In the instance where you're unsure if your device has pip3 installed, please continue following this section.
Alternatively, if your device does have pip3 installed but simply lacks the required libraries, please install them by refering to "3. How to install the required libraries".

You can check to see if pip3 is installed on your device via:
   Windows:         py -m pip --version
Unix/macOS:         python -m pip --version
     Linux:         pip3 --version

If pip3 is not found, then please install it by refering to the respective link:

For Windows and Unix/macOS:     https://pip.pypa.io/en/stable/installing/
For Linux Package Manager:      https://packaging.python.org/guides/installing-using-linux-tools/


---------------------------------------------
   3. How to install the required libraries
---------------------------------------------
For your convenience, we have provided a requirement.txt file which details the necessary libraries and their versions.
In you terminal within the root directory of the application (the one with main.py), please enter the following to install the required libraries: 

pip install -r ./requirements.txt


---------------------------------------------
   4. How to run the server
---------------------------------------------
FilmFlick runs off of a flask server.
To start up the server please run "main.py" from the terminal located in the root directory of the application with

python3 main.py

If all the necessary libraries are installed on your device, the terminal will provide you with an IP address that can be used to access the site.
Please copy this IP address into your browser of choice to access FilmFlick.
ALlow the process to run in the terminal for the period you're accessing the site.
When you wish to stop the server, simply press "ctrl + c" on the respective terminal running the server to stop the process.


---------------------------------------------
5. FilmFlick's Database
---------------------------------------------
FilmFlick's movie database consists of access to two external APIs and a local cache of films (All content licensed under CC BY-NC 4.0 via the OMDB API).
Due to this local cache of films, the database must remain intact with the rest of the application for the sake of functionality of the site.
The information regarding users and user reviews have been cleared for the sake of submission. 


© FILMFLICK 2020-2021 - W2 Group









