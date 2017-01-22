# FireflyEpisodes
Alexa skill written in python that provides Firely episode info.  

## Overview
It supports basic voice interactions with Alexa via the "custom skill" model.  It usages a DynamoDB database to store the episode information

Interaction model information can found in the following files:
* slot_types.txt
* utterances.txt

##main.py
This is main code file and supports the very basic interactions with Alexa.

Here is a short description of significant functions:
###lambda_handler()
The main lambda function that is called by the Alexa. Depending on the request type, it will call on_session_started(), onlaunch(), onintent(), or onsessionended() functions.

###on_session_started()
This function is called when the session first starts.

###onlaunch()
Called when the user launches the skill without specifying what they want.  Calls the get_welcome_message().

###onintent()
Called when the user specifies an intent for this skill.  Based on the intent (GetEpisodeIntent, GetAirDateIntent, NoIntent,, YesIntent) it will build the Alexa response to the user.

###onsessionended()
Called when the user ends the session.  Note that this function is not called when the skill returns should_end_session=true




