# Arcaea Lib Script
# Ver 0.0.5a by
# @Player01
# @yyyr

# Video links collected by
# @Player01
# @MBRjun

# Open Source under MIT Lisence

'''
TODO List:

Arcaea Nickname system									0%
Song Name Comparing System								30%
Arc & Hold Note Count									90%
Arc Coordinate Calc										30%
Arcaea autoplay											1%
RemoteDL Challenge Calc									0%
Phigros chart reader									1%
Phigros chart and Arcaea chart converter				1%
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

# Standard Arcaea Song Picture pixel: 512*512
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
class botres:
    def __init__(self, path, filetype) -> None:
        self.path = path
        self.type = filetype

    def GetCode(self):
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
        self.threads[-1:][0][1] += self.length % self.thread_num

    def thread(self, num) -> int:
        self.lock[num] = _thread.allocate_lock()
        with self.lock[num]:
            header = {'Range': f'bytes=' + str(self.threads[num][0]) + '-' + str(self.threads[num][1])}
            print(header)
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

    def getDownloadInfo(self) -> list:
        info = []
        total = 0
        for i in range(self.thread_num):
            if None in self.proc: return None
            info.append(str(self.proc[i] * 100) + '%')
            total += self.proc[i]
        info.append(str(total / self.thread_num * 100) + '%') #[*threads_info, total_info]
        return info

    def run(self):
        for i in range(self.thread_num):
            _thread.start_new_thread(self.thread, (i,))
        time.sleep(10)
        locked = 1
        while locked:
            print(self.getDownloadInfo())
            locked = 0
            for n in range(self.thread_num):
                while None in self.lock:
                    locked = 1
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
        print('File download as', self.path + self.filename)

def formatScore(score: int) -> int:
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
    def __init__(self, Time: int, BPM: float, Beats: int, TiminggroupId: int) -> None:
        self.StartTime = Time
        self.BPM = BPM
        self.Beats = Beats
        self.TiminggroupId = TiminggroupId
        self.Count = 0

class Arc: pass

class Arctap:
    def __init__(self, Time: int):
        self.StartTime = Time
        self.count = 1
        self.Enabled = True

    def Instantiate(self, arc: Arc):
        self.Arc = arc

    def Destroy(self):
        self.Enabled = False

    def Clone(self):
        return Arctap(self.StartTime)

class Arc:
    def __init__(self, StartTime: int, EndTime: int, XStart: float, XEnd: float, EasingType: str, YStart: float, YEnd: float, Color: int, FX: str, IsSkyline: bool, ArcTaps: list, BPM: int, TimingPointDensityFactor: float, NoInput: bool, AngleX: int, AngleY: int, TiminggroupId: int) -> None:
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.XStart = XStart
        self.XEnd = XEnd
        self.EasingType = EasingType
        self.YStart = YStart
        self.YEnd = YEnd
        self.Color = Color
        self.FX = FX
        self.IsSkyLine = IsSkyline
        self.Arctaps = ArcTaps
        self.BPM = BPM
        self.TimingPointDensityFactor = TimingPointDensityFactor
        self.NoInput = NoInput
        self.AngleX = AngleX
        self.AngleY = AngleY
        self.TiminggroupId = TiminggroupId
        self.Count = 0
        if self.IsSkyLine:
            self.Count = len(self.Arctaps)
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
        BPM = abs(self.BPM)
        if BPM >= 255.0: x = 1.0
        else: x = 2.0
        PartitionIndex = 60000.0 / BPM / x / self.TimingPointDensityFactor
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
        if not self.NoInput:
            if len(self.Arctaps): #ArcTaps, Skyline
                self.Count = len(self.Arctaps)
            elif not self.IsSkyLine: #Arc
                self.Count = len(self.JudgeTimings)
        else: self.Count = 0

    def GetXAtTiming(self, t: int):
        t2 = (t - self.StartTime) / (self.EndTime - self.StartTime)
        return ArcXToWorld(X(self.XStart, self.XEnd, t2, self.EasingType))

    def GetYAtTiming(self, t: int):
        t2 = (t - self.StartTime) / (self.EndTime - self.StartTime)
        return ArcXToWorld(Y(self.YStart, self.YEnd, t2, self.EasingType)) 

    def AddArcTap(self, arctap: Arctap):
        if arctap.StartTime > self.EndTime or arctap.StartTime < self.StartTime:
            raise AffError("Arctap Time Invalid")
        if not self.IsSkyLine:
            raise AffError("Try to add arctap into an non-skyline arc")
        arctap.Instantiate(self)
        self.Arctaps.append(arctap)

class Tap:
    def __init__(self, Time: int, Lane: int, NoInput: bool, TiminggroupId: int) -> None:
        self.StartTime = Time
        self.Lane = Lane
        self.NoInput = NoInput
        self.TiminggroupId = TiminggroupId
        self.Count = 0
        if not self.NoInput: self.Count = 1
        else: pass

class Hold:
    def __init__(self, StartTime: int, EndTime: int, Lane: int, BPM: int, TimingPointDensityFactor: float, NoInput: bool, FadingHolds: bool, TiminggroupId: int) -> None:
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.Lane = Lane
        self.BPM = BPM
        self.TimingPointDensityFactor = TimingPointDensityFactor
        self.NoInput = NoInput
        self.FadingHolds = FadingHolds
        self.TiminggroupId = TiminggroupId
        self.Count = 0
        if not self.NoInput: self.CalcJudgeTimings(); self.Count = len(self.JudgeTimings)
        else: pass
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
        BPM = abs(self.BPM)
        if BPM >= 255.0: x = 1.0
        else: x = 2.0
        PartitionIndex = 60000.0 / BPM / x / self.TimingPointDensityFactor
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

    def Clone(self):
        return Hold(self.StartTime, self.EndTime, self.Lane, self.TiminggroupId)

class Camera:
    def __init__(self, StartTime: int, Transverse: float, BottomZoom: float, LineZoom: float, SteadyAngle: float, TopZoom: float, RotateAngle: float, EasingType: str, LastingTime: int, TiminggroupId: int) -> None:
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
        self.Count = 0

class SceneControl:
    def __init__(self, args, TiminggroupId: int) -> None:
        self.Count = 0
        self.TiminggroupId = TiminggroupId
        if len(args) == 2: #scenecontrol(t,type);
            self.SceneControlType = 'HideTrack'
            self.StartTime = args[0]
            self.Type = args[1]
        elif len(args) == 4: #scenecontrol(t,type,x,y); scenecontrol(t,hidegroup,x,type);
            if args[1] in ['redline', 'arcahvdistort', 'arcahvdabris']:
                self.SceneControlType = 'Arcahv'
                self.StartTime = args[0]
                self.Type = args[1]
                self.LastingTime = args[2]
                self.Param = args[3]
            else:
                self.SceneControlType = 'HideNote'
                self.StartTime = args[0]
                self.HideGroup = args[1]
                self.Param = args[2]
                self.Type = args[3]

class TiminggroupProperties:
    def __init__(self, Type, TiminggroupId: int):
        self.TiminggroupId = TiminggroupId
        self.Type = Type
        self.Count = 0

class Flick:
    def __init__(self, Time, X, Y, FX, FY, NoInput, TiminggroupId: int):
        self.Time = Time
        self.X = X
        self.Y = Y
        self.FX = FX
        self.FY = FY
        self.NoInput = NoInput
        self.Count = 0 if NoInput else 1
        self.TiminggroupId = TiminggroupId

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
            if i[0] == 'TimingPointDensityFactor':
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
        self.CurrentBPM = None
        for i in aff[1]:
            line += 1
            if i.startswith('};'):
                NoInput = False
                FadingHolds = False
                TiminggroupId = 0
                AngleX = 0
                AngleY = 0
                self.TiminggroupBPM = None
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
            else:
                self.Events.append(self.proceed(i, NoInput, FadingHolds, AngleX, AngleY, len(aff[0]) + 1 + line, TiminggroupId))
        del self.CurrentBPM
        try:
            self.Events.remove(None)
        except:
            pass
        for i in self.Events:
            if isinstance(i, TiminggroupProperties):
                Id = i.TiminggroupId
                for n in self.Events:
                    if n.TiminggroupId == Id:
                        if not isinstance(i, Timing):
                            i.StartTime = n.StartTime
        self.CalcArcRelationship()
        self.IsLoaded = True

    def proceed(self, i, NoInput: bool, FadingHolds: bool, AngleX: int, AngleY: int, line: int, TiminggroupId: int):
        i = i.strip().strip(';')
        if i.strip() == '':
            return None
        elif i.startswith('timing') and not i.startswith('timinggroup'):
            args = i.strip('timing')
            args = formatAffCmd(args)
            if TiminggroupId != 0:
                self.TiminggroupBPM = args[1]
            else:
                self.CurrentBPM = args[1]
            return Timing(args[0], args[1], args[2], TiminggroupId)
        BPM = self.TiminggroupBPM if TiminggroupId != 0 else self.CurrentBPM
        if i.startswith('arc'):
            arcCmd = re.match(r'arc\(.*?\)', i)
            if arcCmd == None: raise AffError('Arc regex not matched', line = line)
            arcCmd = arcCmd.group()
            arcCmd = arcCmd.strip('arc')
            arcArgs = formatAffCmd(arcCmd)
            arctapArgs = []
            arctaps = []
            if i.find('arctap') >= 0:
                arctapCmd = re.search(r'(arctap\([0-9]+\),)*arctap\([0-9]+\)', i)
                if arctapCmd == None: AffError('Arctap regex not matched', line = line)
                arctapCmd = arctapCmd.group()
                arctapCmd = arctapCmd.strip('[').strip(']')
                arctapCmd = arctapCmd.split(',')
                for c in arctapCmd:
                    arctapArgs.append(int(c.strip('arctap(').strip(')')))
                for n in arctapArgs:
                    arctaps.append(Arctap(n))
            return Arc(arcArgs[0], arcArgs[1], arcArgs[2], arcArgs[3], arcArgs[4], arcArgs[5], arcArgs[6], arcArgs[7], arcArgs[8], arcArgs[9], arctaps, BPM, self.TimingPointDensityFactor, NoInput, AngleX, AngleY, TiminggroupId)
        elif i.startswith('hold'):
            args = formatAffCmd(i.strip('hold').strip(';'))
            return Hold(args[0], args[1], args[2], BPM, self.TimingPointDensityFactor, NoInput, FadingHolds, TiminggroupId)
        elif i.startswith('scenecontrol'):
            args = formatAffCmd(i.strip('scenecontrol').strip(';'))
            return SceneControl(args, TiminggroupId)
        elif i.startswith('flick'):
            args = formatAffCmd(i.strip('flick').strip(';'))
            return Flick(args[0], args[1], args[2], args[3], args[4], NoInput, TiminggroupId)
        elif i.startswith('camera'):
            args = formatAffCmd(i.strip('camera').strip(';'))
            return Camera(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[9], TiminggroupId)
        elif i[0] == '(' and i[-1:] == ')': #Tap
            args = formatAffCmd(i.strip(';'))
            return Tap(args[0], args[1], NoInput, TiminggroupId)
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

'''
ArcaeaSongs: Parse packlist, songlist, unlocks from Arcaea APK file
'''

class Song:
    def __init__(self, song_id, song_name, artist, charter_list, bpm, bpm_base, is_remote_dl, difficulties, diff_list) -> None:
        self.SongId = song_id
        self.SongName = song_name
        self.Artist = artist
        self.CharterList = charter_list
        self.BPM = bpm
        self.BPM_Base = bpm_base
        self.IsRemoteDl = is_remote_dl
        self.Difficulties = difficulties
        self.DiffList = diff_list

class ArcaeaSongs:
    def __init__(self, res_path, log: Log = Log(True, 'log.txt')) -> None:
        # if res_path[-1:] != '\\' or not os.path.exists(res_path):
        #     log.log('warning', 'Path not valid', 'ArcaeaSongs.__init__()')
        #     res_path += '\\'
        #     if not os.path.exists(res_path):
        #         raise ValueError('Path not found')
        self.res_path = res_path
        log.log('info', 'parsing songlist', 'ArcaeaSongs.__init__()')
        time1 = time.time()
        self.slist_json = json.loads(open(res_path + 'songs\\songlist', 'r', encoding='utf-8').read())
        self.slist = []
        for i in self.slist_json['songs']:
            diffs = []
            charters = []
            for n in i['difficulties']:
                charters.append(n['chartDesigner'])
                if n.get('ratingPlus', False):
                    diffs.append(str(n['rating']) + '+')
                    continue
                diffs.append(str(n['rating']))
            sinfo = Song(i['id'], i['title_localized'], i['artist'], charters, i['bpm'], i['bpm_base'], i.get('remote_dl', False), len(i['difficulties']) - 1, diffs)
            self.slist.append(sinfo) #(song_id, song_name, artist, charter_list, bpm, bpm_base, is_remote_dl, difficulties, diff_list)
        time2 = time.time()
        log.log('info', 'songlist parsed, time spent: %sms' % ((time2 - time1) * 1000), 'ArcaeaSongs.__init__()')
        log.log('info', 'parsing characters list', 'ArcaeaSongs.__init__()')
        time1 = time.time()
        self.chardict = {}
        chars = open(res_path + 'chars_formated.txt', 'r', encoding='utf-8')
        for i in chars.readlines():
            key = int(i[:i.find(' ')])
            value = i[len(str(key)) + 1:]
            self.chardict[key] = value
        time2 = time.time()
        log.log('info', 'characters parsed, time spent: %sms' % ((time2 - time1) * 1000), 'ArcaeaSongs.__init__()')
        log.log('info', 'parsing packlist', 'ArcaeaSongs.__init__()')
        time1 = time.time()
        self.plist_json = json.loads(open(res_path + 'songs\\packlist', 'r', encoding='utf-8').read())
        self.plist = []
        for i in self.plist_json['packs']:
            self.plist.append([i['id'], i['plus_character'], i['name_localized']['en'], i.get('description_localized').get('zh-Hans', i['description_localized']['en'])])
        time2 = time.time()
        log.log('info', 'packlist parsed, time spent: %sms' % ((time2 - time1) * 1000), 'ArcaeaSongs.__init__()')
        log.log('info', 'parsing unlocks', 'ArcaeaSongs.__init__()')
        time1 = time.time()
        self.ulks_json = json.loads(open(res_path + 'songs\\unlocks', 'r', encoding='utf-8').read())
        self.ulks = {}
        for i in self.ulks_json['unlocks']:
            key = i['songId'] + str(i['ratingClass'])
            value = []                            #[type0 :int,    type1 :list,            type2 :list,            type3 :list,                               type4 :list,                      type5 :int,             type101 :list,    type103 :int]
            for c in i['conditions']:             # frag           grade on early chart    play on early charts    multiple grade on early charts multiple    multiple selectable conditions    reaching a potential    anomaly           character id
                if int(c['type']) == 0:
                    value.append([0, c['credit']])
                elif int(c['type']) == 1:
                    value.append([1, c['song_id'], c['song_difficulty'], c['grade']])
                elif int(c['type']) == 2:
                    value.append([2, c['song_id'], c['song_difficulty']])
                elif int(c['type']) == 3:
                    value.append([1, c['song_id'], c['song_difficulty'], c['grade'], c['times']])
                elif int(c['type']) == 4:
                    selection = []
                    for n in c['conditions']:
                        if int(n['type']) == 0:
                            selection.append([0, n['credit']])
                        elif int(n['type']) == 1:
                            selection.append([1, n['song_id'], n['song_difficulty'], n['grade']])
                        elif int(n['type']) == 2:
                            selection.append([2, n['song_id'], n['song_difficulty']])
                        elif int(n['type']) == 3:
                            selection.append([3, n['song_id'], n['song_difficulty'], n['grade'], n['times']])
                        else:
                            raise ResError('Unknown Unlocks type ' + str(c['type']), 'unlocks')
                    value.append([4, selection])
                elif int(c['type']) == 5:
                    value.append([5, c['rating']])
                elif int(c['type']) == 101:
                    value.append([101, c['min'], c['max']])
                elif int(c['type']) == 103:
                    value.append([103, c['id']])
                else:
                    raise ResError('Unknown Unlocks type ' + str(c['type']), 'unlocks')
            self.ulks[key] = value
        time2 = time.time()
        log.log('info', 'unlocks parsed, time spent: %sms' % ((time2 - time1) * 1000), 'ArcaeaSongs.__init__()')
        log.log('info', 'loding vlinks and nicknames', 'ArcaeaSongs.__init__()')
        self.vlinks = json.load(open(self.res_path + 'vlinks.json', 'r', encoding='utf-8'))
        self.nicknames = json.load(open(self.res_path + 'nicknames.json', 'r', encoding='utf-8'))

    def fetchSinfoById(self, song_id):
        for i in self.slist:
            if i.SongId == song_id: return i
        return 0

    def fetchSinfoByName(self, song_name):
        for i in self.slist:
            if i.SongName['en'] == song_name or i.SongName['ja'] == song_name: return i
        return 0

    def songRes(self, song_id):
        song = self.fetchSinfoById(song_id)
        folder_name = song.SongId
        if song.IsRemoteDl:
            folder_name = 'dl_' + folder_name
        pic_list = [self.res_path + 'songs\\' + folder_name + '\\base.jpg']
        for i in range(song.Difficulties + 1):
            if os.path.exists(self.res_path + 'songs\\' + folder_name + '\\' + str(i) + '.jpg'): pic_list.append(self.res_path + 'songs\\' + folder_name + '\\' + str(i) + '.jpg')
            else: pass
        aud_path = self.res_path + 'songs\\' + folder_name + '\\base.ogg'
        if song.IsRemoteDl:
            aud_path = self.res_path + 'songs\\' + 'dl\\' + song.SongId
        aff_path_list = [self.res_path + 'songs\\' + folder_name + '\\' + str(x) + '.aff' for x in range(0, int(song.Difficulties) + 1)]
        if song.IsRemoteDl:
            aff_path_list = [self.res_path + 'songs\\' + 'dl' + '\\' + song.SongId + '_' + str(x) for x in range(0, int(song.Difficulties) + 1)]
        return pic_list, aud_path, aff_path_list

    def songs_id(self) -> list:
        return [i.SongId for i in self.slist]

    def songs(self) -> list:
        return [i.SongName['en'] for i in self.slist]

    def count(self) -> list:
        return len(self.slist)

    def fetchUnlocks(self, song_id: str, song_difficulty: int, tab_size: int = 2) -> list:
        tab_size *= ' '
        key = song_id + str(song_difficulty)
        value = self.ulks.get(key, False)
        if not value: return ''
        ulksInfo = []
        for i in value:
            if i[0] == 0:
                ulksInfo.append(str(i[1]) + ' 残片')
            elif i[0] == 1:
                ulksInfo.append('以 「' + self.grade_dict[i[3]] + '」 或以上成绩通关 ' + self.fetchSinfoById(i[1]).SongName['en'] + ' [' + self.diff_dict.get(i[2])[0] + '] ')
            elif i[0] == 2:
                ulksInfo.append('游玩 ' + self.fetchSinfoById(i[1]).SongName['en'] + ' [' + self.diff_dict.get(i[2])[0] + ']')
            elif i[0] == 3:
                ulksInfo.append('以 「' + self.grade_dict[i[3]] + '」 或以上成绩通关 ' + self.fetchSinfoById(i[1]).SongName['en'] + ' [' + self.diff_dict.get(i[2])[0] + '] ' + str(i[4]) + '回')
            elif i[0] == 4:
                fo = tab_size + '或 '
                t = 0
                for n in i[1]:
                    t += 1
                    if t == 1:
                        if n[0] == 0:
                            ulksInfo.append(str(n[1]) + ' 残片')
                        elif n[0] == 1:
                            ulksInfo.append('以 「' + self.grade_dict[n[3]] + '」 或以上成绩通关 ' + self.fetchSinfoById(n[1]).SongName['en'] + ' [' + self.diff_dict.get(n[2])[0] + '] ')
                        elif n[0] == 2:
                            ulksInfo.append('游玩 ' + self.fetchSinfoById(n[1]).SongName['en'] + ' [' + self.diff_dict.get(n[2])[0] + '] ')
                        elif n[0] == 3:
                            ulksInfo.append('以 「' + self.grade_dict[n[3]] + '」 或以上成绩通关 ' + self.fetchSinfoById(n[1]).SongName['en'] + ' [' + self.diff_dict.get(n[2])[0] + '] ' + str(n[4]) + '回')
                    else:
                        if n[0] == 0:
                            ulksInfo.append(fo + str(n[1]) + ' 残片')
                        elif n[0] == 1:
                            ulksInfo.append(fo + '以 「' + self.grade_dict[n[3]] + '」 或以上成绩通关 ' + self.fetchSinfoById(n[1]).SongName['en'] + ' [' + self.diff_dict.get(n[2])[0] + '] ')
                        elif n[0] == 2:
                            ulksInfo.append(fo + '游玩 ' + self.fetchSinfoById(n[1]).SongName['en'] + ' [' + self.diff_dict.get(n[2])[0] + '] ')
                        elif n[0] == 3:
                            ulksInfo.append(fo + '以 「' + self.grade_dict[n[3]] + '」 或以上成绩通关 ' + self.fetchSinfoById(n[1]).SongName['en'] + ' [' + self.diff_dict.get(n[2])[0] + '] ' + str(n[4]) + '回')
            if i[0] == 5:
                potential = i[1] / 100
                ulksInfo.append('个人游玩潜力值 ' + '%.2f'% potential + ' 或以上')
            if i[0] == 101:
                ulksInfo.append('通过异象解锁，失败时最少获得' + str(i[1]) + '%，最多获得' + str(i[2]) + '%')
            if i[0] == 103:
                ulksInfo.append('解锁时需使用 ' + self.chardict.get(i[1]) + ' 搭档')
        ulks = ''
        for i in ulksInfo:
            ulks += str(i) + '\n'
        return ulks

    def genVlinksJson(self, difficulty, file):
        json_data = []
        for i in self.slist:
            index = -1
            for n in i.DiffList:
                song_vlinks = {}
                index += 1
                if int(n.replace('+', '')) >= difficulty:
                    song_vlinks['song_id'] = i.SongId
                    song_vlinks['song_name'] = i.SongName['en']
                    song_vlinks['rating_class'] = index
                    song_vlinks['difficulty'] = n
                    song_vlinks['play_video'] = ''          #手元
                    song_vlinks['rhyparse_video'] = ''      #节奏解析/节奏谱
                    json_data.append(song_vlinks)
        f = open(file, 'w', encoding='utf-8')
        json.dump({'vids': json_data}, f, ensure_ascii=False, indent = 4)
        f.close()

    def genNickNamesJson(self, file):
        json_data = []
        for i in self.slist:
            song_nicknames = {}
            song_nicknames['song_id'] = i.SongId
            song_nicknames['song_name'] = i.SongName['en']
            song_nicknames['song_nicknames'] = ['']
            json_data.append(song_nicknames)
        f = open(file, 'w', encoding='utf-8')
        json.dump({'nicknames': json_data}, f, ensure_ascii=False, indent = 4)
        f.close()

    def songDetails(self, song_id):
        song = self.fetchSinfoById(song_id)
        def Count(aff_path):
            aff = Aff()
            aff.Load(aff_path)
            return aff.CountNotes()
        def f(str1: str, str2: str):
            if str1 + str2 != str1 and str1 + str2 != str1: return str1 + str2
            return ''
        return [song.SongName['en'], botres(self.songRes(song_id)[0][0], 'image')] + [self.diff_dict[i][0] + ': ' + song.DiffList[i] + '，共 ' + str(Count(self.songRes(song_id)[2][i])[0]) + ' Notes' for i in range(song.Difficulties + 1)] + [x for x in [f(song.SongName['en'] + ' 「' + self.diff_dict.get(i)[0] + '」 的解锁条件：\n', self.fetchUnlocks(song_id, i)) for i in range(song.Difficulties + 1)] if x != '']

    grade_dict = {0: 'No Limit', 1: 'C', 2: 'B', 3: 'A', 4: 'AA', 5: 'EX', 6: 'EX+'}
    diff_dict = {0: ['PST', ['pst'], 'Past'], 
                1: ['PRS', ['prs', 'pre'], 'Present'],
                2: ['FTR', ['ftr'], 'Future'],
                3: ['BYD', ['byd', 'byn'], 'Beyond']}


'''
Phigros Chart Reader(Beta)
'''
class BPMGroup:
    def __init__(self, BPM: float, Beat: float, Time: float) -> None:
        self.BPM = BPM
        self.Beat = Beat
        self.Time = Time

class SpeedEvent:
    def __init__(self, StartTime: float, EndTime: float, Value: float) -> None:
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.Value = Value

class PhiChart:
    def __init__(self) -> None:
        self.IsLoaded = False

    def Load(self, file: str or TextIOWrapper, format: str):
        if isinstance(file, TextIOWrapper):
            file = file.read()
        if format == 'offical':
            self.format = format
            self.raw = file
            self.jsonraw = json.dumps(file)
        pass

    def ToOffical(self):
        pass

'''
Update functions
'''
def autoUpd(res_path, log: Log = Log(True, 'log.txt')) -> int:
    arcWebApi = r'https://webapi.lowiro.com/webapi/serve/static/bin/arcaea/apk'
    req = requests.get(arcWebApi)
    if req.status_code != 200: return 1
    content = json.loads(req.content)
    log.log('info', content, 'autoUpd()')
    version = open(res_path + 'version', 'r')
    version = version.read()
    if version == content['value']['version']: return 0
    apkUrl = content['value']['url']
    down = MultiprocessDownload(apkUrl, res_path, 'arcApk.zip', 16)
    down.run()
    res = zipfile.ZipFile(res_path + 'arcApk.zip')
    res.extractall(res_path + content['value']['version'])
    os.mkdir(res_path + version)
    for i in ['char', 'songs']:
        shutil.move(res_path + i, res_path + version)
        shutil.move(res_path + content['value']['version'] +'\\assets\\' + i, res_path)
    ver_update = open(res_path + 'version', 'w')
    ver_update.write(content['value']['version'])
    log.log('info', 'Updated to ' + content['value']['version'] + ' old files in ' + version + ' folder', 'autoUpd()')
    return 0

def autoDlRes(res_path, log: Log = Log(True, 'log.txt')) -> int:
    arcWebApi = r'https://webapi.lowiro.com/webapi/serve/static/bin/arcaea/apk'
    req = requests.get(arcWebApi)
    if req.status_code != 200: return 1
    content = json.loads(req.content)
    log.log('info', content, 'autoDlRes()')
    apkUrl = content['value']['url']
    down = MultiprocessDownload(apkUrl, res_path, 'arcApk.zip', 16)
    down.run()
    res = zipfile.ZipFile(res_path + 'arcApk.zip')
    res.extractall(res_path + content['value']['version'])
    for i in ['char', 'songs']:
        shutil.move(res_path + content['value']['version'] + '\\assets\\' + i, res_path)
    ver_file = open(res_path + 'version', 'w')
    ver_file.write(content['value']['version'])
    log.log('info', 'Download to ' + content['value']['version'], 'autoDlRes()')
    return 0

def resource(res_path) -> int:
    if os.path.exists(res_path + 'version'):
        autoUpd(res_path)
    else:
        autoDlRes(res_path)
    return 0


'''
Bot functions
'''
class GuessPic:
    def __init__(self, song: Song, res: ArcaeaSongs, guess_type: str): #guess_type: easy, hard, insane
        self.song = song
        self.pic_path = res.songRes(song.SongId)[0][0]
        self.guess_type = guess_type
        self.pic = Image.open(self.pic_path)
        self.res = res

    def GeneratePic(self, save_path: str):
        if self.guess_type == 'easy': length = self.pic.size[0] // 3
        if self.guess_type == 'hard': length = self.pic.size[0] // 4
        if self.guess_type == 'insane': length = self.pic.size[0] // 5; self.pic.convert('L')
        xstart = random.randint(0, self.pic.size[0] - length)
        xend = xstart + length
        ystart = random.randint(0, self.pic.size[1] - length)
        yend = ystart + length
        self.pic.crop((xstart, ystart, xend, yend)).save(save_path)

    def Guess(self, msg, qq):
        if compare(msg.split().lower(), self.song.SongId) or compare(msg.split().lower(), self.song.SongName['en']) or compare(msg.split().lower(), self.song.SongName['ja']): win = True
        self.winner = qq
        return True if win else False

class BotMessageBuilder:
    def __init__(self):
        self.Message = []

    def Add(self, *args):
        pass

    def ToDataSegment(self):
        pass

'''
Autoplay script generator
'''

class SlotEvent:
    def __init__(self, SlotId, Time, Type, X, Y):
        self.SlotId = SlotId
        self.Time = Time
        self.Type = Type
        self.X = X
        self.Y = Y

class Slots:
    def __init__(self):
        self.Events = []

    def AddEvent(self, SlotId, Time, Type, X, Y):
        self.Events.append(SlotEvent(SlotId, Time, Type, X, Y))

    def SortEventByTime(self):
        self.Events.sort(key = lambda slot:slot.Time)

    def ToSlotsCode(self):
        pass

def ArcAutoplayGenerator(aff_path, Width = 1920, Height = 1080):
    CanvasW = [Width * 0.33, Width * 0.71]
    CanvasH = [Height * 0.81, Height * 0.37]
    JudgeArea = [CanvasW[1] - CanvasW[0], CanvasH[0] - CanvasH[1]]
    aff = Aff()
    aff.Load(aff_path)

t1 = time.time()
a = ArcaeaSongs('.\\')
j = json.loads(open('arcsong.json', 'r', encoding='utf-8').read())
def query_in_arcsong(j, id):
    for i in j['content']['songs']:
        if i['id'] == id: return i
text = ''
for i in a.slist:
    try:
        for n in a.songRes(i.SongId)[2]:
            z = Aff()
            z.Load(n)
            try:
                diff = int(n[-1:])
            except:
                diff = int(n[1:].split('.')[0][-1:])
            if z.CountNotes()[0] != query_in_arcsong(j, i.SongId)['difficulties'][diff]['totalNotes']:
                text += i.SongName['en'] + '「' + a.diff_dict[diff][0] + '」' + ': {0} -> {1}'.format(z.CountNotes()[0], query_in_arcsong(j, i.SongId)['difficulties'][diff]['totalNotes']) + '\n'
    except:
        pass
print(text)
t2 = time.time()
print('%sms' % ((t2 - t1) * 1000))
f = open('errors.txt', 'w', encoding='utf-8')
f.write(text)
f.close()