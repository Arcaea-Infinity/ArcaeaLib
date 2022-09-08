# Phigros Lib Script
# Ver 0.0.2stable by
# @Player01
# Prefs testing by
# @luch4736
# Prefs encrypting method by
# @yuhao


import base64
import urllib
import pyDes
from xml.etree.ElementTree import Element, ElementTree
import xmltodict
from io import TextIOWrapper
import json
import gc

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
    TargetNotes = {
        1: Tap,
        2: Drag,
        3: Hold,
        4: Flick
    }
    return TargetNotes[NoteDict['type']](NoteDict['time'], NoteDict['positionX'], NoteDict['holdTime'], NoteDict['speed'], NoteDict['floorPosition'])

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
            self.__LoadOfficial(self.JsonRaw)
        pass

    def ToOfficial(self):
        pass

    def __LoadOfficial(self, JsonRaw: json) -> None:
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
    def NumOfNotes(self) -> int:
        Notes = 0
        for i in self.JudgeLineList:
            Notes += i.NumOfNotes
        return Notes

def RankDictToStr(d: dict) -> str:
    s = '{'
    for k, v in zip(d.keys(), d.values()):
        s += '"{key}":{value},'.format(key=k, value=v)
    s = s[0:-1] # Delete the last comma
    s += '}'
    return s

def IsRankDict(d: dict) -> bool:
    try: k = d.keys()
    except Exception as e:
        if isinstance(e, AttributeError):
            return False
        raise e
    return True if len(k) == 3 and 'a' in k and 'c' in k and 's' in k and isinstance(d['a'], float) and isinstance(d['c'], int) and isinstance(d['s'], int) else False

def ToString(obj) -> str:
    if IsRankDict(obj):
        return RankDictToStr(obj)
    if isinstance(obj, float):
        if obj.is_integer():
            return '%.1f'% obj
    return str(obj)

def __indent(e, level=0):
    # tab = '\t
    tab = '    '
    indent = '\n' + level * tab
    if len(e):
        if not e.text or not e.text.strip():
            e.text = indent + tab
        if not e.tail or not e.tail.strip():
            e.tail = indent
        for e in e:
            __indent(e, level=level+1)
        if not e.tail or not e.tail.strip():
            e.tail = indent
    else:
        if level and (not e.tail or not e.tail.strip()):
            e.tail = indent

class UnityPlayerPrefs:
    def __init__(self) -> None:
        pass

    def Load(self, file):
        self.file = file
        self.__xmlraw = xmltodict.parse((open(file, 'r', encoding='utf-8')).read())
        self.__ToDict()

    def __ToDict(self):
        extracted = {}
        for i in self.__xmlraw['map']['string']:
            key = UnityPlayerPrefs.DecryptXmlData(i['@name'])
            value = UnityPlayerPrefs.DecryptXmlData(i['#text'])
            # extracted[key].append(value)
            extracted[key] = value
        # Decrypt and restore ints
        for i in self.__xmlraw['map']['int']:
            key = UnityPlayerPrefs.DecryptXmlData(i['@name'])
            value = int(i['@value'])
            # extracted[key].append(value)
            extracted[key] = value
        for i in self.__xmlraw['map']['float']:
            key = UnityPlayerPrefs.DecryptXmlData(i['@name'])
            value = float(i['@value'])
            # extracted[key].append(value)
            extracted[key] = value
        self.__Dict = extracted

    def GetString(self, key: str):
        return self.__Dict[key]

    def GetInt(self, key: str):
        return self.__Dict[key]

    def GetFloat(self, key: str):
        return self.__Dict[key]

    def SetString(self, key: str, value: str):
        self.__Dict[key] = value

    def SetInt(self, key: str, value: int):
        self.__Dict[key] = value

    def SetFloat(self, key: str, value: float):
        self.__Dict[key] = value

    def DeleteAll(self):
        del self.__Dict
        self.__Dict = {}

    def DeleteKey(self, key: str):
        del self.__Dict[key]

    def HasKey(self, key: str):
        try:
            self.__Dict[key]
            return True
        except:
            return False

    @staticmethod
    def EncryptXmlData(value: str):
        return urllib.parse.quote(value, safe = '')

    @staticmethod
    def DecryptXmlData(value: str):
        return urllib.parse.unquote(value)

    def Save(self, file: str):
        map = Element('map')
        tree = ElementTree(map)
        # Write elements
        for key in self.__Dict.keys():
            value = self.__Dict[key]
            if isinstance(value, str):
                e = Element('string', {'name': UnityPlayerPrefs.EncryptXmlData(key)})
                e.text = UnityPlayerPrefs.EncryptXmlData(value)
            elif isinstance(value, int) or isinstance(value, float):
                tag = 'int'
                if isinstance(value, float):
                    tag = 'float'
                e = Element(tag, {'name': UnityPlayerPrefs.EncryptXmlData(key), 'value': str(value)})
        # Make indents for xml
        __indent(map)
        tree.write(file, encoding='utf-8', xml_declaration=True)
        # ElementTree.py:
        # write("<?xml version='1.0' encoding='%s'?>\n" % (declared_encoding,))
        # Change into <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
        content = (open(file, mode='r', encoding='utf-8')).read()
        f = open(file, mode='w', encoding='utf-8')
        content = content.splitlines()
        content[0] = "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>"
        f.write('\n'.join(content))
        f.close()

class PhigrosPlayerPrefsManager(UnityPlayerPrefs):
    def __init__(self) -> None:
        pass

    def Load(self, file):
        super().Load(self, file)
        self.phides = pyDes.des('P\0G\0R\0S\0', pyDes.CBC, 'P\0G\0R\0S\0', pad = None, padmode = pyDes.PAD_PKCS5)

    def __DecryptRawDict(self):
        pass

    def DecryptPhiData(self, value: str):
        return (self.phides.decrypt(base64.b64decode(self.DecryptXmlData(value)))).decode('utf-16-le')

    def DecryptXmlData(self, value: str):
        return urllib.parse.unquote(value)

    def EncryptPhiData(self, value: str):
        return self.EncryptXmlData((base64.b64encode((self.phides.encrypt(value.encode('utf-16-le'))))).decode())

    def EncryptXmlData(self, value: str):
        return urllib.parse.quote(value, safe = '')

# class PhigrosPlayerPrefsManager:
#     def __init__(self) -> None:
#         pass

#     def Load(self, file):
#         self.file = file
#         self.xmlraw = xmltodict.parse((open(file, 'r', encoding='utf-8')).read())
#         self.phides = pyDes.des('P\0G\0R\0S\0', pyDes.CBC, 'P\0G\0R\0S\0', pad = None, padmode = pyDes.PAD_PKCS5)
#         self.DecryptRawDict()

#     def DecryptRawDict(self):
#         # No object have the same @name in PhigrosPayerPrefs
#         decrypted = {}
#         ints = {}
#         strings = {}
#         # Decrypt and restore strings
#         # for i in self.xmlraw['map']['string']:
#         #     if i['@name'] in ['unity.cloud_userid', 'unity.player_session_count', 'unity.player_sessionid']:
#         #         continue # Ignore Unity Data
#         #     key = self.DecryptPhiData(i['@name'])
#         #     decrypted[key] = []
#         # for i in self.xmlraw['map']['int']:
#         #     key = self.DecryptXmlData(i['@name'])
#         #     decrypted[key] = []
#         for i in self.xmlraw['map']['string']:
#             if i['@name'] in ['unity.cloud_userid', 'unity.player_session_count', 'unity.player_sessionid']:
#                 # Unencrypted data
#                 key = i['@name']
#                 value = i['#text']
#                 decrypted[key] = value
#                 strings[key] = value
#                 continue
#             key = self.DecryptPhiData(i['@name'])
#             value = self.DecryptPhiData(i['#text'])
#             try:
#                 value = eval(value)
#             except:
#                 pass
#             # decrypted[key].append(value)
#             decrypted[key] = value
#             strings[key] = value
#         # Decrypt and restore ints
#         for i in self.xmlraw['map']['int']:
#             key = self.DecryptXmlData(i['@name'])
#             value = int(i['@value'])
#             # decrypted[key].append(value)
#             decrypted[key] = value
#             ints[key] = value
#         self.map = decrypted
#         self.ints = ints
#         self.strings = strings

#     def DecryptPhiData(self, value: str):
#         return (self.phides.decrypt(base64.b64decode(self.DecryptXmlData(value)))).decode('utf-16-le')

#     def DecryptXmlData(self, value: str):
#         return urllib.parse.unquote(value)

#     def EncryptPhiData(self, value: str):
#         return self.EncryptXmlData((base64.b64encode((self.phides.encrypt(value.encode('utf-16-le'))))).decode())

#     def EncryptXmlData(self, value: str):
#         return urllib.parse.quote(value, safe = '')

#     def GetRecordId(self, Song: str, Difficulty: str, Artist: None or str = None) -> str or None:
#         # Can get song record id except introduction and aprilfools record
#         # Normal SongRecordId: Songname.Artist.'0' or '1'.'Record'.Difficulty
#         for rec in self.map.keys():
#             l = rec.split('.')
#             if len(l) == 5:
#                 if Artist:
#                     if l[0] == Song and l[1] == Artist and l[4] == Difficulty and l[3] == 'Record':
#                         return rec
#                 else:
#                     if l[0] == Song and l[4] == Difficulty and l[3] == 'Record':
#                         return rec
#         return None

#     def GetAllRecordKeys(self) -> list:
#         k = []
#         for rec in self.map.keys():
#             l = rec.split('.')
#             if len(l) > 2 and l[-2] == 'Record' and l[-1] in ['EZ', 'HD', 'IN', 'AT', 'SP', 'Legacy']:
#                 k.append(rec)
#         return k

#     def PrefsStringModifier(self, name: str, value):
#         self.map[name] = value
#         self.strings[name] = value # Don't forget to modify strings too

#     def PrefsStringDeleter(self, name: str):
#         del self.map[name]
#         del self.strings[name]

#     def PrefsIntModifier(self, name: str, value: int):
#         self.map[name] = value
#         self.ints[name] = value # Don't forget to modify ints too

#     def PrefsIntDeleter(self, name: str):
#         del self.map[name]
#         del self.ints[name]

#     def SetRecordRank(self, RecordId: str, Rank: str):
#         if IsRankDict(Rank):
#             self.PrefsStringModifier(RecordId, Rank)

#     def SetRecordMaxRank(self, RecordId: str):
#         self.SetRecordRank(RecordId, {'a':100.0,'c':1,'s':1000000})

#     def SetAllRecordMaxRank(self):
#         for recordid in self.GetAllRecordKeys():
#             self.SetRecordMaxRank(recordid)

#     def SetChalangeModeRank(self, level: int, rank: int):
#         # Rank
#         # 5: Ranbow 3000000
#         # 4: Gold   2999999-2940000
#         # 3: Orange 2939999-2850000
#         # 2: Blue   2849999-2700000
#         # 1: Green  2699999-2460000
#         # No rank below 2460000
#         self.PrefsStringModifier('ChallengeModeRank', int(str(rank)+str(level)))

#     def SetPlayerIcon(self, icon: str):
#         self.PrefsStringModifier('UserIconKeyName', icon)

#     def RemoveAllRecord(self):
#         for r in self.GetAllRecordKeys():
#             self.PrefsStringDeleter(r)

#     def SetPlayerName(self, name: str):
#         self.PrefsStringModifier('playerID', name)

#     def SetPlayerSelfIntro(self, content: str):
#         self.PrefsStringModifier('selfIntro', content)

#     def SetData(self, kba:int, kb:int, mb:int, tb:int, pb:int):
#         # KB After Demical Point, KB, MB, TB, PB
#         # NumOfMoney1, NumOfMoney2, NumOfMoney3, NumOfMoney4, NumOfMoney5
#         data = [kba, kb, mb, tb, pb]
#         key = ['NumOfMoney1', 'NumOfMoney2', 'NumOfMoney3', 'NumOfMoney4', 'NumOfMoney5']
#         for p in range(5):
#             self.PrefsStringModifier(key[p], data[p])

#     def Save(self, file: str):
#         map = Element('map')
#         tree = ElementTree(map)
#         # Write elements
#         for string in self.strings.keys():
#             if string in ['unity.cloud_userid', 'unity.player_session_count', 'unity.player_sessionid']:
#                 e = Element('string', {'name': string})
#                 e.text = str(self.strings[string])
#             else: # Need to encrypt
#                 e = Element('string', {'name': self.EncryptPhiData(string)})
#                 e.text = self.EncryptPhiData(ToString(self.strings[string]))
#             map.append(e)
#         for intkey in self.ints.keys():
#             e = Element('int', {'name': self.EncryptXmlData(intkey), 'value': str(self.ints[intkey])})
#             map.append(e)
#         # Make indents for xml
#         __indent(map)
#         tree.write(file, encoding='utf-8', xml_declaration=True)
#         # ElementTree.py:
#         # write("<?xml version='1.0' encoding='%s'?>\n" % (declared_encoding,))
#         # Change into <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
#         content = (open(file, mode='r', encoding='utf-8')).read()
#         f = open(file, mode='w', encoding='utf-8')
#         content = content.splitlines()
#         content[0] = "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>"
#         f.write('\n'.join(content))
#         f.close()

#     def SaveUnencrypted(self, file):
#         map = Element('map')
#         tree = ElementTree(map)
#         # Write elements
#         for string in self.strings.keys():
#             e = Element('string', {'name': string})
#             e.text = ToString(self.strings[string])
#             map.append(e)
#         for intkey in self.ints.keys():
#             e = Element('int', {'name': intkey, 'value': str(self.ints[intkey])})
#             map.append(e)
#         # Make indents for xml
#         __indent(map)
#         tree.write(file, encoding='utf-8', xml_declaration=True)


