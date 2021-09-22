import spotify
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import urllib

# Set up Twilio client
# Account SID and Auth Token from www.twilio.com/console
TWILIO_ACCOUNT_SID=os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN=os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Configure public domain for this flask app
APP_URL=os.environ.get('APP_URL')

app = Flask(__name__)

# A route to respond to SMS messages
@app.route('/sms', methods=['POST'])
def inbound_sms():
    # Grab the relevant phone numbers and text body
    from_number = request.form['From']
    to_number = request.form['To']
    body_text = request.form['Body']

    # help
    if (body_text.lower() == "h"):
        response = MessagingResponse()
        response_message = """
supported commands:
'call me' -> get phone call
'play <song_title>' -> get phone call with requested song
        """
        response.message(response_message)
        return str(response)

    # 'call me' command
    if ("call me" in body_text.lower()):
        # Create a phone call
        client.api.account.calls.create(to=from_number, from_=to_number, url=APP_URL+'/call/hello_world')

        response = MessagingResponse()
        response.message('Giving you call right now')
        return str(response)


    # 'play <song_title>' command - look up song and play it via call
    # check if first word is 'play'
    is_play_command = body_text.split(' ', 1)[0].lower() == 'play'
    if (is_play_command):
        rest_of_command = body_text.split(' ', 1)[1:]
        print(rest_of_command)
        if len(rest_of_command) == 0:
            response = MessagingResponse()
            response.message('please provide a song name')
            return str(response)

        # Grab the song title from the body of the text message after play command
        song_title = urllib.parse.quote(rest_of_command[0])

        # Create a phone call that uses our other route to play a song from Spotify.
        client.api.account.calls.create(to=from_number, from_=to_number,
                            url=APP_URL+'/call/play_song?track={}'
                            .format(song_title))

        response = MessagingResponse()
        response.message('Thanks for texting! Searching for your song now. Wait to receive a phone call :)')
        return str(response)
    
    response = MessagingResponse()
    response_message = "Command not supported. Reply with valid command. Reply with 'h' to view supported commands."
    response.message(response_message)
    return str(response)


# A route to handle the logic for playing song
@app.route('/call/play_song', methods=['POST'])
def play_song():
    song_title = request.args.get('track')
    track_url = spotify.get_track_url(song_title)

    response = VoiceResponse()
    if not track_url:
        response.say("Sorry, we could not find your song")
    else:
        response.say("Here is the song you requested:")
        response.play(track_url)
    
    return str(response)

# A route to handle the logic for saying hello world
@app.route('/call/hello_world', methods=['POST'])
def voice_hello_world():
    response = VoiceResponse()
    response_message = "Hello World"
    response.say(response_message)
    return str(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)