import untangle
import sys, os, time, configparser

ct2vecWatermark = """
       _   ___                 
      | | |__ \                
   ___| |_   ) |_   _____  ___ 
  / __| __| / /\ \ / / _ \/ __|
 | (__| |_ / /_ \ V /  __/ (__ 
  \___|\__|____| \_/ \___|\___|
                               
"""

ct2vecSealOfQuality = """
\n// Generated with ct2vec 1.0
\n// Made by Lungu#0001
"""

default_ini = """; to disable a setting, comment out it by adding ';' at the start of the line
[settings]
; add after every line a comment with the base address and the type of pointer
addComments=True"""

def formatEntryName(name: str):
    resultString = ""
    weird_chars = "\`\'\" ()[]{}-=,.;@!£$%^&*+~#/?><\\|¬"
    for char in name:
        if char not in weird_chars:
            resultString += char
    return numbersAsSuffix(resultString)

def numbersAsSuffix(name: str):
    numbers = "0123456789"
    resultString = ""
    if (name[0] in numbers):
        suffix = ""
        counter = 0
        for char in name:
            if char in numbers:
                suffix += char
            else:
                break
            counter+=1
        resultString = name[counter:] + suffix
    else:
        resultString = name
    return resultString

def listToPrettyString(_list: list):
    offsets = _list[::-1]
    returnString = ""
    counter = 1
    for element in offsets:
        returnString += "0x{}".format(element)
        if (counter < len(offsets)):
            returnString += ", "
        counter+=1

    return returnString

class Pointer:
    def __init__(self, object):
        self._object = object

        self.name = "NA"
        try:
            self.name = formatEntryName(self._object.Description.cdata)
        except AttributeError:
            pass

        self.base = "NA"
        try:
            self.base = self._object.Address.cdata
        except AttributeError:
            pass

        self.offsets = []
        try:
            _offsets = self._object.Offsets.Offset
            for offset in _offsets:
                self.offsets.append(offset.cdata)
        except AttributeError:
            self.offsets = "NA"
        
        self.type = "NA"
        try:
            self.type = formatEntryName(self._object.VariableType.cdata)
        except AttributeError:
            pass

        self.subPointers = []
        try:
            subPointers = self._object.CheatEntries.CheatEntry
            for subPointer in subPointers:
                self.subPointers.append(Pointer(subPointer))
        except Exception:
            pass
    
    def pprint(self, comments=False):
        output = ""
        if self.offsets != "NA":
            output = "\n"
            if comments:
                output += "std::vector<uint64_t> {} = {}; // Base: {}; Type: {}".format(self.name, "{"+listToPrettyString(self.offsets)+"}", self.base, self.type)
            else:
                output += "std::vector<uint64_t> {} = {};".format(self.name, "{"+listToPrettyString(self.offsets)+"}")

        if self.subPointers != []:
            for i in self.subPointers:
                output += "\n" + i.pprint(comments)
        
        return output

def ct2vec(path, console=True):
    if console:
        os.system("cls")
    try:
        file = open(path)
    except Exception:
        path = input("Cheat table file: ")
        file = open(path)
    
    print(ct2vecWatermark)

    xmlContent = file.read()
    file.close()

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isfile(os.path.join(application_path, 'config.ini')):
        f = open(os.path.join(application_path, "config.ini"), 'w')
        f.write(default_ini)
        f.close()
    
    configFile = configparser.ConfigParser()
    configFile.read(os.path.join(application_path, 'config.ini'))
    
    try:
        comments = configFile.getboolean('settings','addComments')
    except Exception:
        print("Can't access config.ini file, using default settings")
        comments = False
    
    outputFilePath = os.path.join(application_path, "output.txt")
    outputFile = open(outputFilePath, "w")

    startTime = time.time()
    _input = untangle.parse(xmlContent).CheatTable.CheatEntries.CheatEntry
    for entry in _input:
        pointer = Pointer(entry)
        outputFile.write(pointer.pprint(comments))
    
    outputFile.write(ct2vecSealOfQuality)
    outputFile.close()

    endTime = round(time.time() - startTime, 3)

    lines = ""

    with open(outputFilePath, "r") as file:
        for line in file:
            if (line != "\n"):
                lines += line
    
    with open(outputFilePath, "w") as file:
        file.write(lines)

    print("Result saved to file: {}".format(outputFilePath))
    print("Conversion finished in {}s".format(endTime))
    

    
    if console:
        os.system("pause")

if __name__ == '__main__':
    ct2vec(sys.argv[1], True)
