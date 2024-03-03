# ------PROJECT OUTLINE------
# Tree-based system of directories and files, accessed via a terminal-based command-line interface
# Tree object contains File and Folder objects
# File and Folder classes are children of Node class
# ----CLI----
# > [command argument] [name argument(s)] [location argument(s)] [augment argument] [content argument(s)] 

import os
import re
import copy

class Node:
    def __init__(self, name, context) -> None:
        self.name = name
        self.type = 'node'
        self.context = context

    def __str__(self):
        return self.name

    def populate(self, name, type, content = '', location = '') -> None:
        if type == 'file':
            self.branches.append(File(name, self, content))
            print(f"New file {name} created within {self.name}.")
        elif type == 'folder':
            self.branches.append(Folder(name, self))
            print(f"New folder {name} created within {self.name}.")
        elif type == 'shortcut':  
            if not location:
                location = self
            self.branches.append(Shortcut(name, self, location))
            print(f"New shortcut {name} created within {self.name}.")
        else:
            print(f"{type} is not a recognized node type.")

    def get_address(self, string = False):
        '''
        Returns address of current object as a list, beginning with 
        name of root object and followed by names of progressively 
        smaller contexts, terminating with name of current object.
        '''
        context_list = [self.name]
        curr_context = self.context
        # loops until counters empty context
        while curr_context:
            # appends name of context to context_list
            context_list.append(curr_context.name)
            # moves up one level of context
            curr_context = curr_context.context
        address = context_list[::-1]

        # allow obtaining address as string
        if string:
            return ':'.join(address)
        return address

class Folder(Node):
    def __init__(self, name, context) -> None:
        Node.__init__(self, name, context)
        self.branches = []
        self.type = 'folder'
    
    def get_name_matches(self, name_list) -> list:
        # return list of references to objects in folder whose names are in name_list
        matches = []
        match_count = 0

        for name in name_list:
            for object in self.branches:
                if object.name == name:
                    matches.append(object)
                    match_count += 1
                    break

        match_names = [obj.name for obj in matches]
        absent_names = [name for name in name_list if name not in match_names]
        return matches, absent_names

    def get_branches(self) -> list:
        return self.branches

class File(Node):
    def __init__(self, name, context, content) -> None:
        Node.__init__(self, name, context)
        self.type = 'file'
        self.content = content

    def get_content(self) -> list:
        return self.content

class Shortcut(Folder):
    # A shortcut is a type of folder with a single location as its content
    # When a shortcut is made the working directory i.e: filesystem = Shortcut()
    # the program automatically makes the content reference contained within it the working directory
    # modified functions implementation -> change all movement functions
    def __init__(self, name, context, location) -> None:
        Folder.__init__(self, name, context)
        self.branches = [location]
        self.type = 'shortcut'

def load_filesystem(filename = 'default_filesystem.txt'):
    # load_filesystem is called automatically when script is run as main
    global command_history
    global root_object
    global filesystem

    # initialise filesystem if filesystem is empty
    if not filesystem:
        filesystem = copy.copy(root_object)

    # attempts to read from default_filesystem.txt
    try:
        with open(filename, 'r', encoding = 'utf-8') as file:
            pass

    # If this fails, performs no action
    except FileNotFoundError:
        print('Err: default file not found.')

    # if successful, populates filesystem_tree
    else:
        print(f"Loading filesystem from {filename}...")
        with open(filename, 'r', encoding = 'utf-8') as file:
            while True:
                file_line = file.readline()
                if file_line == 'end':
                    break
                file_line_san = command_sanitizer(file_line)
                if file_line_san:
                    command_parser(file_line_san)
            print("Filesystem loaded.")
                
def clear_filesystem(augment):
    global root_object
    global filesystem
    # skip user validation if augment passed
    user_check = (augment == 'certain')
    while not user_check:
        user_command = input("Calling this function will copy the default root object to the filesystem. Anything not saved will be lost. Are you sure? (Y/N) > ")
        if user_command.upper() == "Y":
            user_check = True
        break
    if user_check:
        filesystem = copy.copy(root_object)

def save_filesystem(filename = "q"):
    # user can either save the current filesystem under a specific name
    # or user can tell the program to make a quicksave
    # if no argument is passed, then file is a quicksave
    if filename == 'q':
        filename = "qsave.txt"
    else:
        # if user input is used, sanitise input
        filename = filename_sanitizer(filename)
        # ask user if they want to overwrite existing file
        if os.path.exists(filename):
            print("File with the same name already exists. Overwrite? (Y/N) > ")
            while user_command.upper() != "Y" or "N":
                print("Invalid command.")
                user_command = input("> ")
            if user_command.upper() == "N":
                print("Save command has been cancelled.")
                filename = ''
            else:
                print(f"Current filesystem has been saved as {filename}.")
    if filename:
        # assemble file string with copy of global command history
        cmd_hist_copy = command_history.copy()
        cmd_hist_copy.append('end')
        hist_to_write = '\n'.join(cmd_hist_copy)
        with open(filename, 'w', encoding = 'utf-8') as file:
            file.write(hist_to_write)
        
def filename_sanitizer(name):
    valid_non_alnum_chars = ["-","_"]
    # checks that input string only contains valid characters, is of valid length, and if the filename already exists
    # returns valid filename, or empty string if filename is invalid
    if len(name) <= 1:
        print("Err: input filename is too short.")
        return ""
    if filename[-1:-5] != '.txt':
        filename += '.txt'
    if not name.isalnum():
        # generate name string with all invalid characters removed
        name = [char for char in name if char.isalnum() or char in valid_non_alnum_chars]
    


def move_in(name_list, augment = ''):
    global filesystem
    global command_history
    for name in name_list:
        # iterate through objects stored in current context
        for i, obj in enumerate(filesystem.get_branches()):
            # if name and type are valid, write new value for filesystem
            if name == obj.name and obj.type != 'file':
                filesystem = filesystem.branches[i]
                if augment != 'norec':
                    command_history.append(f"in @{name}")
                break
        else:
            print("Err: object not found.")

def move_out(augment = ''):
    global filesystem
    global command_history
    # If current object has context, get context
    # make the current object's context the current object
    if not filesystem.context:
        print("Err: no valid context found.")
    else:
        filesystem = filesystem.context
        if augment != 'norec':
            command_history.append(f"out")

def change_directory(target_address_list_raw):
    global command_history
    global filesystem
    for target_address_raw in target_address_list_raw:
        # convert str target_address to list
        target_address = target_address_raw.split(':')
        curr_address = filesystem.get_address()
        # print(f"target address: {target_address}")
        # print(f"current address: {curr_address}")
        # compare current and target address
        # -does the maximum term of target address exist within current address?
        # If yes, then iteratively move out of context until current object = maximum term
        # Then follow target address in until arriving at the final term and the target object
        # If that doesn't work, then take the length of the target address as L
        # move out of context (L - 1) times
        # check if maximum term of target list exists within current context
        # If yes, then follow target address down until final term and target object
        # If not, then print error message

        target_add_max = target_address[0]
        # print(f"target max address: {target_add_max}")
        target_max_loc = curr_address.count(target_add_max)
        # print(f"target max location: {target_max_loc}")
        if target_max_loc:       
            steps_to_target_max = len(curr_address) - target_max_loc
            for i in range(steps_to_target_max):
                move_out(augment = 'norec')
            target_address = target_address[1:]
            move_in(target_address)
        else:
            target_add_len = len(target_address)
            for i in range(1, target_add_len):
                move_out(augment = 'norec')
            branch_names = [obj.name for obj in filesystem.get_branches()]
            if target_add_max in branch_names:
                move_in(target_address, augment = 'norec')
                command_history.append(f"cd @{target_address_raw}")
            else:
                change_directory([':'.join(curr_address)])
                print("Err: unable to find target directory.")

def create_file(name_list, content_list = []):
    global filesystem
    global command_history
    # protect against IndexErrors caused by accessing content_list
    len_diff = len(name_list) - len(content_list)
    for i in range(len_diff):
        content_list.append('')

    branch_names = [obj.name for obj in filesystem.get_branches()]
    for i, name in enumerate(name_list):
        # get content associated with name
        content = content_list[i]

        # mutate name if object in context already possesses name
        while name in branch_names:
            name += '_o'

        filesystem.populate(name, 'file', content)
        command_history.append(f"file ~{name} #{content}")
            
def create_folder(name_list):
    global filesystem
    global command_history
    
    # produce list of objects in current context
    branch_names = [obj.name for obj in filesystem.get_branches()]
    
    for name in name_list:
        # mutate name if object in context already possesses name
        while name in branch_names:
            name += '_o'

        filesystem.populate(name, 'folder')
        command_history.append(f"folder ~{name}")

def create_shortcut(name_list, address_list):
    global filesystem
    global command_history
    
    len_name = len(name_list)
    len_add = len(address_list)
    # if list arguments differ in length, truncate any arguments that lack a camplement
    if len_name > len_add:
        name_list = name_list[0:len_add]
    elif len_name < len_add:
        address_list = address_list[0:len_name]

    # produce list of objects in current context
    branch_names = [obj.name for obj in filesystem.get_branches()]
    for i, name in enumerate(name_list):
        address = address_list[i]
        # get reference to object with address argument
        address_obj = validate_address(address)
        # skip shortcut creation if address argument is not valid
        if not address_obj:
            continue
        # mutate name if object in context already possesses name
        while name in branch_names:
            name += '_s'

        filesystem.populate(name, 'shortcut', location = address_obj)
        command_history.append(f"shortcut ~{name} @{address}")
    
def validate_address(address):
    global filesystem
    # record current address
    home_address = filesystem.get_address(True)
    # navigate to address
    change_directory([address])
    target_address = filesystem.get_address(True)
    # if target_address = address argument, then the argument is valid
    if target_address == address:
        # return reference to object at target address
        address_obj = filesystem
        change_directory([home_address])
        return address_obj
    return None

def shortcut_entry_check():
    global filesystem
    # if current directory is a shortcut, change directory to shortcut stored address
    type = filesystem.type
    name = filesystem.name
    if type == 'shortcut':
        # access shortcut address
        address = filesystem.branches[0].get_address(True)
        change_directory([address])
        print(f"Taken shortcut {name} to address {address}.")

def exit():
    # returns True if exit successful, otherwise returns False
    while True:
        user_command = input("Save filesystem before exit? (Y/N) > ")
        if user_command.upper() == "N":
            print("Terminating program. Thank you for using the file system.")
            return True
        elif user_command.upper() == "Y":
            user_command = input("Enter name for filesystem to be saved under, or enter 'q' for a quicksave. > ")
            save_filesystem(user_command)
            return True

def command_sanitizer(command):
    # takes a string entered by the user
    # weak: augments the entered string such that it meets the program requirements
    # strong: rejects any invalid entered strings, otherwise returns entered string
    command_reject = '' # truth value of 0

    # valid string:
    # must have > 0 length -> S
    if len(command) < 1:
        return command_reject
    
    # maximum of 1 of each tag character, unless preceded by escape character
    tag_list = re.findall("[^%][~@#!]", command)
    if tag_list:
        # remove non-tag characters
        tag_list = [tag[1] for tag in tag_list]
        tag_set = set(())
        # sets in python cannot contain duplicate values
        [tag_set.add(tag) for tag in tag_list]
        if len(tag_list) != len(tag_set):
            return command_reject
    
    # no whitespaces at beginning or end -> W
    command = command.strip()
    
    # must only contain alnums, valid special characters and valid tag characters -> W
    # this rule may be broken if the preceding character is the escape character %
    # command = re.sub(f"[^%][^-_%@#!:|~ \w]", "", command)
    
    # only alnums and valid special characters can adjacent-repeat - no tags or whitespaces -> W
    # identify any occurence of two or more adjacent invalid characters
    # in each occurence, remove all characters except the first
    adj_exceptions = re.findall(f".[:@#~!|][:@#~!| ]+", command)
    for excp in adj_exceptions:
        # only perform removal if no escape character present
        if excp[0] != '%':
            command = re.sub(f"{excp}", f"{excp[1]}", command)

    # tags must occur after a whitespace or escape character -> W
    # identify occurences of non-whitespace before tag
    # replace occurence with original tag
    adj_exceptions = re.findall(f"[^ %][@#~!]", command)
    for excp in adj_exceptions:
        excp_corrected = excp[0] + ' ' + excp[1:]
        command = re.sub(f"{excp}", f"{excp_corrected}", command)

    return command

def extract_arg(tag, command) -> list:
    # find string enclosed by tag and whitespace/semicolon
    # does not include tags preceded by escape characters
    temp = re.findall(f"[^%]{tag}[^~@!#]+[ ;]", command)
    # only proceed if temp is not empty and argument has been found
    if not temp:
        return []
    temp = temp[0]
    l = len(temp) - 1
    # remove enclosing chars
    temp = temp[2:l]
    # plurality - get argument list
    out = temp.split('|')
    return out

def command_parser(user_command):
    # Early escape if string is invalid
    if user_command == '':
        return None
    
    # splits user_command into 1-5 strings and/or lists, which are used to define arguments
    # to support argument plurality, each argument (except command and augment) is a list with a default length of 1
    # initialise args with empty strings/lists
    args = {
        'name' : [],
        'location' : [],
        'augment' : '',
        'content' : []
    }
    # command argument has no tag so it gets identified early
    command_pair = user_command.split(" ", 1)
    args['command'] = command_pair.pop(0)

    # get user_command as string and its argument tags as a list
    if command_pair:
        user_command = command_pair[0]
        # bracket user_command with whitespace and semicolon to indicate argument limits
        user_command = ' ' + user_command + ';'
        user_command_tags = re.findall("[~@!#]", user_command)
        # search for matching tag
        # use tag to extract argument
        # remove tag and terminating character from argument
        # plurality: pass argument as list to variables
        # pass empty strings/lists if no argument is extracted
        args['name'] = extract_arg('~', user_command)
        args['location'] = extract_arg('@', user_command)
        # only 1 augment tag can be passed in each command
        temp = extract_arg('!', user_command)
        args['augment'] = temp[0] if temp else ''
        args['content'] = extract_arg('#', user_command)
    
        # get user_command without content argument but with content tag
        # " ~a @b !c #"
        if user_command.count('#'):
            user_command = user_command.split('#')[0]
            user_command += '#'
        # in this range, number of spaces = number of arguments is the correct equivalence
        spaces_count = user_command.count(' ')
        tags_count = len(user_command_tags)
        # sanitation eliminates the possibility of tag duplicates: so a non-zero equivalence indicates arguments have not been tagged.
        if tags_count - spaces_count != 0:
            print("Err: argument in input has not been prefixed with a tag.")
    
    function_hash = {
        'in' : lambda args: move_in(args['location']),
        'out' : lambda args: move_out(),
        'cd' : lambda args: change_directory(args['location']),

        'file' : lambda args: create_file(args['name'], args['content']),
        'folder' : lambda args: create_folder(args['name']),
        'shortcut' : lambda args: create_shortcut(args['name'], args['location']),
        'delete' : lambda args: delete_objects(args['name'], args['augment']),

        'read' : lambda args: read_files(args['name']),
        'write' : lambda args: write_files(args['name'], args['augment'], args['content']),
        'rename' : lambda args: rename_objects(args['name'], args['content']),
        'copy' : lambda args: copy_objects(args['name']),
        'paste' : lambda : paste_objects(),

        'list' : lambda args: list_context(),
        'props' : lambda args: object_properties(args['name']),
        'search' : lambda args: search_filesystem_wrapper(args['name']),

        'save' : lambda args: save_filesystem(args['name']),
        'load' : lambda args: load_filesystem(args['name']),
        'help' : lambda args: help(args['location'])
    }

    func_hash_keys = [key for key in function_hash.keys()]
    # check if command argument is contained in key list
    if args['command'] in func_hash_keys:
        # access lambda function associated with key
        # pass hash of arguments as argument to lambda function
        function_hash[args['command']](args)
        # check for entry into a shortcut
        if args['command'] in ['in', 'cd']:
            shortcut_entry_check()
    else:
        print("Err: command argument not recognised.")

def read_files(name_list):
    global filesystem
    match_list, absent_names = filesystem.get_name_matches(name_list)
    # iterate through objects stored in current context
    for obj in match_list:
        if obj.type == 'file':
            #print file content
            print(f"File name: {obj.name}")
            print("-" * 10)
            print(obj.get_content())
            print("-" * 10)
    if absent_names:
        print(f"Err: files {', '.join(absent_names)} not found.")
    

def write_files(name_list, augment = 'write', content_list = []):
    global filesystem
    global command_history
    # protect against IndexErrors caused by accessing content_list
    len_diff = len(name_list) - len(content_list)
    for i in range(len_diff):
        content_list.append('')
    # create hash for accessing content values
    content_hash = {}
    for i, name in enumerate(name_list):
        content_hash[name] = content_list[i]

    match_list, absent_names = filesystem.get_name_matches(name_list)
    for obj in match_list:
        # get content at matching index
        content = content_hash[obj.name]
        # iterate through objects in current context
        if obj.type == 'file':
            # checks for augment. passes write as default.
            if augment == 'write':
                obj.content = content
            elif augment == 'append':
                obj.content += content
                command_history.append(f"write ~{obj.name} !append #{content}")
            command_history.append(f"write ~{obj.name} !write #{content}")

    if absent_names:
        print(f"Err: files {', '.join(absent_names)} not found.")
        
                           
def copy_objects(name_list):
    global object_clipboard
    object_clipboard = []
    match_list, absent_names = filesystem.get_name_matches(name_list)

    for obj in match_list:
        object_clipboard.append(obj)
        print(f"{obj.type} {obj.name} copied to clipboard.")
        command_history.append(f"copy ~{obj.name}")

    if absent_names:
        print(f"Err: objects {', '.join(absent_names)} not found.")


def paste_objects():
    global object_clipboard
    global filesystem
    # proceed if clipboard is not empty
    if object_clipboard:
        branches = [branch.name for branch in filesystem.get_branches()]
        for obj in object_clipboard:
            # if object name is already taken at destination, mutate name
            name_buffer = obj.name
            context_buffer = obj.context
            while obj.name in branches:
                obj.name += "_c"
            # set object context to current filesystem
            obj.context = filesystem
            # clone object in clipboard and append clone to filesystem
            filesystem.branches.append(copy.deepcopy(obj))
            # restore name and context of original object
            if name_buffer:
                obj.name = name_buffer
            obj.context = context_buffer
            print(f"{obj.type} {obj.name} pasted to {filesystem.name}.")
            command_history.append(f"paste")
    else:
        print("Err: clipboard is empty.")

def list_context():
    global filesystem
    branches = filesystem.get_branches()
    s_plural = 's' * (len(branches) != 1)
    colon = ':' * (len(branches) != 0) or '.'
    print(f"{filesystem.type} {filesystem.name} contains {len(branches)} object{s_plural}{colon}")
    for obj in branches:
        print(f" > {obj.type} {obj.name}")

def object_properties(name_list = []):
    global filesystem
    match_list, absent_names = filesystem.get_name_matches(name_list)
    # if no name argument passed, return properties of current filesystem object
    if not name_list:
        object_properties_print(filesystem)
    else:
        for obj in match_list:
            object_properties_print(obj)

        if absent_names:
            print(f"Err: objects {', '.join(absent_names)} not found.")


def object_properties_print(obj):
    print(f"Properties:")
    print("-" * 10)
    print(f"Name: {obj.name}")
    print(f"Type: {obj.type}")
    print(f"Context: {obj.context}")
    print(f"Address: {obj.get_address(True)}")
    if obj.type == 'file':
        print(f"Content size: {len(obj.content)} characters.")
    elif obj.type == 'folder':
        print(f"Number of branches: {len(obj.get_branches())}")
    elif obj.type == 'shortcut':
        print(f"Location reference: {obj.branches[0].get_address(True)}")
    print("-" * 10)

def delete_objects(name_list = [], augment = ''):
    global filesystem
    match_list, absent_names = filesystem.get_name_matches(name_list)
    if not name_list:
        # skip user validation if augment passed
        user_check = (augment == 'certain')
        while not user_check:
            user_command = input("Calling delete without specifying a name argument will delete the current context. Do you want to continue? (Y/N) > ")
            if user_command.upper() == "Y":
                user_check = True
            break
        # requires user consent and for filesystem to not be root folder
        if user_check and filesystem.context:
            loc_temp = [filesystem.name]
            move_out()
            delete_objects(loc_temp)
            command_history.append(f"delete !certain")
    else:
        for obj in match_list:
            # pass object reference to remove method to delete from filesystem
            filesystem.branches.remove(obj)
            print(f"{obj.type} {obj.name} deleted from {filesystem.type} {filesystem.name}.")
            command_history.append(f"delete ~{obj.name} !certain")

        if absent_names:
            print(f"Err: objects {', '.join(absent_names)} not found.")

    pass

def search_filesystem_wrapper(name_list):
    global filesystem
    # wrapper manages name plurality
    # calls search_filesystem function for each name in list
    print("Search results:")
    for name in name_list:
        search_results = search_filesystem(filesystem, name)
        if search_results:
            print("-" * 10)
            for result in search_results:
                print(f"Name: {result.name}")
                print(f"Address: {result.get_address(True)}")
                print("-" * 10)
        else:
            print(f"Err: no matches found for \"{name}\" within {filesystem.name}.")

def search_filesystem(search_obj, name, recursive = False):
    search_results = []
    # get objects contained in current search object
    context_contents = search_obj.get_branches()
    for obj in context_contents:
        # look for name content matches if no exact matches found
        # add matches to search results
        if obj.name == name or obj.name in name:
            search_results.append(obj)
        
        if obj.type == 'folder':
            # search contents of obj
            results = search_filesystem(obj, name, True)
            search_results.extend(results)
    return search_results

def help(name_list):
    if not name_list:
        print("--HELP--")
        print("Enter one of the following keywords to access a specific resource.")
        print("After entering a .")
        print("intro : introduction to the filesystem.")
        print("about : description of the filesystem.")
        print("cli : explanation of the command line interface.")
        print("glossary : descriptions of command arguments and their functions.")
        print("augments : descriptions of augment arguments and their effects.")
        user_command = input("> ")
        help_text(user_command)
    else:
        for name in name_list:
            help_text(name)
    pass

def help_text(name): 
    func_hash = {
        "out" : "out - \t\t\tmove out of current context.",
        "in" : "in (name) - \t\tmove into context with specified name.",
        "file" : "file (name|) (content|) - create new object in context populated with content.",
        "folder" : " folder(type) (name|) - create new object of class type in context with specified name.",
        "exit" : "exit (augment) - \tbegin exit dialogue, exit immediately if !certain augment passed.",
        "load" : "load (name) - \t\tloads filesystem stored in file with specified name.",
        "save" : "save (name) - \t\tsaves filesystem in new file with specified name.",  
        "read" : "read (name|) (augment) - prints content of named file to terminal.",
        "write" : "write (name|) (augment) (content|) - writes passed content to named file at named location.",
        "copy" : "copy (name|) - \t\tcopies named object(s) to variable. ",
        "paste" : "paste (location) (augment) - pastes copied object(s) to named location. object names are preserved but appended with a copy tag.",
        "list" : '''list (name) (location) (augment) - prints list of objects in the context of the given location.
                    name argument is used to pass object types like 'files', 'folders', or 'all'.''',
        "props" : "props (name|) (augment) - prints properties of named object, such as location, size, and names of contained objects.",
        "delete" : "delete (name|) (location) (augment) - destroys named objects.",
        "search" : '''search (name) (location) (augment) - searches for named object within context of given location. Returns names and locations of any matches.
                      search uses current location if no location argument is passed.''',
    }
    aug_hash = {
        "certain" : "!certain - skips any validation dialogue otherwise required by a command. Used by delete and exit.",
        "append" : "!append - appends content argument to end of existing data in file. Used by write.",
        "write" : "!write - replaces any existing data in file with content argument. Used by write",
    }
    function_list = [func for func in func_hash.keys()]
    augment_list = [aug for aug in aug_hash.keys()]

    if name == 'intro':
        text_intro = '''
filesystem.py is a program that simulates the behaviours of a text-based computer filesystem. 
The program allows you to navigate a hierarchy of object nodes, read the states of specific nodes and modify node states as you see fit.
To give a command to the program, enter a command name followed by arguments separated with whitespaces and prefixed with appropriate tags.
'''
        print(text_intro)
    elif name == 'about':
        text_about = '''
The filesystem consists of a tree of objects, where each object contains references to the objects it contains and the object containing it.
The current state of the filesystem is defined by a global variable, which is accessed and modified when relevant commands are entered by the user.
Each command that alters the filesystem is stored in a list. When a save command is entered, the program commits this data to an external file.
When a load command is entered, such as during initialisation, the data is read from a file and executed as a sequence of commands, thereby rebuilding the filesystem.
'''
        print(text_about)

    elif name == 'cli':
        text_cli = '''
General form of command line arguments:
    
    (cmd) ~(name) @(location) !(augment) #(content)

    Examples: cd @root:after:seven
              file ~tri #There are three sides to a triangle
              read ~yellow|file14|purple
              write ~data2|data4 #text string B|text string D

    cmd: \tkeyword that identifies which function to perform. Cannot be plural.
    name: \tprefixed with ~, used to either define a new name or identify an existing name.
    location: \tprefixed with @, defines location within filesystem to move to or act upon.
    augment: \tprefixed with !, optional argument that alters the behavior of some functions. Cannot be plural.
    content: \tprefixed with #, defines data to be stored within a filesystem object.

    Only the arguments required by the desired function need to be included in each command.
    The command argument must be the first argument, and the content argument must be the last argument.
    Some functions can accept arguments which are a tuple of sub-arguments, where each argument is separated by a |.
'''
        print(text_cli)

    elif name == 'glossary':
        print("Suffix of | indicates argument can be of plural form.")
        for f_name in function_list:
            print(func_hash[f_name])

    elif name in function_list:
        print(func_hash[name])

    elif name == 'augments':
        for a_name in augment_list:
            print(aug_hash[a_name])

    elif name in augment_list:
        print(aug_hash[name])

    else:
        print("Err: keyword not recognised.")

def rename_objects(name_list, content_list = []):
    # finds objects with names in name_list
    # changes their names to corresponsing names in content_list
    global filesystem
    global command_history
    # protect against assigning an empty string as an object name
    len_content = len(content_list)
    name_list = name_list[0:len_content]
    # combine name and content lists into hash
    name_hash = {}
    for i, name in enumerate(name_list):
        name_hash[name] = content_list[i]

    # get list of objects to rename
    match_list, absent_names = filesystem.get_name_matches(name_list)
    branches = filesystem.get_branches()

    for obj in match_list:
        # use object's name to get value from name_hash
        old_name = obj.name
        new_name = name_hash[old_name]
        
        # mutate new_name if object in context already possesses name
        branch_names = [b_obj.name for b_obj in branches]
        while new_name in branch_names:
            new_name += '_r'
        
        obj.name = new_name
        print(f"{obj.type} {old_name} renamed to {obj.name}.")
        command_history.append(f"rename ~{old_name} #{new_name}")


# -- GLOBAL VARIABLES AND OBJECTS
# filesystem variable is initialised with root folder
# functions as a global variable providing handle on current directory
if __name__ == '__main__':
    filesystem = None
    root_object = Folder('root', '')
    command_history = []
    object_clipboard = []
    load_filesystem()
    print("Welcome to the file system. Please enter a valid command, enter 'help' for a description of valid commands, or 'exit' to leave the program.")
    while True:
        # generate input line using address of filesystem
        user_command_raw = input(f"{filesystem.get_address(True)}> ")
        
        if not user_command_raw:
            print("Err: cannot pass an empty string as argument.")

        user_command = command_sanitizer(user_command_raw)
        if not user_command:
            print("Err: command syntax is invalid.")
            continue

        # exit() outside command_parser to break out of main loop
        if user_command[:4] == "exit" and exit():
            break

        command_parser(user_command)

        