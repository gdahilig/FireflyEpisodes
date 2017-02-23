"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# --------------- Constants
APPLICATION_ID = "amzn1.ask.skill.05cab26d-b563-44bc-97a1-932fc623c36d"
CARD_TITLE = "Unofficial Firefly Fan Episode List"
SKILL_TITLE = "Firefly Fan"

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(card_title, card_content, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title':  card_title,
            'content': card_content
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response_nocard(output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Unofficial Firefly Fan Episode List. " \
                    "Please tell me what episode you are interested in."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what episode you are interested in"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, reprompt_text, should_end_session))

def more_info_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = CARD_TITLE
    speech_output = "Please tell me what episode you are interested in."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what episode you are interested in"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, reprompt_text, should_end_session))
def handle_session_end_request():
    card_title = CARD_TITLE
    speech_output = "Thank you for using the Unofficial Firefly Fan Episode List. " \
                    "Have a nice day, and a shiney tomorrow! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response_nocard(speech_output, None, should_end_session))

def create_episide_attributes(episode):
    return {"episode": episode}


def set_episode_in_session(intent, session):
    """ Sets the episode in the session and prepares the speech to reply to the
    user.
    """

    card_title = CARD_TITLE
    session_attributes = {}
    should_end_session = False
    speech_output = ""
    card_content = ""

    if 'Episode' in intent['slots']:
        try:
            if 'value' not in intent['slots']['Episode']:
                print("Error: No value provided for 'Episode'.")
                raise ValueError("Invalid episode")
            current_episode = int(intent['slots']['Episode']['value'])
        except:
            print("Exception handler")
            speech_output = "I'm not sure what episode you are asking for.  " \
                            "You can ask me by saying, " \
                                "Get episode 1"
            reprompt_text = "I'm not sure what episode you are asking for.  " \
                            "You can ask me by saying, " \
                                "Get episode 1"
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, speech_output, reprompt_text, should_end_session))

        print("current_episode: {}".format(current_episode))
        LAST_EPISODE = 14

        if current_episode <= LAST_EPISODE:
            # Get Episode information
            dictEpisode = getEpisodeInfo(current_episode)

            intent_name = intent['name']

            if intent_name == 'GetAirDateIntent':
                episode_title = dictEpisode['Title']
                session_attributes = create_episide_attributes(current_episode)
                episode_synopsis = dictEpisode['Synopsis']
                episode_airdate = dictEpisode['AirDate']
                speech_output = "Episode : " + \
                                str(current_episode) + \
                                ", entitled '" + \
                                episode_title + \
                                "', was first aired " + \
                                episode_airdate + "."
                # Card info 
                card_title = "When was Firefly episode {} aired?".format(current_episode)
                card_content = "Episode: {} \n"\
                               "Title: {} \n"\
                               "Air date: {}".format(current_episode, episode_title, episode_airdate)
            elif intent_name == 'GetEpisodeIntent':
                episode_title = dictEpisode['Title']
                session_attributes = create_episide_attributes(current_episode)
                episode_synopsis = dictEpisode['Synopsis']
                episode_airdate = dictEpisode['AirDate']
                speech_output = "Title for episode " + \
                                str(current_episode) + \
                                " is " + \
                                episode_title + ". " +\
                                "Air date " + episode_airdate + ". " +\
                                episode_synopsis
                card_title = "Firefly Episode {}".format(current_episode)
                card_content =  "Episode:  {}\n"         \
                                "Title:    {}\n"         \
                                "Airdate:  {}\n"         \
                                "Synopsis: {}\n".format(current_episode, episode_title, episode_airdate, episode_synopsis)
            else:
                print("Unknown intent: {}".format(intent))
        else:
            speech_output = "Due to the short-sightedness of network television executives, the series was cancelled after episode 14.  However, the adventures of this small band of galactic outcasts continues in the feature film, Serenity."
        reprompt_text = "Would you like more information for another episode?"
        # speech_output = speech_output + ": : Please tell me another episode you are interested in or say: cancel"
    else:
        speech_output = "I'm not sure what episode you are asking for. " \
                        "Please try again."
        reprompt_text = "I'm not sure what episode you are asking for.  " \
                        "You can ask me by saying, " \
                        "Get episode 1"
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, card_content, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    print("intent name=" + intent_name)
    print("intent={}".format(intent))
    print("session={}".format(session))

    # Dispatch to your skill's intent handlers
    if intent_name == "GetEpisodeIntent":
        return set_episode_in_session(intent, session)
    # handle the GetAirDateIntent
    if intent_name == "GetAirDateIntent":
        return set_episode_in_session(intent, session)
    elif intent_name == "NoIntent":
        return handle_session_end_request()
    elif intent_name == "YesIntent":
        return more_info_response()

    # Handle Amazon intents.
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# -----------------------------------------------
# Database functions

def getEpisodeInfo(iEpisodeNumber):
    # dynamodb = boto3.resource("dynamodb", region_name='us-east-1', endpoint_url="arn:aws:dynamodb:us-east-1:768614738980:table")
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table('FireflyEpisodes')
    item = {}
    try:
        response = table.get_item(
            Key={
                'EpisodeID': iEpisodeNumber
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        print("GetItem succeeded:")
        print(json.dumps(item, indent=4, cls=DecimalEncoder))
    return item
# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Launch Event: {}".format(event))

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    """
    Prevent someone else from configuring a skill that sends requests to this
    function by testing for the application id.
    """
    if (event['session']['application']['applicationId'] != APPLICATION_ID):
        raise ValueError("Invalid Application ID")

    print("Launch type: {}".format(event['request']['type']))


    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
