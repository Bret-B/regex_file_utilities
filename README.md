# regex_file_utilities
 GUI application for manipulating files and folders which match regular expressions.

![GUI demo](../assets/Regex%20file%20utilities%20GUI.png?raw=true)

# Usage and More Information

Python 3 is the only requirement.
Run app.py to start the app.

 Example usage:

![Usage demo](../assets/Regex%20file%20utilities%20demo%201.png?raw=true)

Running the program with the above input would move any files in the source folder which match the pattern to the destination folder.

All operation modes require the input pattern to fully match the the entire file/folder name.

For the rename mode, capture groups can be referenced in the output pattern using \1, \2, \3, and so on.

All regex matching is done through Python's built in re module: https://docs.python.org/3/library/re.html
