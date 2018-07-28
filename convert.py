import json, requests, base64, os, re, subprocess
from collections import defaultdict
from miniutils import parallel_progbar

here = os.path.dirname(__file__)
morneve_dl_url = 'https://www.ccel.org/ccel/spurgeon/morneve.txt'


def convert_to_audio(text, mp3_path, auth, language, voice, gender):
    msg = dict(input=dict(text=text),
               voice=dict(languageCode=language,
                          name=voice,
                          ssmlGender=gender),
               audioConfig=dict(audioEncoding='MP3'))
    url = 'https://texttospeech.googleapis.com/v1beta1/text:synthesize'
    response = requests.post(url, json=msg, headers={'Authorization': f'Bearer {auth}'})
    audio = base64.b64decode(json.loads(response.content.decode())['audioContent'])
    open(mp3_path, 'wb').write(audio)


def process_morneve(path):
    devote_regex = re.compile(r'(Morning|Evening), (\w+) (\d+)\s+(?:\[\d+\][^\n]+$)?([\w\W]+)', re.MULTILINE)

    morneve = open(path).read()
    all_content = defaultdict(lambda: defaultdict(dict))

    for s in morneve.split('_' * 66):
        s = s.strip()
        mtch = devote_regex.match(s)
        if mtch:
            time, month, day, content = mtch.groups()
            day = int(day)
            content = content.strip()
            all_content[month][day][time] = content

    return all_content


def download_morneve(path):
    resp = requests.get(morneve_dl_url).decode()
    open(path, 'w').write(resp)


def main():
    morneve_path = os.path.join(here, 'morneve.txt')
    if not os.path.exists(morneve_path):
        download_morneve(morneve_path)
    devotionals = process_morneve(morneve_path)

    google_auth = subprocess.run(['gcloud', 'auth', 'application-default', 'print-access-token'], stdout=subprocess.PIPE).stdout.decode().strip()

    voices = [('en-gb', 'en-GB-Wavenet-D', 'MALE'), ('en-us', 'en-US-Wavenet-B', 'MALE')]

    jobs = [(month, day, time, voice_details)
            for month in devotionals
            for day in devotionals[month]
            for time in devotionals[month][day]
            for voice_details in voices]

    def create_audio_devotional(month, day, time, voice_details):
        try:
            mp3_path = os.path.join(here, 'output', 'morneve', month, str(day), time, '_'.join(voice_details) + '.mp3')
            if not os.path.exists(mp3_path):
                os.makedirs(os.path.dirname(mp3_path), exist_ok=True)
                content = devotionals[month][day][time]
                convert_to_audio(content, mp3_path, google_auth, *voice_details)
        except Exception:
            import traceback
            print('=' * 80)
            print("On job {month}-{day}-{time}, voice={voice_details}")
            print('=' * 80)
            traceback.print_exc()
            print('=' * 80)
            print('=' * 80)

    parallel_progbar(create_audio_devotional, jobs, starmap=True, nprocs=20)


if __name__ == '__main__':
    main()
