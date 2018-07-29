# spurgeon
Processing scripts to convert Spurgeon devotionals into audio using Google's TTS system (preferably Wavenet)

# Installation
You'll need two things:

1. Install the necessary python dependencies:

        pip install -r requirements.txt
        
2. [Set up your Google Cloud SDK properly](https://cloud.google.com/text-to-speech/docs/quickstart-protocol).

Also, the audio produced by this script is not small. For Morning and Evening, you'll need ~100GB of spare disk space.

# Usage

Just run:

    python convert.py

This is a minimal script. It will pull Morning and Evening, parse the text file into the different days (by month, day, and time of day), then loop through the content for each day and submit it to Google for conversion to audio.

You can modify the "voices" list variable to alter which voices get used by Google. Note that this service has a free tier (1M characters) which is lower than the length of this book (~1.5M characters), so it will end up costing you if you do the whole run in a single month. As such, if cost is an issue, I recommend running this script in pieces in different months; also, using fewer and cheaper (non-Wavenet) voices can save you money.
    
