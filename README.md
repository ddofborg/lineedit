LineEdit
========

LineEdit is a line based editor which can be used to automate tasks.
Particularly useful for auto editing config files.


Command line help
-----------------

     usage: lineedit.py [-h] [-f {starts,regex,exact,ends}] [-n]
                       [-p {replace,above,below,end,begin,comment,delete}]
                       [-m MAX] [-y] [-v] [-l] [--create]
                       file sourceline [destline]

    LineEdit: A tool to quickly automate config file editing.

    positional arguments:
      file                  Source file: file path which should be edited (should
                            be a textfile).
      sourceline            Source line: line to search for using one of the
                            method described in -f option.
      destline              Destination line: the line which will be added or will
                            replace source line using methods described in -p
                            options. If `-p comment` is used, this string will be
                            the comment characher. (default: None)

    optional arguments:
      -h, --help            show this help message and exit
      -f {starts,regex,exact,ends}
                            Find source position using one of the methods.
                            (default: exact)
      -n                    Add the source line to the file, if the source line is
                            not found. Use with `-p end` or `-p begin`. (default:
                            False)
      -p {replace,above,below,end,begin,comment,delete}
                            Destination position: At which position should the
                            destination line be added/replaces. (default: replace)
      -m MAX, --max MAX     Maximum number of matches. If more matches are found,
                            no changes will take place. (default: 1)
      -y                    Yes, make changes to the file. Otherwise only show
                            line numbers which will be changes. (default: False)
      -v                    Output more debug information. (default: False)
      -l, --long-diff       Show whole file with changes, not useful if the source
                            file is long. (default: False)
      --create              Create the output file if source file does not exists.
                            Useful if you want to append something to a (new)
                            file. (default: False)

    Exit codes are as follows: -1 = There was an error. 0 = There was a match and
    it was replaces. 1 = No match was found. Nothing is replaced.


Examples
--------

    # Change port of some service from 3000 to 5000
    $ ./lineedit.py example/ex1.txt "port=3000" "port=5000"


    # Add "alias l='ls -la'" to the end of a file if the line is not yet there.
    # File will not be created if it doesn't exists.
    $ ./lineedit.py example/ex2.txt "alias l='ls -la'" "alias l='ls -la'" -n -p end


    # Comment out bind-option in a config file.
    $ ./lineedit.py example/ex3.txt "bind" "# " -f starts -p comment


    # Remove s line starting with "alias l=" using a regex match.
    $ ./lineedit.py example/ex2.txt "^alias l=" -p delete -f regex


    # Allow PostgreSQL to listen to 0.0.0.0/0 for all users.
    $ ./lineedit.py example/ex4.txt "host all all 127.0.0.1/32 md5" "host all all 0.0.0.0/0    trust" -f regex



Features
--------

* Update unicode files.

* Show the diff with to be made changes.

* Create file if needed to append to a new or existing file.

* Auto-detect line endings.

* Option to add a line if a line in not found to prevent multiple addition.

* Make changs only if one 1 setting is found. In case there are more than one
  match in the source file.

