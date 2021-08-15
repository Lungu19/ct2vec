import untangle
import sys, os, time, configparser, re

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

class Pointer:
    def __init__(self, object):
        self._object = object

        self.name = "NA"
        try:
            self.name = self.formatEntryName(self._object.Description.cdata)
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
            self.type = self.formatEntryName(self._object.VariableType.cdata)
        except AttributeError:
            pass

        self.subPointers = []
        try:
            subPointers = self._object.CheatEntries.CheatEntry
            for subPointer in subPointers:
                self.subPointers.append(Pointer(subPointer))
        except Exception:
            pass
    
    def listToPrettyString(self, offsets: list):
        offsets = offsets[::-1]
        returnString = ""
        counter = 1
        for element in offsets:
            returnString += "0x{}".format(element)
            if (counter < len(offsets)):
                returnString += ", "
            counter+=1

        return returnString
    
    def numbersAsSuffix(self, name: str):
        if (name[0] in "0123456789"):
            suffix = ""
            counter = 0
            for char in name:
                if char in "0123456789":
                    suffix += char
                else:
                    break
                counter+=1
            return name[counter:] + suffix
        else:
            return name
    
    def formatEntryName(self, name: str):
        return self.numbersAsSuffix(name.translate(str.maketrans('', '', "\`\'\" ()[]{}-=,.;@!£$%^&*+~#/?><\\|¬")))
    
    def pprint(self, comments=False):
        output = ""
        if self.offsets != "NA":
            output = "\n"
            if comments:
                output += "std::vector<uint64_t> {} = {}; // Base: {}; Type: {}".format(self.name, "{"+self.listToPrettyString(self.offsets)+"}", self.base, self.type)
            else:
                output += "std::vector<uint64_t> {} = {};".format(self.name, "{"+self.listToPrettyString(self.offsets)+"}")

        for i in self.subPointers:
            output += "\n" + i.pprint(comments)
        
        return output

class ct2vecApp:
    def __init__(self, path, console=True):
        self.console = console
        if self.console:
            os.system("cls")
        try:
            file = open(path)
        except Exception:
            path = input("Cheat table file path: ")
            file = open(path)

        print(ct2vecWatermark)

        self.xmlContent = file.read()
        file.close()

        if getattr(sys, 'frozen', False):
            self.appPath = os.path.dirname(sys.executable)
        else:
            self.appPath = os.path.dirname(os.path.abspath(__file__))
    def run(self):
        if not os.path.isfile(os.path.join(self.appPath, 'config.ini')):
            f = open(os.path.join(self.appPath, "config.ini"), 'w')
            f.write(default_ini)
            f.close()

        configFile = configparser.ConfigParser()
        configFile.read(os.path.join(self.appPath, 'config.ini'))

        try:
            commentsBool = configFile.getboolean('settings','addComments')
        except Exception:
            print("Can't access config.ini file, using default settings")
            commentsBool = False

        outputFilePath = os.path.join(self.appPath, "output.txt")
        outputFile = open(outputFilePath, "w")

        startTime = time.time()
        _input = untangle.parse(self.xmlContent).CheatTable.CheatEntries.CheatEntry
        for entry in _input:
            pointer = Pointer(entry)
            outputFile.write(pointer.pprint(commentsBool))

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

        if self.console:
            os.system("pause")
    

if __name__ == '__main__':
    app = ct2vecApp(sys.argv[1], True)
    app.run()
