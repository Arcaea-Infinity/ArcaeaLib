class StringParser:
    def __init__(self, str:str):
        self.base = str
        self.pos = 0
    base = ""
    pos = 0

    # bool ? x : y convert to python:
    # x if bool else y

    # str.substring(start, length) convert to python:
    # str[start:start+length]

    def Skip(self, length):
        if type(length) == int:
            self.pos += length
        elif type(length) == str:
            self.pos += len(length)

    def ReadFloat(self, terminator = None):
        end = self.base.find(terminator, self.pos) if terminator != None else (int(len(self.base)) - 1)
        value = float(self.base[self.pos:end])
        self.pos += (end - self.pos + 1)
        return value

    def ReadInt(self, terminator = None):
        end = self.base.find(terminator, self.pos) if terminator != None else (int(len(self.base)) - 1)
        value = int(self.base[self.pos:end])
        self.pos += (end - self.pos + 1)
        return value

    def ReadBool(self, terminator = None):
        end = self.base.find(terminator, self.pos) if terminator != None else (int(len(self.base)) - 1)
        value = bool(self.base[self.pos:end].lower() == "true")
        self.pos += (end - self.pos + 1)
        return value

    def ReadString(self, terminator = None):
        end = self.base.find(terminator, self.pos) if terminator != None else (int(len(self.base)) - 1)
        value = self.base[self.pos:end]
        self.pos += (end - self.pos + 1)
        return value

    def Current(self):
        return self.base[self.pos]

    def Peek(self, length = 1):
        return self.base[self.pos:self.pos + length]

    def TryReadFloat(self, terminator = None):
        try:
            return self.ReadFloat(terminator)
        except:
            return 0

    def TryReadInt(self, terminator = None):
        try:
            return self.ReadInt(terminator)
        except:
            return 0

    def CanReadFloat(self, terminator = None):
        originPos = pos
        try:
            self.ReadFloat(terminator)
            pos = originPos
            return True
        except:
            pos = originPos
            return False

    def CanReadInt(self, terminator = None):
        originPos = pos
        try:
            self.ReadInt(terminator)
            pos = originPos
            return True
        except:
            pos = originPos
            return False
