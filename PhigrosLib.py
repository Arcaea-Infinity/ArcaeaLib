# Arcaea Lib Script
# Ver 0.0.1b by
# @Player01


from io import TextIOWrapper
import json
import gc
import time
import _thread # 别骂我 这个真的很简单
# threading太难我不会（x

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

    def AddNotesAbove(self, Note: PhiNote) -> None:
        self.NotesAbove.append(Note)

    def AddNotesBelow(self, Note: PhiNote) -> None:
        self.NotesBelow.append(Note)

    def SetNotesByJudgeLineDict(self, JudgeLineDict: dict) -> None:
        for note in JudgeLineDict['notesAbove']:
            self.NotesAbove.append(DictToNote(note))
        for note in JudgeLineDict['notesBelow']:
            self.NotesBelow.append(DictToNote(note))

    def SetEventsByJudgeLineDict(self, JudgeLineDict: dict) -> None:
        for event in JudgeLineDict['speedEvents']:
            self.SpeedEvents.append(DictToSpeedEvent(event))
        for event in JudgeLineDict['judgeLineDisappearEvents']:
            self.JudgeLineDisappearEvents.append(DictToJudgeLineEvent(event, 'Disappear'))
        for event in JudgeLineDict['judgeLineMoveEvents']:
            self.JudgeLineMoveEvents.append(DictToJudgeLineEvent(event, 'Move'))
        for event in JudgeLineDict['judgeLineRotateEvents']:
            self.JudgeLineRotateEvents.append(DictToJudgeLineEvent(event, 'Rotate'))

    @property
    def NumOfNotes(self) -> int:
        return len(self.NotesAbove) + len(self.NotesBelow)

class PhiChart:
    def __init__(self) -> None:
        self.IsLoaded = False

    def Load(self, File: str or TextIOWrapper, Format: str):
        if isinstance(File, str):
            File = open(File, 'r')
        if Format == 'official':
            self.JsonRaw = json.load(File)
            self.LoadOfficial(self.JsonRaw)
        pass

    def ToOfficial(self):
        pass

    def LoadOfficial(self, JsonRaw: json) -> None:
        self.Format = 'official'
        self.FormatVersion = JsonRaw['formatVersion']
        if self.FormatVersion != 3:
            raise Exception('Unsupported chart version')
        self.Offset = JsonRaw['offset']
        self.JudgeLineList = []
        for JudgeLineId in range(len(JsonRaw['judgeLineList'])):
            judgelinedict = JsonRaw['judgeLineList'][JudgeLineId]
            judgeline = JudgeLine(JudgeLineId, judgelinedict['bpm'])
            # Set Notes
            # for note in judgelinedict['notesAbove']:
            #     judgeline.NotesAbove.append(DictToNote(note))
            # for note in judgelinedict['notesBelow']:
            #     judgeline.NotesBelow.append(DictToNote(note))
            judgeline.SetNotesByJudgeLineDict(judgelinedict)
            # Set Events
            # for event in judgelinedict['speedEvents']:
            #     judgeline.SpeedEvents.append(DictToSpeedEvent(event))
            # for event in judgelinedict['judgeLineDisappearEvents']:
            #     judgeline.JudgeLineDisappearEvents.append(DictToJudgeLineEvent(event, 'Disappear'))
            # for event in judgelinedict['judgeLineMoveEvents']:
            #     judgeline.JudgeLineMoveEvents.append(DictToJudgeLineEvent(event, 'Move'))
            # for event in judgelinedict['judgeLineRotateEvents']:
            #     judgeline.JudgeLineRotateEvents.append(DictToJudgeLineEvent(event, 'Rotate'))
            judgeline.SetEventsByJudgeLineDict(judgelinedict)
            self.JudgeLineList.append(judgeline)
        gc.collect()
        print(self.NumOfNotes)

    @property
    def NumOfNotes(self):
        Notes = 0
        for i in self.JudgeLineList:
            Notes += i.NumOfNotes
        return Notes

p = PhiChart()
p.Load(r'E:\Lyrith\Chart_AT.json', 'official')

