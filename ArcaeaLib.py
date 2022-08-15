# Arcaea Lib Script
# Ver 0.4.0.255stable by
# @Player01

# Video links collected by
# @Player01
# @MBRjun

# Open Source under MIT Lisence

'''
TODO List:

Rewrite ArcaeaSongs Lib									0%              # Highest priority
Rewrite the Aff System									60%
Arcaea Nickname System									5%
Song Name Comparing System								50%
Arc & Hold Note Count									95%
Arc Coordinate Calc										30%
RemoteDL Challenge Calc									0%
Phigros Chart Reader									30%
Phigros Renderer										0%
Phigros Chart and Arcaea Chart Converter				0%
'''

'''
Imports
'''
import _thread
from io import TextIOWrapper
import json
import os
import pprint
import re
import shutil
import time
import zipfile
import random
import math

from PIL import Image, ImageFilter
import requests

'''
Error Class Definations
'''
class AffError(Exception):
    def __init__(self, error: str, line: int = None) -> None:
        self.error = error
        self.line = line

    def __str__(self) -> str:
        if self.line == None: return self.error
        return self.error + ', in line ' + str(self.line)

class ResError(Exception):
    def __init__(self, error: str, file: str) -> None:
        self.error = error
        self.file = file

    def __str__(self) -> str:
        return self.error + ' in file ' + self.file

class RequestError(Exception):
    def __init__(self, url: str) -> None:
        self.url = url

    def __str__(self) -> str:
        return 'Error while requesting ' + self.url
'''
Draw pic for best30 and recent record card
'''
def whiteblur(image: Image, white_ratio, radius):
    image = image.convert('RGBA')
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            color = image.getpixel((x, y))
            color = color[:-1] + (int((255 - white_ratio) * 255),)
            image.putpixel((x, y), color)
    white_pic = Image.new('RGBA', image.size, (255, 255, 255, int(white_ratio*255)))
    image = Image.alpha_composite(image, white_pic)
    image = image.convert('RGB')
    return image.filter(ImageFilter.GaussianBlur(radius))

# Standard Arcaea Song Picture Size: 512*512
# Resize to 1024*1024

def best30_horizontal():
    pass

def best30_vertical():
    pass

def recent_v1(back, char, result):
    pass

def recent_v2(back, char, result):
    pass

def recent_v3(back, char, result):
    pass


'''
Utils
'''

def EnsurePath(Path):
    if Path.strip() == '':
        return '.\\'
    if Path[-1] == '\\':
        return Path
    return Path + '\\'


class BotRes:
    def __init__(self, path, filetype) -> None:
        self.path = path
        self.type = filetype

    def GetCode(self):
        pass


class BotMessageBuilder:
    def __init__(self, *args):
        self.Message = []
        self.Add(x for x in args)

    def Add(self, *args):
        pass

    def ToDataSegment(self):
        pass

class Log:
    def __init__(self, writefile: bool, logfile = None) -> None:
        self.writefile = writefile
        self.logfile = logfile

    def log(self, level, info, part=None): #level: Info, Output, Warning, Error
        color_dict = {'info': 37, 'output': 34, 'warning': 33, 'error': 31}
        if level.lower() not in color_dict.keys():
            self.log('warning', 'Unknown log level: ' + level, 'Log()')
            level = 'info'
        before_color = '\033[0;{0}m'.format(color_dict.get(level.lower()))
        fore_color = '\033[0m'
        time_str = time.strftime("[%Y/%m/%d] %H:%M:%S", time.localtime())
        if part == None: output = '[' + level.capitalize() + ']' + time_str + '\n' + pprint.pformat(info)
        else: output = '[' + level.capitalize() + ']' + time_str + '    ' + part + ':' + '\n' + pprint.pformat(info)
        print(before_color + output + fore_color)
        if self.writefile:
            file = open(self.logfile, 'a', encoding='utf-8')
            file.write(output + '\n\n')
            file.close()

def compare(inp: str, target: str):
    if inp.lower() == target.lower():
        return True
    def abbr(inp):
        abbrev = ''
        for i in inp.split(' '):
            if len(i) == 1:
                return ''
            abbrev += i[0]
        return abbrev
    if inp.lower() == abbr(target).lower():
        return True
    target = ''.join([char for char in target if char.isalnum() or char == ' '])
    if inp.lower() == abbr(target).lower() or inp.lower() == target.lower():
        return True
    if len(inp) > (len(target) / 3) and inp in target:
        return True
    return False


class MultiprocessDownload:
    # TODO
    # Download ane file with multithreads
    def __init__(self, url: str, path: str, filename: str, thread_num: int) -> None:
        try:
            if self.downloaded: raise Exception('This task is downloaded')
        except: pass
        self.downloaded = False
        self.url = url
        self.path = path
        self.filename = filename
        self.thread_num = thread_num
        self.threads = []
        self.head = requests.head(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}).headers
        self.length = int(self.head.get('Content-Length', False))
        self.proc = self.lock = [None for _ in range(self.thread_num)]
        if self.length < self.thread_num: raise ValueError('File length is smaller than thread_num')
        if self.thread_num >= 64: self.thread_num = 64
        if self.length == False: raise Exception('This file does not support multiprocess download')
        num = self.length // self.thread_num
        last = -1
        for i in range(1, thread_num + 1):
            self.threads.append([last + 1, num * i])
            last = num * i
        self.threads[-1][1] += self.length % self.thread_num

    def started(self) -> bool:
        for i in range(self.thread_num):
            if not os.path.exists('dl_block_' + str(i)):
                return False
        return True

    def thread(self, num) -> int:
        if self.downloaded: raise Exception('This task is downloaded')
        self.lock[num] = _thread.allocate_lock()
        with self.lock[num]:
            header = {'Range': f'bytes=' + str(self.threads[num][0]) + '-' + str(self.threads[num][1])}
            self.proc[num] = 0
            req = requests.get(self.url, headers=header, stream = True)
            blk_size = self.threads[num][1] - self.threads[num][0] + 1
            file = open('dl_block_' + str(num), 'wb')
            i = 0
            for chunk in req.iter_content(chunk_size=512):
                if chunk:
                    file.write(chunk)
                    i += 1
                    self.proc[num] = i * 512 / blk_size
            file.close()
        return 0

    def GetDownloadInfo(self) -> list:
        if self.downloaded: raise Exception('This task is downloaded')
        info = []
        total = 0
        for i in range(self.thread_num):
            if None in self.proc: return None
            info.append(str(self.proc[i] * 100) + '%')
            total += self.proc[i]
        info.append(str(total / self.thread_num * 100) + '%') #[*threads_info, total_info]
        return info

    def run(self):
        if self.downloaded: raise Exception('This task is downloaded')
        for i in range(self.thread_num):
            _thread.start_new_thread(self.thread, (i,))
        locked = 1
        while locked:
            if not self.started(): continue
            print(self.GetDownloadInfo())
            locked = 0
            print(self.lock)
            for n in range(self.thread_num):
                if self.lock[n].locked():
                    locked += 1
            time.sleep(5)
        target = open(self.path + self.filename, 'wb')
        for num in range(self.thread_num):
            blk = open('dl_block_' + str(num), 'rb')
            target.write(blk.read())
            blk.close()
            os.remove('dl_block_' + str(num))
        target.close()
        self.downloaded = True

def FormatScore(score: int) -> int:
    score = str(score)
    if len(score) > 8:
        raise ValueError('Score must be under 8 digits')
    score = score.zfill(8)
    return "'".join([score[:2], score[2:5], score[5:8]])

'''
Aff(Beta): Parse aff file and calc Arc & Hold's JugdeTimings and NotesCount
Notes count for Arc & Hold not complete
Will append Arc Coodinate Calc in the future
'''
class Timing:
    def __init__(self, Time: int, BPM: float, Beats: float, TiminggroupId: int) -> None:
        self.StartTime = Time
        self.BPM = BPM
        self.Beats = Beats
        self.TiminggroupId = TiminggroupId
        self.Count = 0

    def __str__(self) -> str:
        return 'timing(' + str(self.StartTime) + ',' + '%.2f'% self.BPM + ',' + '%.2f'% self.Beats + ')' + ';'

class Aff: pass

class TiminggroupProperties:
    def __init__(self, NoInput: bool, FadingHolds: bool, AngleX: int, AngleY: int, TiminggroupId: int, Chart: Aff) -> None:
        self.TiminggroupId = TiminggroupId
        self.NoInput = NoInput
        self.FadingHolds = FadingHolds
        self.AngleX = AngleX
        self.AngleY = AngleY
        self.StartTime = 0
        self.Count = 0
        self.__Chart = Chart

    def GetTimings(self) -> None:
        self.Timings = [i for i in self.__Chart.Events if i.TiminggroupId == self.TiminggroupId and isinstance(i, Timing)]

    def SetSelfStartTime(self) -> None:
        for i in self.__Chart.Events:
            if i.TiminggroupId == self.TiminggroupId and not (isinstance(i, TiminggroupProperties) or isinstance(i, Timing)):
                self.StartTime = i.StartTime
                return None
        self.StartTime = self.Timings[0].StartTime

    def Update(self) -> None:
        self.GetTimings()
        self.SetSelfStartTime()

    def GetBPMByTiming(self, Time: int) -> float:
        for i in range(len(self.Timings)):
            if self.Timings[i].StartTime == Time: return self.Timings[i].BPM
            elif self.Timings[i].StartTime > Time: return self.Timings[i - 1].BPM
        if self.Timings[-1:][0].StartTime <= Time: return self.Timings[-1:][0].BPM
        # for i in range(len(self.Timings)):
        #     if self.Timings[i].StartTime == Time and self.Timings[i].BPM != 0.0: return self.Timings[i].BPM
        #     elif self.Timings[i].StartTime > Time and self.Timings[i].BPM != 0.0: return self.Timings[i - 1].BPM
        #     else:
        #         for n in range(i, 0, -1):
        #             if self.Timings[n].BPM != 0.0: return self.Timings[n].BPM
        # raise AffError('No Valid Timing Error')

    def __str__(self) -> str:
        # Args = ''
        # if self.NoInput: Args += 'noinput_'
        # if self.FadingHolds: Args += 'fadingholds_'
        # if self.AngleX: Args += ('anglex' + str(self.AngleX) + '_')
        # if self.AngleY: Args += ('angley' + str(self.AngleY) + '_')
        # if Args != '':
        #     Args = Args[:-1]
        Args = []
        if self.NoInput: Args.append('noinput')
        if self.FadingHolds: Args.append('fadingholds')
        if self.AngleX: Args.append('anglex' + str(self.AngleX))
        if self.AngleY: Args.append('angley' + str(self.AngleY))
        return 'timinggroup(' + ('_'.join(Args) if Args != [] else '') + ')'

class Arc: pass

class Arctap:
    def __init__(self, Time: int) -> None:
        self.StartTime = Time

    def SetArc(self, arc: Arc) -> None:
        self.Arc = arc

    @property
    def Effect(self) -> None or str:
        try:
            return self.Arc.Effect
        except:
            return None

    def GetX(self):
        return self.Arc.GetXAtTiming(self.StartTime)

    def GetY(self):
        return self.Arc.GetYAtTiming(self.StartTime)

    def __str__(self) -> str:
        return 'arctap(' + str(self.StartTime) + ')'

    @property
    def Count(self) -> int:
        return 0 if self.Arc.NoInput else 1

# ArcAlgorithm
ArcXToWorld = lambda x:-8.5 * x + 4.25
ArcYToWorld = lambda y:1 + 4.5 * y
WorldXToArc = lambda x:(x - 4.25) / -8.5
WorldYToArc = lambda y:(y - 1) / 4.5
S = lambda start,end,t:(1 - t) * start + end * t
O = lambda start,end,t:start + (end - start) * (1 - math.cos(1.57079625 * t))
I = lambda start,end,t:start + (end - start) * math.sin(1.57079625 * t)
B = lambda start,end,t:math.pow((1 - t), 3) * start + 3 * math.pow((1 - t), 2) * t * start + 3 * (1 - t) * math.pow(t, 2) * end + math.pow(t, 3) * end

def X(start: float, end: float, t: float, ArcEasingType: str):
    if ArcEasingType == 'b':
        return B(start, end, t)
    if ArcEasingType == 'siso':
        return I(start, end, t)
    if ArcEasingType == 'soso':
        return O(start, end, t)
    return S(start, end, t)

def Y(start: float, end: float, t: float, ArcEasingType: str):
    if ArcEasingType == 'b':
        return B(start, end, t)
    if ArcEasingType == 'sosi':
        return I(start, end, t)
    if ArcEasingType == 'soso':
        return O(start, end, t)
    return S(start, end, t)

def Qi(value: float):
    return value * value * value

def Qo(value: float):
    return (value - 1) * (value - 1) * (value - 1) + 1

class Arc:
    def __init__(self, StartTime: int, EndTime: int, XStart: float, XEnd: float, EasingType: str, YStart: float, YEnd: float, Color: int, Effect: str, IsSkyline: bool, TimingPointDensityFactor: float, TiminggroupId: int, Timinggroup: TiminggroupProperties) -> None:
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.XStart = XStart
        self.XEnd = XEnd
        self.EasingType = EasingType
        self.YStart = YStart
        self.YEnd = YEnd
        self.Color = Color
        self.Effect = Effect
        self.IsSkyLine = IsSkyline
        self.Arctaps = []
        self.TimingPointDensityFactor = TimingPointDensityFactor
        self.TiminggroupId = TiminggroupId
        self.TiminggroupProperties = Timinggroup
        # By yyyr
        '''
		public void CalculateJudgeTimings()
		{
			JudgeTimings.Clear();
			if (IsVoid || EndTiming == Timing)
			{
				return;
			}
			int num = ((!RenderHead) ? 1 : 0);
			double num2 = ArcTimingManager.Instance[TimingGroup].CalculateBpmByTiming(Timing);
			if (num2 <= 0.0)
			{
				num2 = 0.0 - num2;
			}
			double num3 = 60000.0 / num2 / (double)((num2 >= 255.0) ? 1 : 2) / ArcGameplayManager.Instance.TimingPointDensityFactor;
			int num4 = (int)((double)(EndTiming - Timing) / num3);
			if ((num ^ 1) >= num4)
			{
				JudgeTimings.Add((int)((float)Timing));// + (float)(EndTiming - Timing) * 0.5f));
				return;
			}
			int num5 = num ^ 1;
			do
			{
				int num6 = (int)((double)Timing + (double)num5 * num3);
				if (num6 < EndTiming)
				{
					JudgeTimings.Add(num6);
				}
			}
			while (num4 != ++num5);
		}
        '''
    def CalcJudgeTimings(self) -> None:
        self.JudgeTimings = []
        if self.NoInput or self.StartTime == self.EndTime or self.IsSkyLine or self.Arctaps: return None
        #int num = ((!RenderHead) ? 1 : 0);
        #self.JudgeHead: bool
        Head = not self.JudgeHead if 1 else 0 
        BPM = abs(self.TiminggroupProperties.GetBPMByTiming(self.StartTime))
        if BPM >= 255.0: x = 1.0
        else: x = 2.0
        try:
            PartitionIndex = 60000.0 / BPM / x / self.TimingPointDensityFactor
        except:
            return None
        Point = int((self.EndTime - self.StartTime) / PartitionIndex)
        if Head ^ 1 >= Point:
            self.JudgeTimings.append(self.StartTime)
            return None
        JudgeTiming = int(self.StartTime + (Head ^ 1) * PartitionIndex)
        if JudgeTiming < self.EndTime: self.JudgeTimings.append(JudgeTiming)
        Judge = Head ^ 1
        while Point != Judge + 1:
            Judge += 1
            JudgeTiming = int(self.StartTime + Judge * PartitionIndex)
            if JudgeTiming < self.EndTime: self.JudgeTimings.append(JudgeTiming)
        # print("Arc JudgeTimings:", self.JudgeTimings)

    def Update(self):
        for i in self.Arctaps:
            i.SetArc(self)

    def GetXAtTiming(self, t: int):
        t2 = (t - self.StartTime) / (self.EndTime - self.StartTime)
        return X(self.XStart, self.XEnd, t2, self.EasingType)

    def GetYAtTiming(self, t: int):
        t2 = (t - self.StartTime) / (self.EndTime - self.StartTime)
        return Y(self.YStart, self.YEnd, t2, self.EasingType)

    def AddArcTap(self, arctap: Arctap):
        if arctap.StartTime > self.EndTime or arctap.StartTime < self.StartTime:
            raise AffError("Arctap Time Invalid")
        if not self.IsSkyLine:
            raise AffError("Try to add arctap into an non-skyline arc")
        arctap.SetArc(self)
        self.Arctaps.append(arctap)

    def __str__(self) -> str:
        Arctaps = ((str([i.__str__() for i in self.Arctaps])).replace(' ', '')).replace("'",'') if self.Arctaps else ''
        return 'arc(' + str(self.StartTime) + ',' + str(self.EndTime) + ',' + '%.2f'% self.XStart + ',' + '%.2f'% self.XEnd + ',' + self.EasingType + ',' + '%.2f'% self.YStart + ',' + '%.2f'% self.YEnd + ',' + str(self.Color) + ',' + self.Effect + ',' + (str(self.IsSkyLine)).lower() + ')' + Arctaps + ';'

    @property
    def Count(self) -> int:
        self.Update()
        if not self.NoInput:
            if self.IsSkyLine: #ArcTaps, Skyline
                return len(self.Arctaps)
            else: #Arc
                return len(self.JudgeTimings)
        else: return 0

    @property
    def NoInput(self) -> bool:
        return self.TiminggroupProperties.NoInput

    @property
    def AngleX(self) -> int:
        return self.TiminggroupProperties.AngleX

    @property
    def AngleY(self) -> int:
        return self.TiminggroupProperties.AngleY


class Tap:
    def __init__(self, Time: int, Lane: int, TiminggroupId: int, Timinggroup: TiminggroupProperties) -> None:
        self.StartTime = Time
        self.Lane = Lane
        self.TiminggroupId = TiminggroupId
        self.TiminggroupProperties = Timinggroup

    def __str__(self) -> str:
        return '(' + str(self.StartTime) + ',' + str(self.Lane) + ')' + ';'

    @property
    def NoInput(self) -> bool:
        return self.TiminggroupProperties.NoInput

    @property
    def Count(self) -> int:
        return 0 if self.NoInput else 1

class Hold:
    def __init__(self, StartTime: int, EndTime: int, Lane: int, TimingPointDensityFactor: float, TiminggroupId: int, Timinggroup: TiminggroupProperties) -> None:
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.Lane = Lane
        self.TimingPointDensityFactor = TimingPointDensityFactor
        self.TiminggroupId = TiminggroupId
        self.TiminggroupProperties = Timinggroup
        # By yyyr
        '''
		public void CalculateJudgeTimings()
		{
			JudgeTimings.Clear();
			int num = 0;
			double num2 = ArcTimingManager.Instance[TimingGroup].CalculateBpmByTiming(Timing);
			if (num2 <= 0.0)
			{
				num2 = 0.0 - num2;
			}
			double num3 = 60000.0 / num2 / (double)((num2 >= 255.0) ? 1 : 2) / ArcGameplayManager.Instance.TimingPointDensityFactor;
			int num4 = (int)((double)(EndTiming - Timing) / num3);
			if ((num ^ 1) >= num4)
			{
				JudgeTimings.Add((int)((float)Timing + (float)(EndTiming - Timing) * 0.5f));
				return;
			}
			int num5 = num ^ 1;
			do
			{
				int num6 = (int)((double)Timing + (double)num5 * num3);
				if (num6 < EndTiming)
				{
					JudgeTimings.Add(num6);
				}
			}
			while (num4 != ++num5);
		}
        '''
    def CalcJudgeTimings(self) -> None:
        self.JudgeTimings = []
        num = 0
        BPM = abs(self.TiminggroupProperties.GetBPMByTiming(self.StartTime))
        if BPM >= 255.0: x = 1.0
        else: x = 2.0
        try:
            PartitionIndex = 60000.0 / BPM / x / self.TimingPointDensityFactor
        except:
            return None
        Point = int((self.EndTime - self.StartTime) / PartitionIndex)
        if (num ^ 1) >= Point:
            JudgeTiming = int(float(self.StartTime) + float(self.EndTime - self.StartTime) * 0.5)
            self.JudgeTimings.append(JudgeTiming)
            return None
        JudgeTiming = int(self.StartTime + (num ^ 1) * PartitionIndex)
        if JudgeTiming < self.EndTime: self.JudgeTimings.append(JudgeTiming)
        Judge = num ^ 1
        while Point != Judge + 1:
            Judge += 1
            JudgeTiming = int(self.StartTime + Judge * PartitionIndex)
            if JudgeTiming < self.EndTime: self.JudgeTimings.append(JudgeTiming)
        # print("Hold JudgeTimings:", self.JudgeTimings)

    def Update(self) -> None:
        if not self.NoInput:
            self.CalcJudgeTimings()

    def __str__(self) -> str:
        return 'hold(' + str(self.StartTime) + ',' + str(self.EndTime) + ',' + str(self.Lane) + ')' + ';'

    @property
    def NoInput(self) -> bool:
        return self.TiminggroupProperties.NoInput

    @property
    def FadingHolds(self) -> bool:
        return self.TiminggroupProperties.FadingHolds

    @property
    def Count(self) -> int:
        self.Update()
        return len(self.JudgeTimings)

class Camera:
    def __init__(self, StartTime: int, Transverse: float, BottomZoom: float, LineZoom: float, SteadyAngle: float, TopZoom: float, RotateAngle: float, EasingType: str, LastingTime: int, TiminggroupId: int, Timinggroup: TiminggroupProperties) -> None:
        self.StartTime = StartTime
        self.Transverse = Transverse
        self.BottomZoom = BottomZoom
        self.LineZoom = LineZoom
        self.SteadyAngle = SteadyAngle
        self.TopZoom = TopZoom
        self.RotateAngle = RotateAngle
        self.EasingType = EasingType
        self.LastingTime = LastingTime
        self.EndTime = self.StartTime + self.LastingTime
        self.TiminggroupId = TiminggroupId
        self.TiminggroupProperties = Timinggroup
        self.Count = 0

    def __str__(self) -> str:
        return 'camera(' + str(self.StartTime) + ',' + str(self.Transverse) + ',' + str(self.BottomZoom) + ',' + str(self.LineZoom) + ',' + str(self.SteadyAngle) + ',' + str(self.TopZoom) + ',' + str(self.RotateAngle) + ',' + str(self.EasingType) + ',' + str(self.LastingTime) + ')' + ';'

class SceneControl:
    def __init__(self, args, TiminggroupId: int, Timinggroup: TiminggroupProperties) -> None:
        self.Count = 0
        self.TiminggroupId = TiminggroupId
        self.TiminggroupProperties = Timinggroup
        self.args = args
        self.StartTime = args[0]
        self.Type = args[1]
        if len(args) == 2: #scenecontrol(t,type);
            pass # Nothing to do
        elif len(args) == 4:
            self.Param1 = args[2]
            self.Param2 = args[3]


    def __str__(self) -> str:
        args = ''
        for i in self.args:
            args += str(i) if not isinstance(i, float) else '%.2f'% i
            args += ','
        args = args[:-1]
        return 'scenecontrol(' + args + ')' + ';'


class Flick:
    def __init__(self, Time: int, X: float, Y: float, FX: float, FY: float, TiminggroupId: int, Timinggroup: TiminggroupProperties):
        self.StartTime = Time
        self.X = X
        self.Y = Y
        self.FX = FX
        self.FY = FY
        self.TiminggroupId = TiminggroupId
        self.TiminggroupProperties = Timinggroup

    def __str__(self) -> str:
        return 'flick(' + str(self.StartTime) + ',' + '%.2f'% self.X + ',' + '%.2f'% self.Y + ',' + '%.2f'% self.FX + ',' + '%.2f'% self.FY + ')' + ';'

    @property
    def NoInput(self) -> bool:
        return self.TiminggroupProperties.NoInput

    @property
    def Count(self) -> int:
        return 0 if self.NoInput else 1

def formatAffCmd(cmd):
    cmd = cmd.strip('(')
    cmd = cmd.strip(')')
    cmd = cmd.split(',')
    index = -1
    for i in cmd:
        index += 1
        if '.' in i:
            try:
                cmd[index] = float(i)
            except:
                pass
        else:
            try:
                cmd[index] = int(i)
            except:
                pass
    cmd = [True if x == 'true' else x for x in cmd]
    cmd = [False if x == 'false' else x for x in cmd]
    return cmd


class Aff:
    def __init__(self) -> None:
        self.IsLoaded = False

    @staticmethod
    def IsValidAff(aff_text: str):
        aff_text = aff_text.splitlines()
        s = aff.index('-')
        aff = [aff[:s]] + [aff[s + 1:]]
        error = 0
        AudioOffsetCount = 0
        TimingPointDensityFactorCount = 0
        for i in aff:
            try:
                i.split(':')
                if i[0] == 'AudioOffset':
                    AudioOffsetCount += 1
                elif i[0] == 'TimingPointDensityFactor':
                    TimingPointDensityFactorCount += 1
                else: error += 1
            except: #Use Regex to match Aff Commands
                pass

    def New(self):
        try:
            if self.IsLoaded: raise Exception('Aff Already Loaded')
        except:
            pass 
        self.Events = []
        self.AudioOffset = 0
        self.TimingPointDensityFactor = 1.0
        self.IsLoaded = True

    def Load(self, file: str or TextIOWrapper) -> None:
        try:
            if self.IsLoaded: raise Exception('Aff Already Loaded')
        except:
            pass
        aff = None
        if type(file) == str:
            try:
                file = open(file, 'r', encoding='utf-8')
                aff = file.read().splitlines()
            except:
                pass
        elif type(file) == TextIOWrapper:
            aff = file.read().splitlines()
        if aff == None: raise AffError('failed to open or read aff file: ' + file)
        s = aff.index('-')
        aff = [aff[:s]] + [aff[s + 1:]]
        self.Events = []
        self.AudioOffset = None
        self.TimingPointDensityFactor = 1.0
        for i in aff[0]:
            i = i.split(':')
            if i[0] == 'AudioOffset':
                self.AudioOffset = int(i[1])
            elif i[0] == 'TimingPointDensityFactor':
                self.TimingPointDensityFactor = float(i[1])
        if self.AudioOffset == None:
            raise AffError('AudioOffset not set')
        TiminggroupId = 0 #0: No Timinggroup
        MaxTiminggroup = 0
        line = 0
        NoInput = False
        FadingHolds = False
        AngleX = 0
        AngleY = 0
        self.TiminggroupProperties = []
        for i in aff[1]:
            if line == 0:
                FirstTiming = self.proceed(i, TiminggroupId, len(aff[0]) + 1 + line + 1)
                if not isinstance(FirstTiming, Timing):
                    raise AffError('First Aff Command not a timing')
                Timinggroup = TiminggroupProperties(False, False, 0, 0, 0, self)
                self.TiminggroupProperties.append(Timinggroup)
                self.Events.append(FirstTiming)
                self.Events.append(Timinggroup)
                line += 1
                continue
            line += 1
            if i.startswith('};'):
                NoInput = False
                FadingHolds = False
                TiminggroupId = 0
                AngleX = 0
                AngleY = 0
            elif i.startswith('timinggroup'):
                MaxTiminggroup += 1
                TiminggroupId = MaxTiminggroup
                cmd = i.strip('timinggroup').strip().strip('{')
                args = formatAffCmd(cmd)
                timinggroupArgs = args[0].split('_')
                for i in timinggroupArgs:
                    if i == 'noinput':
                        NoInput = True
                    elif i == 'fadingholds':
                        FadingHolds = True
                    elif i.startswith('anglex'):
                        AngleX = i[6:]
                    elif i.startswith('angley'):
                        AngleY = i[6:]
                    elif i == '':
                        pass
                    else: raise AffError('Unknow timinggroup type')
                Timinggroup = TiminggroupProperties(NoInput, FadingHolds, AngleX, AngleY, TiminggroupId, self)
                self.TiminggroupProperties.append(Timinggroup)
                self.Events.append(Timinggroup)
            else:
                self.Events.append(self.proceed(i, TiminggroupId, len(aff[0]) + 1 + line))
        try:
            self.Events.remove(None)
        except:
            pass
        self.Refresh()
        self.IsLoaded = True

    def proceed(self, i, TiminggroupId: int, line: int):
        i = i.strip().strip(';')
        if i.strip() == '':
            return None
        elif i.startswith('timing') and not i.startswith('timinggroup'):
            args = i.strip('timing')
            args = formatAffCmd(args)
            return Timing(args[0], args[1], args[2], TiminggroupId)
        if i.startswith('arc'):
            ArcCommand = re.match(r'arc\(.*?\)', i)
            if ArcCommand == None: raise AffError('Arc regex not matched', line = line)
            ArcCommand = ArcCommand.group()
            ArcCommand = ArcCommand.strip('arc')
            ArcArguments = formatAffCmd(ArcCommand)
            ArctapArgs = []
            Arctaps = []
            if i.find('arctap') >= 0:
                ArctapCommand = re.search(r'(arctap\([0-9]+\),)*arctap\([0-9]+\)', i)
                if ArctapCommand == None: AffError('Arctap regex not matched', line = line)
                ArctapCommand = ArctapCommand.group()
                ArctapCommand = ArctapCommand.strip('[').strip(']')
                ArctapCommand = ArctapCommand.split(',')
                for c in ArctapCommand:
                    ArctapArgs.append(int(c.strip('arctap(').strip(')')))
                for n in ArctapArgs:
                    Arctaps.append(Arctap(n))
            arc = Arc(ArcArguments[0], ArcArguments[1], ArcArguments[2], ArcArguments[3], ArcArguments[4], ArcArguments[5], ArcArguments[6], ArcArguments[7], ArcArguments[8], ArcArguments[9], self.TimingPointDensityFactor, TiminggroupId, self.TiminggroupProperties[TiminggroupId])
            for arctap in Arctaps:
                arc.AddArcTap(arctap)
            return arc
        elif i.startswith('hold'):
            args = formatAffCmd(i.strip('hold').strip(';'))
            return Hold(args[0], args[1], args[2], self.TimingPointDensityFactor, TiminggroupId, self.TiminggroupProperties[TiminggroupId])
        elif i.startswith('scenecontrol'):
            args = formatAffCmd(i.strip('scenecontrol').strip(';'))
            return SceneControl(args, TiminggroupId, self.TiminggroupProperties[TiminggroupId])
        elif i.startswith('flick'):
            args = formatAffCmd(i.strip('flick').strip(';'))
            return Flick(args[0], args[1], args[2], args[3], args[4], TiminggroupId, self.TiminggroupProperties[TiminggroupId])
        elif i.startswith('camera'):
            args = formatAffCmd(i.strip('camera').strip(';'))
            return Camera(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], TiminggroupId)
        elif i[0] == '(' and i[-1:] == ')': #Tap
            args = formatAffCmd(i.strip(';'))
            return Tap(args[0], args[1], TiminggroupId, self.TiminggroupProperties[TiminggroupId])
        else:
            raise AffError('Unknow aff command', line=line)

    def CountNotes(self) -> list:
        tap = 0
        hold = 0
        arc = 0
        arctap = 0
        flick = 0
        for i in self.Events:
            if isinstance(i, Tap):
                if not i.NoInput:
                    tap += 1
            if isinstance(i, Hold):
                if not i.NoInput:
                    hold += i.Count
            if isinstance(i, Arc):
                if not i.NoInput:
                    if i.Arctaps:
                        arctap += len(i.Arctaps)
                    else:
                        arc += i.Count
            if isinstance(i, Flick):
                if not i.NoInput:
                    flick +=1
        return [tap + hold + arc + arctap + flick, tap, hold, arc, arctap, flick] # TotalNotes, TapNotes, HoldNotes, ArcNotes, ArcTapNotes, FlickNotes
    # By yyyr
    '''
	public void CalculateArcRelationship()
	{
		foreach (ArcArc arc in Arcs)
		{
			arc.ArcGroup = null;
			arc.RenderHead = true;
			arc.RenderEnd = true;
		}
		foreach (ArcArc arc2 in Arcs)
		{
			foreach (ArcArc arc3 in Arcs)
			{
				if (arc2 == arc3 || !(Mathf.Abs(arc2.XEnd - arc3.XStart) < 0.1f) || Mathf.Abs(arc2.EndTiming - arc3.Timing) > 9 || arc2.YEnd != arc3.YStart || arc2.TimingGroup != arc3.TimingGroup)
				{
					continue;
				}
				if (arc3.Timing - arc2.EndTiming > 0 && !(arc2.Timing == arc2.EndTiming || arc3.Timing == arc3.EndTiming))
                    {
					arc2.arcRenderer.RebuildSegmentsAndColliderWithEndTiming(arc3.Timing);
                    }
				if (arc2.IsVoid == arc3.IsVoid && (arc2.IsVoid == arc3.IsVoid == true || arc2.Color == arc3.Color))
				{
					if (arc2.ArcGroup == null && arc3.ArcGroup != null)
					{
						arc2.ArcGroup = arc3.ArcGroup;
					}
					else if (arc2.ArcGroup != null && arc3.ArcGroup == null)
					{
						arc3.ArcGroup = arc2.ArcGroup;
					}
					else if (arc2.ArcGroup != null && arc3.ArcGroup != null)
					{
						foreach (ArcArc item in arc3.ArcGroup)
						{
							if (!arc2.ArcGroup.Contains(item))
							{
								arc2.ArcGroup.Add(item);
							}
						}
						arc3.ArcGroup = arc2.ArcGroup;
					}
					else if (arc2.ArcGroup == null && arc3.ArcGroup == null)
					{
						arc2.ArcGroup = (arc3.ArcGroup = new List<ArcArc> { arc2, arc3 });
					}
					if (!arc2.ArcGroup.Contains(arc3))
					{
						arc2.ArcGroup.Add(arc3);
					}
					if (!arc3.ArcGroup.Contains(arc2))
					{
						arc3.ArcGroup.Add(arc2);
					}
					arc3.RenderHead = false;
					arc2.RenderEnd = false;
				}
			}
		}
		foreach (ArcArc arc4 in Arcs)
		{
			if (arc4.ArcGroup == null)
			{
				arc4.ArcGroup = new List<ArcArc> { arc4 };
			}
			arc4.ArcGroup.Sort((ArcArc a, ArcArc b) => a.Timing.CompareTo(b.Timing));
		}
		foreach (ArcArc arc5 in Arcs)
		{
			arc5.CalculateJudgeTimings();
		}
	}
    '''
    def CalcArcRelationship(self) -> None:
        for i in self.Events:
            if isinstance(i, Arc):
                i.ArcGroup = None
                i.JudgeHead = True
                i.JudgeEnd = True
        for i in self.Events:
            if isinstance(i, Arc):
                if not i.IsSkyLine:
                    for n in self.Events:
                        if isinstance(n, Arc):
                            if not n.IsSkyLine:
                                if i == n or not abs(i.XEnd - n.XStart) < 0.1 or abs(i.EndTime - n.StartTime) > 9 or i.YEnd != n.YStart: continue
                                if n.StartTime - i.EndTime > 0 and not (i.StartTime == i.EndTime or n.StartTime == n.EndTime): pass #arc2.arcRenderer.RebuildSegmentsAndColliderWithEndTiming(arc3.Timing);
                                if i.NoInput == n.NoInput and (i.NoInput == n.NoInput == True or i.Color == n.Color):
                                    if i.ArcGroup == None and n.ArcGroup != None:
                                        i.ArcGroup = n.ArcGroup
                                    elif i.ArcGroup != None and n.ArcGroup == None:
                                        n.ArcGroup = i.ArcGroup
                                    elif i.ArcGroup != None and n.ArcGroup != None:
                                        for item in n.ArcGroup:
                                            if isinstance(item, Arc):
                                                if item not in i.ArcGroup:
                                                    i.ArcGroup.append(item)
                                                n.ArcGroup = i.ArcGroup
                                    elif i.ArcGroup == None and n.ArcGroup == None:
                                        i.ArcGroup = n.ArcGroup = [i, n]
                                    if n not in i.ArcGroup:
                                        i.ArcGroup.append(n)
                                    if i not in n.ArcGroup:
                                        n.ArcGroup.append(i)
                                    i.JudgeEnd = n.JudgeHead = False
        # def SortArcListByStartTime(ArcList: list) -> list:
        #     for i in range(len(ArcList)):
        #         for n in range(len(ArcList)):
        #             if i == n or ArcList[i].StartTime == ArcList[n].StartTime: pass
        #             if ArcList[i].StartTime > ArcList[n].StartTime or ArcList[i].StartTime < ArcList[n].StartTime:
        #                 ArcList[i], ArcList[n] = ArcList[n], ArcList[i]
        #     return ArcList
        key = lambda arc: arc.StartTime
        for i in self.Events:
            if isinstance(i, Arc):
                if i.ArcGroup == None:
                    i.ArcGroup = [i]
                i.ArcGroup.sort(key=key)
        for i in self.Events:
            if isinstance(i, Arc):
                i.CalcJudgeTimings()
                i.Update()

    def Refresh(self):
        for i in self.Events:
            if isinstance(i, TiminggroupProperties):
                i.Update()
            if isinstance(i, Hold):
                i.Update()
        self.Events.sort(key = lambda x:x.StartTime)
        self.CalcArcRelationship()

    def SetTimingPointDensityFactor(self, TimingPointDensityFactor: float):
        self.TimingPointDensityFactor = TimingPointDensityFactor
        self.Refresh()

    def SetAudioOffset(self, AudioOffset: float):
        self.AudioOffset = AudioOffset
        self.Refresh()

    def AddEvent(self, Event):
        self.Events.append(Event)
        self.Refresh()

    def Chart(self) -> str:
        ChartString = ''
        ChartString += ('AudioOffset:' + str(self.AudioOffset) + '\n')
        if self.TimingPointDensityFactor != 1.0:
            ChartString += ('TimingPointDensityFactor:' + str(self.TimingPointDensityFactor) + '\n')
        ChartString += '-\n'
        MaxTiminggroupId = 0
        for i in self.Events:
            if i.TiminggroupId > MaxTiminggroupId:
                MaxTiminggroupId = i.TiminggroupId
        for i in self.Events:
            if isinstance(i, TiminggroupProperties) and i.TiminggroupId == 0: pass
            elif i.TiminggroupId == 0:
                ChartString += (i.__str__() + '\n')
        for i in self.Events:
            if isinstance(i, TiminggroupProperties) and i.TiminggroupId != 0:
                ChartString += (i.__str__() + '{\n')
                for n in self.Events:
                    if n.TiminggroupId == i.TiminggroupId and not isinstance(n, TiminggroupProperties):
                        ChartString += ('  ' + n.__str__() + '\n')
                ChartString += '};\n'
        return ChartString

    def Save(self, FilePath) -> None:
        ChartFile = open(FilePath, 'w', encoding='utf-8')
        ChartFile.write(self.Chart())
        ChartFile.close()

    def CreateNewChartMigratingTimings(self) -> Aff:
        EventsNeedMigrate = []
        for i in self.Events:
            if isinstance(i, Timing) and i.TiminggroupId == 0:
                EventsNeedMigrate.append(i)
        aff = Aff()
        aff.New()
        aff.SetAudioOffset(self.AudioOffset)
        aff.SetTimingPointDensityFactor(self.TimingPointDensityFactor)
        for i in EventsNeedMigrate:
            aff.AddEvent(i)
        return aff

    def RandomizeChart(self):
        for i in self.Events:
            if isinstance(i, Hold) or isinstance(i, Tap):
                if self.InEnwidenLaneRange(i.StartTime):
                    old = i.__str__()
                    i.Lane = random.randint(0, 5)
                    print('6k note detected', old, '=>', i.__str__())
                else:
                    i.Lane = random.randint(1, 4)
            elif isinstance(i, Arc):
                point = random.randint(0, 1)
                if point == 0:
                    i.XEnd, i.YEnd = i.YEnd, i.XEnd
                elif point == 1:
                    i.XStart, i.YStart = i.YStart, i.XStart

    def InEnwidenLaneRange(self, Timing: int) -> bool:
        enwidens = []
        for i in self.Events:
            if isinstance(i, SceneControl) and i.Type == 'enwidenlanes':
                enwidens.append(i)
        if len(enwidens) == 0:
            return False
        elif len(enwidens) == 1:
            if enwidens[0].StartTime <= Timing:
                return True
            return False
        enwidens.sort(key = lambda sc:sc.StartTime)
        # Match last enwidenlanes event
        last = None
        for i in range(len(enwidens)):
            if enwidens[i].StartTime <= Timing:
                if i == len(enwidens) - 1:
                    last = enwidens[i]
                elif enwidens[i + 1].StartTime > Timing:
                    last = enwidens[i]
        if last:
            return last.Param2
        return False


'''
ArcaeaSongs: Parse packlist, songlist, unlocks from an Arcaea APK file
'''
class ArcaeaSongs: pass
class Difficulties:
    def __init__(self) -> None:
        return None

    def LoadFromDifficultiesList(self, DifficultiesList: dict) -> None:
        self.Raw = DifficultiesList
        self.Difficulties = []
        for i in DifficultiesList:
            difficulty = Difficulty()
            difficulty.LoadFromDifficultyDict(i)
            self.Difficulties.append(difficulty)
        self.BeyondBool = True if len(self.Difficulties) == 4 else False

    def GetDifficultyByRatingClass(self, ratingClass: int):
        for i in self.Difficulties:
            if i.ratingClass == ratingClass:
                return i
        return None


class Difficulty:
    def __init__(self) -> None:
        return None

    def LoadFromDifficultyDict(self, DifficultyDict: dict) -> None:
        self.Raw = DifficultyDict
        self.ratingClass = DifficultyDict['ratingClass']
        self.chartDesigner = DifficultyDict.get('chartDesigner')
        self.jacketDesigner = DifficultyDict.get('jacketDesigner')
        self.ratingPlus = DifficultyDict.get('ratingPlus')
        self.rating = DifficultyDict.get('rating')
        self.plusFingers = DifficultyDict.get('plusFingers')
        self.jacketOverride = DifficultyDict.get('jacketOverride')
        self.audioOverride = DifficultyDict.get('audioOverride')
        self.hidden_until_unlocked = DifficultyDict.get('hidden_until_unlocked')
        self.hidden_until = DifficultyDict.get('hidden_until')
        self.world_unlock = DifficultyDict.get('world_unlock')

    @property
    def ratingString(self):
        return str(self.rating) + ('+' if self.ratingPlus else '')


class Song:
    def __init__(self) -> None:
        pass

    def LoadFromSongDict(self, SongDict: dict) -> None:
        self.Raw = SongDict
        self.idx = SongDict['idx']
        self.id = SongDict['id']
        self.title_localized = SongDict['title_localized']
        self.artist = SongDict['artist']
        self.bpm = SongDict['bpm']
        self.bpm_base = SongDict['bpm_base']
        self.set = SongDict['set']
        self.purchase = SongDict.get('purchase')
        self.audioPreview = SongDict.get('audioPreview')
        self.audioPreviewEnd = SongDict.get('audioPreviewEnd')
        self.side = SongDict.get('side')
        self.bg = SongDict.get('bg')
        self.remote_dl = SongDict.get('remote_dl')
        self.source_copyright = SongDict.get('source_copyright')
        self.world_unlock = SongDict.get('world_unlock')
        self.songlist_hidden = SongDict.get('songlist_hidden')
        self.byd_local_unlock = SongDict.get('byd_local_unlock')
        self.no_stream = SongDict.get('no_stream')
        self.date = SongDict.get('date')
        self.version = SongDict.get('version')
        self.difficulties = Difficulties()
        self.difficulties.LoadFromDifficultiesList(SongDict.get('difficulties'))
        self.additional_files = SongDict.get('additional_files')

class Pack:
    def __init__(self) -> None:
        pass

    def LoadFromPackDict(self, PackDict: dict):
        self.Raw = PackDict
        self.songs = []
        self.sub_packs = []
        self.id = PackDict['id']
        self.plus_character = PackDict['plus_character']
        self.custom_banner = PackDict.get('custom_banner')
        self.name_localized = PackDict['name_localized']
        self.description_localized = PackDict['description_localized']
        self.pack_parent = PackDict.get('pack_parent')

class Unlock:
    def __init__(self) -> None:
        pass

    def LoadFromUnlockDict(self, UnlockDict: dict):
        self.Raw = UnlockDict
        self.songId = UnlockDict['songId']
        self.ratingClass = UnlockDict['ratingClass']
        self.conditions = []
        conditions_list = UnlockDict['conditions']
        for i in conditions_list:
            condition = Condition()
            condition.LoadFromConditionDict(i)
            self.conditions.append(condition)

    def GetSongUnlockCondition(self) -> str:
        return '\n'.join([condition.GetCondition() for condition in self.conditions])

class Condition:
    Songs = None

    _init_flag = False

    def InitBySetSongs(Songs: ArcaeaSongs):
        Condition.Songs = Songs
        Condition._init_flag = True

    def __init__(self) -> None:
        if Condition._init_flag == False:
            raise Exception('__init__ before InitBySetSongs')

    def LoadFromConditionDict(self, ConditionDict: dict):
        if ConditionDict['type'] == 0: # Frag
            self.type = 0
            self.credit = ConditionDict['credit']
        elif ConditionDict['type'] == 1: # Grade On Early Chart
            self.type = 1
            self.song_id = ConditionDict['song_id']
            self.song_difficulty = ConditionDict['song_difficulty']
            self.grade = ConditionDict['grade']
        elif ConditionDict['type'] == 2: # Play On Early Chart
            self.type = 2
            self.song_id = ConditionDict['song_id']
            self.song_difficulty = ConditionDict['song_difficulty']
        elif ConditionDict['type'] == 3: # Multiple Grade On Early Chart
            self.type = 3
            self.song_id = ConditionDict['song_id']
            self.song_difficulty = ConditionDict['song_difficulty']
            self.grade = ConditionDict['grade']
            self.times = ConditionDict['times']
        elif ConditionDict['type'] == 4: # Multiple Selectable Conditions
            self.type = 4
            conditions = ConditionDict['conditions']
            self.conditions = []
            for i in conditions:
                condition = Condition()
                condition.LoadFromConditionDict(i)
                self.conditions.append(condition)
        elif ConditionDict['type'] == 5: # Reach a Rating
            self.type = 5
            self.rating = ConditionDict['rating']
        elif ConditionDict['type'] == 101: # Anomaly
            self.type = 101
            self.min = ConditionDict['min']
            self.max = ConditionDict['max']
        elif ConditionDict['type'] == 103: # Character
            self.type = 103
            self.id = ConditionDict['id']

    def GetCondition(self, tab_size: int = 2) -> str:
        tab_size *= ' '
        if self.type == 0: # Frag
            return str(self.credit) + ' 残片'
        elif self.type == 1: # Grade On Early Chart
            return '以 「' + grade_dict[self.grade] + '」 或以上成绩通关 ' + Condition.Songs.QuerySongNameBySongId(self.song_id) + ' [' + diff_dict.get(self.song_difficulty)[0] + '] '
        elif self.type == 2: # Play On Early Chart
            return '游玩 ' + Condition.Songs.QuerySongNameBySongId(self.song_id) + ' [' + diff_dict.get(self.song_difficulty)[0] + ']'
        elif self.type == 3: # Multiple Grade On Early Chart
            return '以 「' + grade_dict[self.grade] + '」 或以上成绩通关 ' + Condition.Songs.QuerySongNameBySongId(self.song_id) + ' [' + diff_dict.get(self.song_difficulty)[0] + '] ' + str(self.times) + '回'
        elif self.type == 4: # Multiple Selectable Conditions
            return ('\n' + tab_size + '或 ').join([condition.GetCondition() for condition in self.conditions])
        elif self.type == 5: # Reach a Rating
            return '个人游玩潜力值 ' + '%.2f'% (self.rating / 100) + ' 或以上'
        elif self.type == 101: # Anomaly
            return '通过异象解锁，失败时最少获得' + str(self.min) + '%，最多获得' + str(self.max) + '%'
        elif self.type == 103: # Character
            return '需使用 ' + Condition.Songs.CharactersDict.get(self.id) + ' 搭档解锁'

global grade_dict
global diff_dict
grade_dict = {0: 'No Limit', 1: 'C', 2: 'B', 3: 'A', 4: 'AA', 5: 'EX', 6: 'EX+'}
diff_dict = {0: ['PST', ['pst'], 'Past'], 
            1: ['PRS', ['prs', 'pre'], 'Present'],
            2: ['FTR', ['ftr'], 'Future'],
            3: ['BYD', ['byd', 'byn'], 'Beyond']}

class ArcaeaSongs:
    def __init__(self, ResourcePath) -> None:
        self.ResourcePath = EnsurePath(ResourcePath)
        # Parse Songlist Json
        self.SonglistRaw = json.load(open(self.ResourcePath + 'songs\\songlist', mode='r', encoding='utf-8'))
        self.Songlist = []
        for i in self.SonglistRaw['songs']:
            song = Song()
            song.LoadFromSongDict(i)
            self.Songlist.append(song)
        # Parse Characters
        Characters = open(self.ResourcePath + 'chars_formated.txt', mode='r', encoding='utf-8')
        self.CharactersDict = {}
        for i in Characters.readlines():
            i = i.replace('\n', '')
            SingleCharacter = i.split(' ')
            self.CharactersDict[int(SingleCharacter[0])] = SingleCharacter[1]
        # Parse Packlist
        self.PacklistRaw = json.load(open(self.ResourcePath + 'songs\\packlist', mode='r', encoding='utf-8'))
        packs = []
        for i in self.PacklistRaw['packs']:
            pack = Pack()
            pack.LoadFromPackDict(i)
            packs.append(pack)
        # Calculate Song and Pack Relationships
        for i in self.Songlist:
            for n in packs:
                if i.set == n.id:
                    n.songs.append(i)
                    break
        # Calculate Pack Relationships
        for pack in packs:
            pack.is_sub = False
        for i in packs:
            for n in packs:
                if i.id == n.pack_parent:
                    i.sub_packs.append(n)
                    n.is_sub = True
        self.Packlist = []
        for pack in packs:
            if not pack.is_sub:
                self.Packlist.append(i)
        # Parse Unlocks
        UnlocksRaw = json.load(open(self.ResourcePath + 'songs\\unlocks', mode='r', encoding='utf-8'))
        self.Unlocks = []
        Condition.InitBySetSongs(self)
        for i in UnlocksRaw['unlocks']:
            unlock = Unlock()
            unlock.LoadFromUnlockDict(i)
            self.Unlocks.append(unlock)
        self.VideoLinks = json.load(open(self.ResourcePath + 'vlinks.json', 'r', encoding='utf-8'))
        self.NickNames = json.load(open(self.ResourcePath + 'nicknames.json', 'r', encoding='utf-8'))

    def QuerySongNameBySongId(self, SongId: str):
        for song in self.Songlist:
            if song.id == SongId:
                return song.title_localized['en']

    def QuerySongBySongName(self, SongName: str):
        for song in self.Songlist:
            if song.title_localized['en'] == SongName or song.title_localized['ja'] == SongName:
                return song

    def QuerySongBySongId(self, SongId: str):
        for song in self.Songlist:
            if song.id == SongId:
                return song

    def QuerySongUnlockConditions(self, SongId: str, Difficulty: int):
        for unlock in self.Unlocks:
            if unlock.songId == SongId and unlock.ratingClass == Difficulty:
                return unlock.GetSongUnlockCondition()


# class Song:
#     def __init__(self, song_id, song_name, artist, charter_list, bpm, bpm_base, is_remote_dl, difficulties, diff_list) -> None:
#         self.SongId = song_id
#         self.SongName = song_name
#         self.Artist = artist
#         self.CharterList = charter_list
#         self.BPM = bpm
#         self.BPMBase = bpm_base
#         self.IsRemoteDl = is_remote_dl
#         self.Difficulties = difficulties
#         self.DiffList = diff_list

# class ArcaeaSongs:
#     def __init__(self, res_path) -> None:
#         self.res_path = res_path
#         # Get Songs
#         self.songlist_json = json.loads(open(res_path + 'songs\\songlist', 'r', encoding='utf-8').read())
#         self.songlist = []
#         for i in self.songlist_json['songs']:
#             diffs = []
#             charters = []
#             for n in i['difficulties']:
#                 charters.append(n['chartDesigner'])
#                 if n.get('ratingPlus', False):
#                     diffs.append(str(n['rating']) + '+')
#                     continue
#                 diffs.append(str(n['rating']))
#             self.songlist.append(Song(i['id'], i['title_localized'], i['artist'], charters, i['bpm'], i['bpm_base'], i.get('remote_dl', False), len(i['difficulties']) - 1, diffs)) #(song_id, song_name, artist, charter_list, bpm, bpm_base, is_remote_dl, difficulties, diff_list)
#         self.chardict = {}
#         chars = open(res_path + 'chars_formated.txt', 'r', encoding='utf-8')
#         for i in chars.readlines():
#             key = int(i[:i.find(' ')])
#             value = i[len(str(key)) + 1:]
#             self.chardict[key] = value
#         self.packlist_json = json.loads(open(res_path + 'songs\\packlist', 'r', encoding='utf-8').read())
#         self.packlist = []
#         for i in self.packlist_json['packs']:
#             self.packlist.append([i['id'], i['plus_character'], i['name_localized']['en'], i.get('description_localized').get('zh-Hans', i['description_localized']['en'])])
#         self.unlocks_json = json.loads(open(res_path + 'songs\\unlocks', 'r', encoding='utf-8').read())
#         self.unlocks = {}
#         for i in self.unlocks_json['unlocks']:
#             key = i['songId'] + str(i['ratingClass'])
#             value = []                            #[type0 :int,    type1 :list,            type2 :list,            type3 :list,                               type4 :list,                      type5 :int,             type101 :list,    type103 :int]
#             for c in i['conditions']:             # frag           grade on early chart    play on early charts    multiple grade on early charts multiple    multiple selectable conditions    reaching a potential    anomaly           character id
#                 if int(c['type']) == 0:
#                     value.append([0, c['credit']])
#                 elif int(c['type']) == 1:
#                     value.append([1, c['song_id'], c['song_difficulty'], c['grade']])
#                 elif int(c['type']) == 2:
#                     value.append([2, c['song_id'], c['song_difficulty']])
#                 elif int(c['type']) == 3:
#                     value.append([1, c['song_id'], c['song_difficulty'], c['grade'], c['times']])
#                 elif int(c['type']) == 4:
#                     selection = []
#                     for n in c['conditions']:
#                         if int(n['type']) == 0:
#                             selection.append([0, n['credit']])
#                         elif int(n['type']) == 1:
#                             selection.append([1, n['song_id'], n['song_difficulty'], n['grade']])
#                         elif int(n['type']) == 2:
#                             selection.append([2, n['song_id'], n['song_difficulty']])
#                         elif int(n['type']) == 3:
#                             selection.append([3, n['song_id'], n['song_difficulty'], n['grade'], n['times']])
#                         else:
#                             raise ResError('Unknown Unlocks type ' + str(c['type']), 'unlocks')
#                     value.append([4, selection])
#                 elif int(c['type']) == 5:
#                     value.append([5, c['rating']])
#                 elif int(c['type']) == 101:
#                     value.append([101, c['min'], c['max']])
#                 elif int(c['type']) == 103:
#                     value.append([103, c['id']])
#                 else:
#                     raise ResError('Unknown Unlocks type ' + str(c['type']), 'unlocks')
#             self.unlocks[key] = value
#         self.vlinks = json.load(open(self.res_path + 'vlinks.json', 'r', encoding='utf-8'))
#         self.nicknames = json.load(open(self.res_path + 'nicknames.json', 'r', encoding='utf-8'))

#     def GetSongById(self, SongId):
#         for i in self.songlist:
#             if i.SongId == SongId: return i
#         return 0

#     def GetSongByName(self, SongName):
#         for i in self.songlist:
#             if i.SongName['en'] == SongName or i.SongName['ja'] == SongName: return i
#         return 0

#     # def GetSongResources(self, SongId):
#     #     song = self.GetSongById(SongId)
#     #     folder_name = song.SongId
#     #     if song.IsRemoteDl:
#     #         folder_name = 'dl_' + folder_name
#     #     pic_list = [self.res_path + 'songs\\' + folder_name + '\\base.jpg']
#     #     for i in range(song.Difficulties + 1):
#     #         if os.path.exists(self.res_path + 'songs\\' + folder_name + '\\' + str(i) + '.jpg'): pic_list.append(self.res_path + 'songs\\' + folder_name + '\\' + str(i) + '.jpg')
#     #         else: pass
#     #     aud_path = self.res_path + 'songs\\' + folder_name + '\\base.ogg'
#     #     if song.IsRemoteDl:
#     #         aud_path = self.res_path + 'songs\\' + 'dl\\' + song.SongId
#     #     aff_path_list = [self.res_path + 'songs\\' + folder_name + '\\' + str(x) + '.aff' for x in range(0, int(song.Difficulties) + 1)]
#     #     if song.IsRemoteDl:
#     #         aff_path_list = [self.res_path + 'songs\\' + 'dl' + '\\' + song.SongId + '_' + str(x) for x in range(0, int(song.Difficulties) + 1)]
#     #     return pic_list, aud_path, aff_path_list

#     def GetSongResources(self, SongId):
#         song = self.GetSongById(SongId)
#         # Get Audio
#         pass


#     def SongsId(self) -> list:
#         return [i.SongId for i in self.songlist]

#     def Songs(self) -> list:
#         return [i.SongName['en'] for i in self.songlist]

#     def Count(self) -> list:
#         return len(self.songlist)

#     def FetchUnlocks(self, song_id: str, song_difficulty: int, tab_size: int = 2) -> list:
#         tab_size *= ' '
#         key = song_id + str(song_difficulty)
#         value = self.unlocks.get(key, False)
#         if not value: return ''
#         unlocks_info = []
#         for i in value:
#             if i[0] == 0:
#                 unlocks_info.append(str(i[1]) + ' 残片')
#             elif i[0] == 1:
#                 unlocks_info.append('以 「' + ArcaeaSongs.grade_dict[i[3]] + '」 或以上成绩通关 ' + self.GetSongById(i[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(i[2])[0] + '] ')
#             elif i[0] == 2:
#                 unlocks_info.append('游玩 ' + self.GetSongById(i[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(i[2])[0] + ']')
#             elif i[0] == 3:
#                 unlocks_info.append('以 「' + ArcaeaSongs.grade_dict[i[3]] + '」 或以上成绩通关 ' + self.GetSongById(i[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(i[2])[0] + '] ' + str(i[4]) + '回')
#             elif i[0] == 4:
#                 fo = tab_size + '或 '
#                 t = 0
#                 for n in i[1]:
#                     t += 1
#                     if t == 1:
#                         if n[0] == 0:
#                             unlocks_info.append(str(n[1]) + ' 残片')
#                         elif n[0] == 1:
#                             unlocks_info.append('以 「' + ArcaeaSongs.grade_dict[n[3]] + '」 或以上成绩通关 ' + self.GetSongById(n[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(n[2])[0] + '] ')
#                         elif n[0] == 2:
#                             unlocks_info.append('游玩 ' + self.GetSongById(n[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(n[2])[0] + '] ')
#                         elif n[0] == 3:
#                             unlocks_info.append('以 「' + ArcaeaSongs.grade_dict[n[3]] + '」 或以上成绩通关 ' + self.GetSongById(n[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(n[2])[0] + '] ' + str(n[4]) + '回')
#                     else:
#                         if n[0] == 0:
#                             unlocks_info.append(fo + str(n[1]) + ' 残片')
#                         elif n[0] == 1:
#                             unlocks_info.append(fo + '以 「' + ArcaeaSongs.grade_dict[n[3]] + '」 或以上成绩通关 ' + self.GetSongById(n[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(n[2])[0] + '] ')
#                         elif n[0] == 2:
#                             unlocks_info.append(fo + '游玩 ' + self.GetSongById(n[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(n[2])[0] + '] ')
#                         elif n[0] == 3:
#                             unlocks_info.append(fo + '以 「' + ArcaeaSongs.grade_dict[n[3]] + '」 或以上成绩通关 ' + self.GetSongById(n[1]).SongName['en'] + ' [' + ArcaeaSongs.diff_dict.get(n[2])[0] + '] ' + str(n[4]) + '回')
#             if i[0] == 5:
#                 potential = i[1] / 100
#                 unlocks_info.append('个人游玩潜力值 ' + '%.2f'% potential + ' 或以上')
#             if i[0] == 101:
#                 unlocks_info.append('通过异象解锁，失败时最少获得' + str(i[1]) + '%，最多获得' + str(i[2]) + '%')
#             if i[0] == 103:
#                 unlocks_info.append('解锁时需使用 ' + self.chardict.get(i[1]) + ' 搭档')
#         unlocks = ''
#         for i in unlocks_info:
#             unlocks += str(i) + '\n'
#         return unlocks

#     def GenerateVlinksJson(self, difficulty, file):
#         json_data = []
#         for i in self.songlist:
#             index = -1
#             for n in i.DiffList:
#                 song_vlinks = {}
#                 index += 1
#                 if int(n.replace('+', '')) >= difficulty:
#                     song_vlinks['song_id'] = i.SongId
#                     song_vlinks['song_name'] = i.SongName['en']
#                     song_vlinks['rating_class'] = index
#                     song_vlinks['difficulty'] = n
#                     song_vlinks['play_video'] = ''          #手元
#                     song_vlinks['rhyparse_video'] = ''      #节奏解析/节奏谱
#                     json_data.append(song_vlinks)
#         f = open(file, 'w', encoding='utf-8')
#         json.dump({'vids': json_data}, f, ensure_ascii=False, indent = 4)
#         f.close()

#     def GenerateNickNamesJson(self, file):
#         json_data = []
#         for i in self.songlist:
#             song_nicknames = {}
#             song_nicknames['song_id'] = i.SongId
#             song_nicknames['song_name'] = i.SongName['en']
#             song_nicknames['song_nicknames'] = ['']
#             json_data.append(song_nicknames)
#         f = open(file, 'w', encoding='utf-8')
#         json.dump({'nicknames': json_data}, f, ensure_ascii=False, indent = 4)
#         f.close()

#     def SongDetails(self, song_id):
#         song = self.GetSongById(song_id)
#         def Count(aff_path):
#             aff = Aff()
#             aff.Load(aff_path)
#             return aff.CountNotes()
#         def f(str1: str, str2: str):
#             if str1 + str2 != str1 and str1 + str2 != str1: return str1 + str2
#             return ''
#         return [song.SongName['en'], BotRes(self.SongRes(song_id)[0][0], 'image')] + [ArcaeaSongs.diff_dict[i][0] + ': ' + song.DiffList[i] + '，共 ' + str(Count(self.SongRes(song_id)[2][i])[0]) + ' Notes' for i in range(song.Difficulties + 1)] + [x for x in [f(song.SongName['en'] + ' 「' + ArcaeaSongs.diff_dict.get(i)[0] + '」 的解锁条件：\n', self.FetchUnlocks(song_id, i)) for i in range(song.Difficulties + 1)] if x != '']

#     def InitRemoteDownloadFiles(self):
#         Songs = s

#     grade_dict = {0: 'No Limit', 1: 'C', 2: 'B', 3: 'A', 4: 'AA', 5: 'EX', 6: 'EX+'}
#     diff_dict = {0: ['PST', ['pst'], 'Past'], 
#                 1: ['PRS', ['prs', 'pre'], 'Present'],
#                 2: ['FTR', ['ftr'], 'Future'],
#                 3: ['BYD', ['byd', 'byn'], 'Beyond']}


'''
Update functions
'''

def CheckUpdate(ResourcePath):
    ResourcePath = EnsurePath(ResourcePath)
    ArcaeaDownloadApi = r'https://webapi.lowiro.com/webapi/serve/static/bin/arcaea/apk'
    Request = requests.get(ArcaeaDownloadApi)
    if Request.status_code != 200: raise RequestError(ArcaeaDownloadApi)
    Content = json.loads(Request.content)
    try:
        Version = open(ResourcePath + 'version', 'r')
        Version = Version.read()
    except:
        return Content
    if Version == Content['value']['version']: return 0
    return Content, Version

def ExecuteUpdate(ResourcesPath) -> None:
    ResourcePath = EnsurePath(ResourcePath)
    Content, Version = CheckUpdate(ResourcesPath)
    if not Content: return None
    Download = MultiprocessDownload(Content['value']['url'], ResourcesPath, 'ArcaeaApk.apk', 16)
    Download.run()
    Resources = zipfile.ZipFIle(ResourcesPath + 'ArcaeaApk.apk')
    Resources.extractall(ResourcesPath + Content['value']['version'])
    os.mkdir(ResourcesPath + Version)
    for i in ['char', 'songs']:
        shutil.move(ResourcePath + i, ResourcePath + Version)
        shutil.move(ResourcePath + Content['value']['version'] +'\\assets\\' + i, ResourcePath)
    VersionUpdate = open(ResourcePath + 'version', 'w')
    VersionUpdate.write(Content['value']['version'])

def ExecuteResource(ResourcesPath) -> None:
    ResourcePath = EnsurePath(ResourcePath)
    Content = CheckUpdate(ResourcesPath)
    if not Content: return None
    Download = MultiprocessDownload(Content['value']['url'], ResourcesPath, 'ArcaeaApk.apk', 16)
    Download.run()
    Resources = zipfile.ZipFIle(ResourcesPath + 'ArcaeaApk.apk')
    Resources.extractall(ResourcesPath + Content['value']['version'])
    for i in ['char', 'songs']:
        shutil.move(ResourcePath + Content['value']['version'] +'\\assets\\' + i, ResourcePath)
    VersionUpdate = open(ResourcePath + 'version', 'w')
    VersionUpdate.write(Content['value']['version'])

