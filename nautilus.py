# Initialising
users = ["root"]
user = users[0]
nodes = []

# Directory class to make life a little easier
class Directory:
    def __init__(self, path, parent):
        self.name = path.split('/')[-1]
        self.parent = parent
        self.children = []
        self.owner = user
        self.perms = [[user, "rwx"],["group", "r-x"]]
        self.path = path

    def addChild(self, child):
        self.children.append(child)
    def getName(self):
        return self.name 
    def getChildren(self):
        return self.children
    def getParent(self):
        return self.parent
    def getOwner(self):
        return self.owner
    def getPath(self):
        return self.path
    def getPerms(self):
        return self.perms
    def setPerms(self, perms):
        self.perms = perms
    def isDir(self):
        return True
    def remChild(self, child):
        self.children.remove(child)
    def setOwner(self, owner):
        self.owner = owner
        self.perms[0][0] = owner

# Define class before defining home node
# Create a false base to make later processing easier
rootParent = Directory("///", None)
# Create root node and append to list of accessible nodes
nodes.append(Directory("/", rootParent))
cDir = nodes[0]

# File class to make life a little easier, mirrors most attributes of directory class.
class File:
    def __init__(self, path, parent):
        self.name = path.split('/')[-1]
        self.parent = parent
        self.owner = user
        self.perms = [[user, "rw-"],["group", "r--"]]
        self.path = path
    
    def getName(self):
        return self.name
    def getPath(self):
        return self.path
    def getPerms(self):
        return self.perms
    def getParent(self):
        return self.parent
    def getOwner(self):
        return self.owner
    def getChildren(self):
        return []
    def isDir(self):
        return False
    def setPerms(self, perms):
        self.perms = perms
    def setOwner(self, owner):
        self.owner = owner
        self.perms[0][0] = owner

# Useful functions
# Check if only valid characters are user
def sanityCheck(cmdChecked):
    for cmd in cmdChecked:
        for char in cmd:
            if not (char.isalnum() or (char in ' -_/.')):
                return False
    return True
# Check commands to deal with quotation marks
def checkCmd(cmds):
    cmdChecked = []
    i = 0
    while i < len(cmds):
        temp = cmds[i]
        # Combines items which are bound by quotation marks. Raises error if only 1 is used.
        if cmds[i][0] == '"':
            temp = cmds[i][1:]
            if temp[-1] == '"':
                temp = temp[:-1]
            else:
                i += 1
                if i >= len(cmds):
                    return False
                while cmds[i][-1] != '"':
                    temp += " " + cmds[i]
                    i += 1
                    if i >= len(cmds):
                        return False
                temp += " " + cmds[i][:-1]
        elif cmds[i][-1] == '"':
            return False
        cmdChecked.append(temp)
        i += 1
    return cmdChecked
# Finding files or directories: doing preprocessing using find() and recursively finding using recursiveFindDir()
def recursiveFindDir(tempNode, dPath):
    # If folders left to look through = 0, node must be found
    if len(dPath) == 0:
        return (tempNode, True)
    # Special processing for . and ..
    if dPath[0] == '.':
        return recursiveFindDir(tempNode, dPath[1:])
    if dPath[0] == '..':
        if tempNode == nodes[0]:
            if len(dPath) == 1:
                return (tempNode, True)
            else:
                return recursiveFindDir(tempNode, dPath[1:])
        else:
            if len(dPath) == 1:
                return (tempNode.getParent(), True)
            else:
                return recursiveFindDir(tempNode.getParent(), dPath[1:])
    # The actual recusive path calling function again if necessary
    for child in tempNode.getChildren():
        if (child.getName() == dPath[0]):
            if child.isDir():
                return recursiveFindDir(child, dPath[1:])
            else:
                if len(dPath) == 1:
                    if tempNode == nodes[0] and (child.getPath() == ("/" + dPath[-1])):
                        return (child, True)
                    elif child.getPath() == (tempNode.getPath() + "/" + dPath[-1]):
                        return (child, True)
                else:
                    return (child, False)
    return (tempNode, False)
def find(dir, dPath):
# Need options for both relative and absolute paths (check first letter to be /)
# Processing to make recursive find work
    if dir[0] == "/":
        tempNode = nodes[0]
    else:
        tempNode = cDir

    if len(dPath) == 1:
        if dPath[0] == "":
            return (tempNode, True)
    if len(dPath) > 1:
        if dPath[0] == "":
            dPath = dPath[1:]
        if dPath[-1] == "":
            dPath = dPath[:-1]
    return recursiveFindDir(tempNode, dPath)
# Find permissions: currentPerms() does given file, recursivePerms() does ancestors
def recursivePerms(tempNode, perms):
    if tempNode == nodes[0].getParent():
        return True
    elif user == users[0]:
        return True
    elif currentPerms(tempNode, perms):
        return recursivePerms(tempNode.getParent(), perms)
    else:
        return False
def currentPerms(tempNode, perms):
    if user == users[0]:
        return True
# Get perms returns strings with length 3, rwx
    tempPerms = tempNode.getPerms()
    if tempPerms[0][0] == user:
        for c in perms:
            if c not in tempPerms[0][1]:
                return False
        return True
    else:
        for c in perms:
            if c not in tempPerms[1][1]:
                return False
        return True
# Check if the appropriate amount arguments are given
def validCheck(cmd, min, max=0):
    vars = len(cmd)
    if vars < min:
        print(cmd[0] + ": Invalid syntax")
        return False
    if max != 0:
        if vars > max:
            print(cmd[0] + ": Invalid syntax")
            return False
    return True

# Functions for commands
# Change directory command
def cd(dir):
    # Declaring global is a bit touchy but makes sense in this circumstance.
    global cDir
    (found, foundFlag) = find(dir, dir.split("/"))
    if dir == "..":
        if cDir != nodes[0]:
            cDir = cDir.getParent()
    elif not foundFlag:
        print("cd: No such file or directory")
    elif not found.isDir():
        print("cd: Destination is a file")
    else:
        if currentPerms(found, "x"):
            cDir = found
        else:
            print("cd: Permission denied")  
# 3 options for Make directory: mkdir() is non-recursive and mkdirP() is the intitialising for recursively making dirs
# mkdirPR will recursively make these dirs
def mkdir(flag, pFlag):
    dir = flag
    if dir[-1] == "/":
        dir = flag[:-1]
    dirR = dir.split("/")
    (found, foundFlag) = find(flag, dirR[:-1])
    (made, madeFlag) = find(flag, dirR)
    if foundFlag != False:
        if madeFlag == False:
            if currentPerms(found, "w") and recursivePerms(found, "x"):
                if dir[0] == "/":
                    nodes.append(Directory(dir, found))
                elif cDir == nodes[0]:
                    nodes.append(Directory(("/" + dir), found))
                else:
                    nodes.append(Directory((cDir.getPath() + "/" + dir), found))
                found.addChild(nodes[-1])
                return True
            else:
                print("mkdir: Permission denied")
        elif not pFlag:
            print("mkdir: File exists")
    elif not pFlag:
        print("mkdir: Ancestor directory does not exist")
    return False
def mkdirPR(tempNode, dirR):
    if len(dirR) == 0:
        return True
    if dirR[0] != ".":
        if dirR[0] != "..":
            dirs = tempNode.getPath().split("/")
            if tempNode == nodes[0]:
                dirs = [""]
            dirs.append(dirR[0])
            if find(tempNode.getPath(), dirs)[1] == False:
                # Calls mkdir to shorten code except with the pFlag preventing error messages
                if tempNode == nodes[0]:
                    mkdir("/" + dirR[0], True)
                else:
                    mkdir(tempNode.getPath() + "/" + dirR[0], True)
            tempNode = find(tempNode.getPath(), dirs)[0]
        else:
            if tempNode != nodes[0]:
                tempNode = tempNode.getParent()
    return mkdirPR(tempNode, dirR[1:])
def mkdirP(flag):
    # Processing for the recursive function
    dir = flag
    if dir[-1] == "/":
        dir = flag[:-1]
    dirR = dir.split("/")
    if mkdir(flag, True):
        return True
    else:
        tempNode = 0
        if dirR[0] == "":
            dirR = dirR[1:]
            tempNode = nodes[0]
        else:
            tempNode = cDir
        mkdirPR(tempNode, dirR)
# Make needed directories for root folder
# Touch command
def touch(flags):
    for dir in flags:
        if dir[-1] != "/":
            dirR = dir.split("/")
            (found, foundFlag) = find(dir, dirR[:-1])
            (made, madeFlag) = find(dir, dirR)
            if madeFlag == False:
                if not made.isDir():
                    print("touch: Ancestor directory does not exist")
                    return False
                if foundFlag != False:
                    if (recursivePerms(found, "x") != False) and (currentPerms(found, "w") != False):
                        if dir[0] == "/":
                            nodes.append(File(dir, found))
                        elif cDir == nodes[0]:
                            nodes.append(File(("/" + dir), found))
                        else:
                            nodes.append(File((cDir.getPath() + "/" + dir), found))
                        found.addChild(nodes[-1])
                    else:
                        print("touch: Permission denied")
                else:
                    print("touch: Ancestor directory does not exist")
# Copy command
def cp(flags):
    if flags[1][0] != "/":
        if cDir == nodes[0]:
            flags[1] = "/" + flags[1]
        else:
            flags[1] = cDir.getPath() + "/" + flags[1]
    (source, srcFlag) = find(flags[0], flags[0].split("/"))
    (dst, dstFlag) = find(flags[1], flags[1].split("/"))
    if srcFlag == False:
        print("cp: No such file")
    elif dstFlag == False:
        if not dst.isDir():
            print("cp: No such file or directory")
            return False
        if flags[1][-1] == "/":
            print("cp: Destination is a directory")
        else:
            if source.isDir():
                print("cp: Source is a directory")
                return False
            parentS = source.getParent()
            (parentD, parentDFlag) = find(flags[1], flags[1].split("/")[:-1])
            if parentDFlag == True:
                if parentD.isDir():
                    if currentPerms(source, "r") and currentPerms(parentD, "w") \
                        and recursivePerms(parentS, "x") and recursivePerms(parentD, "x"):
                        nodes.append(File(flags[1], parentD))
                        parentD.addChild(nodes[-1])
                    else:
                        print("cp: Permission denied")      
            else:
                print("cp: No such file or directory")
    elif dst.isDir():
        print("cp: Destination is a directory")
    else:
        print("cp: File exists")
# Move command
def mv(flags):
    (src, srcFlag) = find(flags[0], flags[0].split("/"))
    (dst, dstFlag) = find(flags[1], flags[1].split("/"))
    if flags[1][0] != "/":
        if cDir == nodes[0]:
            flags[1] = "/" + flags[1]
        else:
            flags[1] = cDir.getPath() + "/" + flags[1]
    if srcFlag == False:
        print("mv: No such file")
    else:
        if dstFlag == False:
            if src.isDir():
                print("mv: Source is a directory")
            else:
                if flags[1][-1] == "/":
                    print("mv: Destination is a directory")
                else:
                    (parentD, parentDFlag) = find(flags[1], flags[1].split("/")[:-1])
                    parentS = src.getParent()
                    if (parentDFlag == False) or (not parentD.isDir()):
                        print("mv: No such file or directory")
                    else:
                        if currentPerms(parentS, "w") and currentPerms(parentD, "w") \
                            and recursivePerms(parentS, "x") and recursivePerms(parentD, "x"):
                            nodes.append(File(flags[1], parentD))
                            parentD.addChild(nodes[-1])
                            # Similar to copy command except removes the file after copying
                            # And slightly different in other ways.
                            rm([src.getPath()])
                        else:
                            print("mv: Permission denied")
        elif dst.isDir():
            print("mv: Destination is a directory")
        else:
            print("mv: File exists")
# Remove command
def rm(flags):
    for flag in flags:
        (file, fileFlag) = find(flag, flag.split("/"))
        if fileFlag != False:
            if file.isDir() == False:
                parent = file.getParent()
                if currentPerms(file, "w") and currentPerms(parent, "w") and recursivePerms(parent, "x"):
                    parent.remChild(file)
                    nodes.remove(file)
                else:
                    print("rm: Permission denied")
            else:
                print("rm: Is a directory")
        else:
            print("rm: No such file")
# Remove directory command
def rmDir(flags):
    for flag in flags:
        (dir, dirFlag) = find(flag, flag.split("/"))
        if dir == nodes[0] and cDir != nodes[0]:
            print("rmdir: Directory not empty")
            return False
        if dirFlag:
            if dir.isDir() == True:
                parent = cDir
                while parent != nodes[0].getParent():
                    if parent == dir:
                        print("rmdir: Cannot remove pwd")
                        return False
                    parent = parent.getParent()
                if dir.getChildren() == []:
                    parent = dir.getParent()
                    if currentPerms(parent, "w") and recursivePerms(parent, "x"):
                        parent.remChild(dir)
                        nodes.remove(dir)
                    else:
                        print("rmdir: Permission denied")
                else:
                    print("rmdir: Directory not empty")
            else:
                print("rmdir: Not a directory")
        else:
            print("rmdir: No such file or directory")
# 2 commands for changing permissions
# chmod() is for processing recursive and non-recursive changing perms
# chmodCmd() changes perms with a flag for recursion
def chmodCmd(found, u, p, op, recursive):
    if (found.getOwner() == user) or (user == users[0]):
        if recursivePerms(found, "x"):
            perms = found.getPerms()
            userPerms = list(perms[0][1])
            otherPerms = list(perms[1][1])
            if op == "=":
                for c in u:
                    if c == "u" or c == "a":
                        userPerms = ["-", "-", "-"]
                        for l in p:
                            if l == "r":
                                userPerms[0] = "r"
                            elif l == "w":
                                userPerms[1] = "w"
                            elif l == "x":
                                userPerms[2] = "x"
                    if c == "o" or c == "a":
                        otherPerms = ["-", "-", "-"]
                        for l in p:
                            if l == "r":
                                otherPerms[0] = "r"
                            elif l == "w":
                                otherPerms[1] = "w"
                            elif l == "x":
                                otherPerms[2] = "x"
            elif op == "+":
                for c in u:
                    if c == "u" or c == "a":
                        for l in p:
                            if l == "r":
                                userPerms[0] = "r"
                            elif l == "w":
                                userPerms[1] = "w"
                            elif l == "x":
                                userPerms[2] = "x"
                    if c == "o" or c == "a":
                        for l in p:
                            if l == "r":
                                otherPerms[0] = "r"
                            elif l == "w":
                                otherPerms[1] = "w"
                            elif l == "x":
                                otherPerms[2] = "x"  
            elif op == "-":
                for c in u:
                    if c == "u" or c == "a":
                        for l in p:
                            if l == "r":
                                userPerms[0] = "-"
                            elif l == "w":
                                userPerms[1] = "-"
                            elif l == "x":
                                userPerms[2] = "-"
                    if c == "o" or c == "a":
                        for l in p:
                            if l == "r":
                                otherPerms[0] = "-"
                            elif l == "w":
                                otherPerms[1] = "-"
                            elif l == "x":
                                otherPerms[2] = "-" 
            perms[0][1] = "".join(userPerms)
            perms[1][1] = "".join(otherPerms)
            found.setPerms(perms)      

        else:
            print("chmod: Permission denied")
    else:
        print("chmod: Operation not permitted")

    if recursive:
        for child in found.getChildren():
            chmodCmd(child, u, p, op, True)
def chmod(flags, recursive):
    flag = flags[0]
    u, p = 0, 0
    charTrue = False
    char2True = False
    op = ""
    for char in "-+=":
        if len(flag.split(char)) == 2:
            if charTrue:
                char2True = True
            charTrue = True
            u, p = flag.split(char)
            op = char
    if char2True or not charTrue:
        print("chmod: Invalid mode")
    else:
        tempFlag = True
        for c in u:
            if c not in "uoa":
                tempFlag = False
        for c in p:
            if c not in "rwx-":
                tempFlag = False

        if tempFlag:
            for dir in flags[1:]:
                (found, foundFlag) = find(dir, dir.split("/"))
                if foundFlag == False:
                    print("chmod: No such file or directory")
                else:
                    chmodCmd(found, u, p, op, recursive)
        else:
            print("chmod: Invalid mode")
# Change perms for rootParent directory (false base) to make life easier
chmodCmd(rootParent, "a", "rwx", "=", False)
# 3 commands for changing owners
# chown() changes for current file
# chownR() is processing to change recursive and chownRecursive() does this
def chownRecursive(dir, owner):
    dir.setOwner(owner)
    for child in dir.getChildren():
        chownRecursive(child, owner)
def chownR(flags):
    if flags[0] in users:
        for dir in flags[1:]:
            (found, foundFlag) = find(dir, dir.split("/"))
            if foundFlag == False:
                print("chown: No such file or directory")
            else:
                chownRecursive(found, flags[0])
    else:
        print("chown: Invalid user")
def chown(flags):
    if flags[0] in users:
        for dir in flags[1:]:
            (found, foundFlag) = find(dir, dir.split("/"))
            if foundFlag == False:
                print("chown: No such file or directory")
            else:
                found.setOwner(flags[0])
    else:
        print("chown: Invalid user")
# ls command, quite long due to various flags and options
def ls(flags):
    global cDir
    if len(flags) == 0:
        tempDir = cDir
        if recursivePerms(tempDir, "x"):
            files = []
            if currentPerms(tempDir, "r"):
                files = tempDir.getChildren().copy()
            else:
                print("ls: Permission denied")
                return
            toRemove = []
            for file in files:
                if len(file.getName()) > 0:
                    if file.getName()[0] == ".":
                        toRemove.append(file)
            for file in toRemove:
                files.remove(file)
            for file in files:
                print(file.getName())
        else:
            print("ls: Permission denied")
    else:
        found = 0
        foundFlag = True
        pFlag = None
        if flags[-1][0] == "-":
            found = cDir
        else:
            (found, foundFlag) = find(flags[-1], flags[-1].split("/"))
            pFlag = -1
        if foundFlag == False:
            print("ls: No such file or directory")
        else:
            aFlag = False
            dFlag = False
            lFlag = False
            allFlag = True
            for flag in flags[:pFlag]:
                if flag == "-a" and not aFlag:
                    aFlag = True
                elif flag == "-d" and not dFlag:
                    dFlag = True
                elif flag == "-l" and not lFlag:
                    lFlag = True
                else:
                    print("ls: Invalid syntax")
                    allFlag = False
                    break
            if allFlag:
                if recursivePerms(found.getParent(), "x"):
                    files = []
                    if dFlag or (not found.isDir()):
                        if currentPerms(found.getParent(), "r"):
                            files = [found]
                            dFlag = True
                        else:
                            print("ls: Permission denied")
                            return
                    elif currentPerms(found, "r"):
                        files = found.getChildren().copy()
                        files.sort(key=lambda x: x.name)
                    else:
                        print("ls: Permission denied")
                        return
                    if not aFlag:
                        if dFlag:  
                            if flags[-1][0] == ".":
                                files = []
                        toRemove = []
                        for file in files:
                            if len(file.getName()) > 0:
                                if file.getName()[0] == ".":
                                    toRemove.append(file)
                        for file in toRemove:
                            files.remove(file)
                    if aFlag and found.isDir() and not dFlag:
                        files = [Directory(".", rootParent), Directory("..", rootParent)] + files
                    for file in files:
                        string = ""
                        if lFlag:
                            if file.isDir():
                                string += "d"
                            else:
                                string += "-"
                            string += file.getPerms()[0][1] + file.getPerms()[1][1] + " "
                            string += file.getOwner() + " " 
                        if dFlag and flags[-1][0] != "-":
                            string += flags[-1]
                        elif file != nodes[0]:
                            string += file.getName()
                        else:
                            string += "."
                            if not aFlag:
                                string = ""
                        if len(string.strip()) > 0:
                            print(string)
                else:
                    print("ls: Permission denied")
                
# Checking for which command is used, some commands processed inside here
# There is general preprocessing as well to ensure commands are valid and able to be executed
def check(cmd):
    cmds = cmd.split()
    cmdC = cmds[0]
    cmdChecked = checkCmd(cmds)


    if cmdChecked == False:
        print(cmdC + ": Missing double quote")
    else:
        for flag in cmdChecked[1:]:
            if cmdC == flag:
                print(cmdC + ": Invalid syntax")
                return False
        if not sanityCheck(cmdChecked) and cmdC != "chmod":
            # This is due to chmod having more valid characters (checked seperately)
            print(cmdC + ": Invalid syntax")
        elif cmdC == "exit":
            global user
            if validCheck(cmdChecked, 1, 1):
                print("bye,", user)
                exit()
        elif cmdC == "pwd":
            if validCheck(cmdChecked, 1, 1):
                print(cDir.getPath())
        elif cmdC == "cd":
            if validCheck(cmdChecked, 2, 2):
                cd(cmdChecked[1])
        elif cmdC == "mkdir":
            if validCheck(cmdChecked, 2):
                if cmdChecked[1][0] == "-":
                    if cmdChecked[1] == "-p":
                        if validCheck(cmdChecked, 3):
                            flags = cmdChecked[2:]
                            for dir in flags:

                                mkdirP(dir)
                    else:
                        print("mkdir: Invalid syntax")
                else:
                    flags = cmdChecked[1:]
                    for dir in flags:
                        mkdir(dir, False)
        elif cmdC == "touch":
            if validCheck(cmdChecked, 2):
                touch(cmdChecked[1:])
        elif cmdC == "cp":
            if validCheck(cmdChecked, 3, 3):
                cp(cmdChecked[1:])
        elif cmdC == "mv":
            if validCheck(cmdChecked, 3, 3):
                mv(cmdChecked[1:])
        elif cmdC == "rm":
            if validCheck(cmdChecked, 2):
                rm(cmdChecked[1:])
        elif cmdC == "rmdir":
            if validCheck(cmdChecked, 2):
                rmDir(cmdChecked[1:])
        elif cmdC == "chmod":
            if validCheck(cmdChecked, 2):
                flag = True
                for c in cmd:
                    if not sanityCheck(c) and c not in "+=-":
                        flag = False
                        break
                if flag:
                    if cmdChecked[1][0] == "-":
                        if cmdChecked[1] == "-r":
                            if validCheck(cmdChecked, 3):
                                chmod(cmdChecked[2:], True)
                        else:
                            print("chmod: Invalid syntax")
                    else:
                        chmod(cmdChecked[1:], False)
                else:
                    print("Invalid characters")
        elif cmdC == "chown":
            if validCheck(cmdChecked, 3):
                if user == users[0]:
                    if cmdChecked[1][0] == "-":
                        if cmdChecked[1] == "-r":
                            if validCheck(cmdChecked, 3):
                                chownR(cmdChecked[2:])
                    else:
                        chown(cmdChecked[1:])
                else:
                    print("chown: Operation not permitted")
        elif cmdC == "adduser":
            # Adding a user to the userlist
            if validCheck(cmdChecked, 2, 2):
                if user == users[0]:
                    if cmdChecked[1] in users:
                        print("adduser: The user already exists")
                    else:
                        users.append(cmdChecked[1])
                else:
                    print("adduser: Operation not permitted")
        elif cmdC == "deluser":
            # Deleting a user from the userlist with a special statement printed for root
            if validCheck(cmdChecked, 2, 2):
                if user == users[0]:
                    if cmdChecked[1] in users:
                        if cmdChecked[1] == users[0]:
                            print("WARNING: You are just about to delete the root account")
                            print("Usually this is never required as it may render the whole system unusable")
                            print("If you really want this, call deluser with parameter --force")
                            print("(but this `deluser` does not allow `--force`, haha)")
                            print("Stopping now without having performed any action")
                        else:
                            users.remove(cmdChecked[1])
                    else:
                        print("deluser: The user does not exist")
                else:
                    print("deluser: Operation not permitted")
        elif cmdC == "su":
            # Swapping to a user in the userlist
            if validCheck(cmdChecked, 1, 2):
                if len(cmdChecked) == 1:
                    user = users[0]
                else:
                    if cmdChecked[1] in users:
                        user = cmdChecked[1]
                    else:
                        print("su: Invalid user")     
        elif cmdC == "ls":
            if validCheck(cmdChecked, 1, 5):
                ls(cmdChecked[1:])
        else:
            print(cmdC + ": Command not found")

# Infinite loop until exited, calls nodes to stop references from being wiped
def main():
    while True:
        nodes
        cmd = (input(user + ":" + cDir.getPath() + "$ "))
        if len(cmd.strip()) != 0:
            check(cmd)

if __name__ == '__main__':
    main()