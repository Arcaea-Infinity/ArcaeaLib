import requests


class ParallelRequest:
    def __init__(self, Url, Thread, Times) -> None:
        self.Url = Url
        self.Thread = Thread
        self.Times
        self.ThreadTimes = [None for i in range(Thread)]

    async def Thread(self, ThreadId):
        print('Thread', ThreadId, 'started')
        self.ThreadTimes[ThreadId] = 0
        while 1:
            r = requests.get(self.Url)
            if r.status_code == 200:
                self.ThreadTimes[ThreadId] += 1


