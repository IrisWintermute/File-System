filesystem.py is a python script that when run, creates a sandboxed file system that can be read from and manipulated via the command line.
After installing the project, run filesystem.py from your terminal to open the program.
The program will attempt to load a filesystem from default_filesystem.txt in the local directory. 
If the file cannot be found, then no filesystem will be loaded.

The file system consists of a collection of mutable objects arranged in a tree hierarchy. 
The tree of objects can be read from, written to, and edited with instructions passed through command line arguments.
> {command argument} ~{name argument(s)} @{location argument(s)} !{augment argument} #{content argument(s)}
Above is the standard syntax for passing arguments to the file system.
Each command makes use of specific argument types, so make sure to check a command's definition in > help if you aren't sure what arguments are taken.
Except for the command argument, each argument type must be prefixed with the appropriate tag character for the argument to be recognised.
--> ~ for name, @ for location, ! for augment, # for content
The command argument must always be the first argument in the series, and (if being passed) the content argument must always be the last.
For some commands, it is possible to pass multiple name, location, and/or content arguments. In these situations, every separate argument of the same type must be separated by a | symbol.
--> > file ~two|three|four #zebra|lion|giraffe will create three files, each populated with their own text data.
