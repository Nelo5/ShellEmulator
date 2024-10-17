import sys
import re
import tarfile

def char_to_int(new_mode,current_mode):
    mode_changes = re.findall("[-+=][rwx]*",new_mode)
    modes_to_int = {'r': 4, 'w': 2, "x": 1, "rw": 6, "rx": 5, "wx": 3, "rwx": 7, "": 0}
    groups_to_int = {'u': 100, 'g': 10, "o": 1, "gu": 110, "ou": 101, "go": 11, "gou": 111, "": 111}
    groups = groups_to_int["".join(sorted(set(re.findall("[ugo]*", new_mode)[0])))]
    result_mode = current_mode
    for change in mode_changes:
        symbol = change[0]
        modes = modes_to_int["".join(sorted(set(change[1:])))]
        new_mode_int = groups * modes
        if symbol == "-":
            result_mode = (((7-new_mode_int//100)&result_mode//100)*100
                           +((7-new_mode_int%100//10)&result_mode%100//10)*10
                           +((7-new_mode_int%10)&result_mode%10))
        elif symbol == "=":
            result_mode = ((new_mode_int // 100 if groups//100 == 1 else result_mode // 100) * 100
                           + (new_mode_int % 100 // 10 if groups%100//10 == 1 else result_mode % 100 // 10) * 10
                           + (new_mode_int % 10 if groups%10 == 1 else result_mode % 10))
        else:
            result_mode = ((new_mode_int // 100 | result_mode // 100) * 100
                           + (new_mode_int % 100 // 10 | result_mode % 100 // 10) * 10
                           + (new_mode_int % 10 | result_mode % 10))
    return result_mode

def abs_path(current_directory,path,root):
    steps = path.split("/")
    result_path = ""
    if steps[0] == "":
        result_path =root
    elif steps[0] == "..":
        result_path = "/".join(current_directory.split("/")[:-1]) if len(current_directory.split("/"))>1 else root
    elif steps[0] == ".":
        result_path = current_directory
    else:
        result_path = current_directory+"/"+steps[0]
    for i in range(1,len(steps)):
        if steps[i] == "..":
            result_path = "/".join(result_path.split("/")[:-1]) if len(result_path.split("/")) > 1 else root
        elif steps[i] in [".", ""]:
            continue
        else:
            result_path += "/" + steps[i]
    return result_path


class Emulator:
    def __init__(self,user_name, machine_name, tar_path):
        self.user_name = user_name
        self.machine_name = machine_name
        self.tar_path = tar_path
        self.tar = tarfile.open(tar_path,"r")
        self.root = self.tar.getnames()[0]
        self.current_directory = self.root

    def ls(self, args):
        res = "";
        paths = args.split(" ")
        if len(paths) == 1:
            for name in self.tar.getnames():
                if re.fullmatch(fr"{self.current_directory}/[^/]+",name):
                    res += f"{name[len(self.current_directory)+1:]}\n"
        elif len(paths) == 2:
            path = abs_path(self.current_directory, paths[1], self.root)
            try:
                info = self.tar.getmember(path)
                if info.isfile():
                    res+=paths[1]+"\n"
                elif info.isdir():
                    for name in self.tar.getnames():
                        if re.fullmatch(fr"{path}/[^/]+",name):
                            res+=f"{name[len(path)+1:]}\n"
            except:
                res+=f"ls: cannot access '{paths[1]}': No such file or directory"
        else:
            for path in paths[1:]:
                path_ = abs_path(self.current_directory, path, self.root)
                try:
                    info = self.tar.getmember(path_)
                except:
                    res += f"ls: cannot access '{path}': No such file or directory"
                    paths.pop(paths.index(path))
            if (len(paths) != 1):
                for i in range(1, len(paths)):
                    path = abs_path(self.current_directory, paths[i], self.root)
                    info = self.tar.getmember(path)
                    if info.isfile():
                        res+=paths[i]+"\n\n"
                    else:
                        res+=paths[i]+":\n"
                        for name in self.tar.getnames():
                            if re.fullmatch(fr"{path}/[^/]+",name):
                                res+=f"{name[len(path)+1:]}\n"
                        res+="\n"
        print(res.strip())
        return res
    def cd(self,args):
        paths = args.split(" ")
        res = ""
        if len(paths)>2:
            print("-bash: cd: too many arguments")
            res += "-bash: cd: too many arguments"

        else:
            path = abs_path(self.current_directory,paths[1],self.root)
            try:
                member = self.tar.getmember(path)
                if not (member.isdir()):
                    print(f"-bash: cd: {paths[1]}: Not a directory")
                    res+=f"-bash: cd: {paths[1]}: Not a directory"
                else:
                    self.current_directory = path
                    res+= path
            except:
                print(f"-bash: cd: {paths[1]}: No such file or directory")
                res+=f"-bash: cd: {paths[1]}: No such file or directory"
        return res

    def cat(self,args):
        paths = args.split(" ")
        res = ""
        for path in paths[1:]:
            path_ = abs_path(self.current_directory,path,self.root)
            try:
                member = self.tar.getmember(path_)
                if member.isfile():
                    res += self.tar.extractfile(member).read().decode("utf-8")+"\n"
                else:
                    res += f"cat: {path}: Is a {member.type}\n"
            except:
                res += f"cat: {path}: No such file or directory\n"
        print(res.strip())
        return res
    def chmod(self,args):
        data = args.split(" ")
        res = ""
        if len(data)<3:
            res += f"chmod: missing operand after {data[-1]}"
        else:
            mode = data[1]
            files = data[2:]
            for file in files:
                path_ = abs_path(self.current_directory, file, self.root)
                new_mode = 0
                try:
                    member = self.tar.getmember(path_)
                    if re.fullmatch(r"\d+",mode):
                        new_mode = int(mode)
                        if (new_mode>777 or new_mode<0):
                            res+= f"chmod: invalid mode: '{mode}'"
                        else:
                            res+=f"{file}'s mode: {member.mode} -> {new_mode}\n"
                            member.mode = new_mode
                    else:
                        if re.fullmatch(r"[ugo]*(?:[-+=]+[rwx]*)+", mode):
                            new_mode = char_to_int(mode,member.mode)
                            res+=f"{file}'s mode: {member.mode} -> {new_mode}\n"
                            member.mode = new_mode
                        else:
                            res+=f"chmod: invalid mode: '{mode}'\n"
                except:
                    res+=f"chmod: {file}: No such file or directory\n"
        print(res.strip())
        return res

    def close(self):
        self.tar.close()

    def execute_start_script(self, path_to_script):
        with open(path_to_script, 'r') as script:
            for command in script.readlines():
                self.run_command(command.strip())

    def run_command(self, command):
        if command.startswith("ls"):
            self.ls(command)
        elif command.startswith("cd"):
            self.cd(command)
        elif command.startswith("chmod"):
            self.chmod(command)
        elif command.startswith("cat"):
            self.cat(command)
    def emulation(self):
        command = ""
        while command!= "exit":
            command = input(f"\033[1;32;40m{self.user_name}@{self.machine_name}\033[1;37;40m:\033[1;34;40m{'/' if self.current_directory == self.root else self.current_directory[len(self.root):]}\033[1;37;40m$ ")
            self.run_command(command)

if __name__ == "__main__":
    args = sys.argv
    emulator = Emulator(args[1],args[2],args[3])
    emulator.execute_start_script(args[4])
    emulator.emulation()




