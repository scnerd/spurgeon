import requests, re, os
from miniutils import parallel_progbar

months = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']
          
month_max = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
          
times = {'m': 'Morning', 'e': 'Evening'}

if __name__ == '__main__':
    base_url = 'https://www.biblegateway.com/audio/devotional/morning-and-evening'
    jobs = [(month, day, time)
            for month in range(12)
            for day in range(31)
            for time in 'me']
            
    base_path = './output/morneve_biblegateway'
            
    def fetch_mp3(month, day, time):
        if day > month_max[month]:
            return
        path = os.path.join(base_path, months[month], str(day+1), times[time], 'biblegateway.mp3')
        if os.path.exists(path):
            return
        
        signature = f'{month+1:02d}{day+1:02d}{time}'
        listening_page = f'{base_url}/{signature}'
        listening_page = requests.get(listening_page).content.decode()
        mp3_url = re.search(f'(http(?:s)?://.+?{signature}.+?\\.mp3)', listening_page)
        if mp3_url:
            mp3_data = requests.get(mp3_url.group(1)).content
            if len(mp3_data) > 100:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, 'wb').write(mp3_data)
                
    parallel_progbar(fetch_mp3, jobs, starmap=True)
