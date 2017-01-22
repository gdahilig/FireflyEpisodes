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

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
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
    speech_output = "Welcome to the Firefly Episode List. " \
                    "Please tell me what episode you are interested in."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what episode you are interested in"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def more_info_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "More Episode Info"
    speech_output = "Please tell me what episode you are interested in."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what episode you are interested in"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the Firefly Episode List. " \
                    "Have a nice day, and a shiney tomorrow! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_episide_attributes(episode):
    return {"episode": episode}


def set_episode_in_session(intent, session):
    """ Sets the episode in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    speech_output = ""

    if 'Episode' in intent['slots']:
        if 'value' not in intent['slots']['Episode']:
            should_end_session = True
            return
        try:
            current_episode = int(intent['slots']['Episode']['value'])
        except:
            speech_output = "I'm not sure what episode you are asking for. " \
                            "Please try again."
            reprompt_text = "I'm not sure what episode you are asking for.  " \
                            "You can ask me by saying, " \
                                "Get episode 1"
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

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
                                ": entitled " + \
                                episode_title + \
                                ": was first aired " + \
                                episode_airdate + "."
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
            else:
                print("Unknown intent: {}".format(intent))
        else:
            speech_output = "Due to the short-sightedness of network television executives, the series was cancelled after episode 14.  However, the adventures of this small band of galactic outcasts continues in the feature film, Serenity. "
        reprompt_text = "Would you like more information for another episode?"
    else:
        speech_output = "I'm not sure what episode you are asking for. " \
                        "Please try again."
        reprompt_text = "I'm not sure what episode you are asking for.  " \
                        "You can ask me by saying, " \
                        "Get episode 1"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

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
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

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