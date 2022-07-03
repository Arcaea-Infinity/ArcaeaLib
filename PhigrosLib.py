# Arcaea Lib Script
# Ver 0.0.1b by
# @Player01


from io import TextIOWrapper
import json
import gc
import time

'''
Phigros Chart Reader(Beta)
'''

# Note

class PhiEvent:
    def __init__(self) -> None:
        pass

class PhiNote:
    def __init__(self, Time: int, PositionX: float, HoldTime: float, Speed: float, FloorPosition: float) -> None:
        self.Time = Time
        self.PositionX = PositionX
        self.HoldTime = HoldTime
        self.Speed = Speed
        self.FloorPosition = FloorPosition

class Tap(PhiNote): pass # Type = 1
class Hold(PhiNote): pass # Type = 3
class Flick(PhiNote): pass # Type = 4
class Drag(PhiNote): pass # Type = 2



# Event

class SpeedEvent(PhiEvent):
    def __init__(self, StartTime: float, EndTime: float, FloorPosition: float, Value: float) -> None:
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.FloorPosition = FloorPosition
        self.Value = Value

class JudgeLineEvent(PhiEvent):
    def __init__(self, StartTime: float, EndTime: float, Start: float, End: float, Start2: float, End2: float) -> None:
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.Start = Start
        self.End = End
        self.Start2 = Start2
        self.End2 = End2

class JudgeLineDisappearEvent(JudgeLineEvent): pass
class JudgeLineMoveEvent(JudgeLineEvent): pass
class JudgeLineRotateEvent(JudgeLineEvent): pass

# ?
# class BPMGroup:
#     def __init__(self, BPM: float, Beat: float, Time: float) -> None:
#         self.BPM = BPM
#         self.Beat = Beat
#         self.Time = Time


# Util

def DictToNote(NoteDict: dict) -> PhiNote:
    TargetNote = {
        1: Tap,
        2: Drag,
        3: Hold,
        4: Flick
    }
    return TargetNote[NoteDict['type']](NoteDict['time'], NoteDict['positionX'], NoteDict['holdTime'], NoteDict['speed'], NoteDict['floorPosition'])

def DictToSpeedEvent(EventDict: dict) -> SpeedEvent:
    return SpeedEvent(EventDict['startTime'], EventDict['endTime'], EventDict['floorPosition'], EventDict['value'])

def DictToJudgeLineEvent(EventDict: dict, Type: str) -> SpeedEvent:
    TargetEvents = {
        'Disappear': JudgeLineDisappearEvent,
        'Move': JudgeLineMoveEvent,
        'Rotate': JudgeLineRotateEvent
    }
    return TargetEvents[Type](EventDict['startTime'], EventDict['endTime'], EventDict['start'], EventDict['end'], EventDict['start2'], EventDict['end2'])


class JudgeLine:
    def __init__(self, JudgeLineId: int, BPM: float) -> None:
        self.JudgeLineId = JudgeLineId
        self.SpeedEvents = []
        self.NotesAbove = []
        self.NotesBelow = []
        self.JudgeLineDisappearEvents = []
        self.JudgeLineMoveEvents = []
        self.JudgeLineRotateEvents = []
        self.BPM = BPM

    def AddEvent(self, Event: PhiEvent) -> None:
        if isinstance(Event, SpeedEvent):
            self.SpeedEvents.append(Event)
        elif isinstance(Event, JudgeLineDisappearEvent):
            self.JudgeLineDisappearEvents.append(Event)
        elif isinstance(Event, JudgeLineMoveEvent):
            self.JudgeLineMoveEvents.append(Event)
        elif isinstance(Event, JudgeLineRotateEvent):
            self.JudgeLineRotateEvents.append(Event)

    def AddNoteAbove(self, Note: PhiNote) -> None:
        self.NotesAbove.append(Note)

    def AddNoteBelow(self, Note: PhiNote) -> None:
        self.NotesBelow.append(Note)

    @property
    def NumOfNotes(self) -> int:
        return len(self.NotesAbove) + len(self.NotesBelow)

class PhiChart:
    def __init__(self) -> None:
        self.IsLoaded = False

    def Load(self, File: str or TextIOWrapper, Format: str):
        if isinstance(File, str):
            File = open(File, 'r')
        if Format == 'offical':
            self.JsonRaw = json.load(File)
            self.LoadOffical(self.JsonRaw)
        pass

    def ToOffical(self):
        pass

    def LoadOffical(self, JsonRaw: json) -> None:
        self.Format = 'offical'
        self.FormatVersion = JsonRaw['formatVersion']
        if self.FormatVersion != 3:
            raise Exception('Unsupported chart version')
        self.Offset = JsonRaw['offset']
        self.JudgeLineList = []
        for JudgeLineId in range(len(JsonRaw['judgeLineList'])):
            judgelinedict = JsonRaw['judgeLineList'][JudgeLineId]
            judgeline = JudgeLine(JudgeLineId, judgelinedict['bpm'])
            # Set Notes
            for note in judgelinedict['notesAbove']:
                judgeline.AddNoteAbove(DictToNote(note))
            for note in judgelinedict['notesBelow']:
                judgeline.AddNoteBelow(DictToNote(note))
            # Set Events
            for event in judgelinedict['speedEvents']:
                judgeline.AddEvent(DictToSpeedEvent(event))
            for event in judgelinedict['judgeLineDisappearEvents']:
                judgeline.AddEvent(DictToJudgeLineEvent(event, 'Disappear'))
            for event in judgelinedict['judgeLineMoveEvents']:
                judgeline.AddEvent(DictToJudgeLineEvent(event, 'Move'))
            for event in judgelinedict['judgeLineRotateEvents']:
                judgeline.AddEvent(DictToJudgeLineEvent(event, 'Rotate'))
            self.JudgeLineList.append(judgeline)
        gc.collect()
        print(self.NumOfNotes)

    @property
    def NumOfNotes(self):
        Notes = 0
        for i in self.JudgeLineList:
            Notes += i.NumOfNotes
        return Notes


t1 = time.time()
Chart = PhiChart()
Chart.Load('E:\\Lyrith\\Chart_AT.json', 'offical')
t2 = time.time()
print('%sms' % ((t2 - t1) * 1000))