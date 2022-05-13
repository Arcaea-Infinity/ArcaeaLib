import ArcaeaLib
import math

Width = 1920
Height = 1080
CanvasW = [Width * 0.33, Width * 0.71]
CanvasH = [Height * 0.81, Height * 0.37]
JudgeArea = [CanvasW[1] - CanvasW[0], CanvasH[0] - CanvasH[1]]

class Slot:
    def __init__(self, SlotId, Time, X, Y):
        self.SlotId = SlotId
        self.Events = [[2, X, Y, Time]]
    
    def addEvent(self, Time, X, Y):
        self.TimeList.append([2, X, Y, Time])
    
    def press(self, Time):
        self.Events.append(0, Time)
    
    def unpress(self, Time):
        self.Events.append(1, Time)