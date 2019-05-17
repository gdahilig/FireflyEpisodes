# FireflyEpisodes
Alexa skill written in python that provides Firely episode info.  

## Overview
It supports basic voice interactions with Alexa via the "custom skill" model.  It uses a DynamoDB database to store the episode information.

Interaction model information can found in the following files:
* utterances.txt
* slot_types.txt

## Example Interaction
"Alexa, ask the Firefly Fan for episode 1"
"Alexa, get the airdate for episode 10 from the Firefly Fan"
"Alexa, ask the Firefly Fan to find episode 14"

##main.py
This is main code file and supports the very basic interactions with Alexa.

Here is a short description of significant functions:
###lambda_handler()
The main lambda function that is called by the Alexa. Depending on the request type, it will call on_session_started(), onlaunch(), onintent(), or onsessionended() functions.

###on_session_started()
This function is called when the session first starts.

###on_launch()
Called when the user launches the skill without specifying what they want.  Calls the get_welcome_message().

###on_intent()
Called when the user specifies an intent for this skill.  Based on the intent (GetEpisodeIntent, GetAirDateIntent, NoIntent,, YesIntent) it will build the Alexa response to the user.

###on_session_ended()
Called when the user ends the session.  Note that this function is not called when the skill returns should_end_session=true




