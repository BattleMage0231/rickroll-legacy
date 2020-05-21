# Editor Documentation

The editor is a built-in part of the rickroll language that allows the user to type code directly on the command line.

There are two modes to the editor, console and editing.

The console looks like this.

<span style="color:lime">rickroll > </span>

The editor looks like this.

<span style="color:yellow">  1 > </span>

The editor is pretty self-explanatory. You can type code and each line is marked by its index. To exit out of the editor, type 'exit' on a line. That line will not be saved.

Due to the nature of the command line, you cannot go back a line.

<span style="color:yellow">  1 > </span> exit

The console has several commands that can be used to revise or delete lines, however.

## Exit

The exit command exits out of the shell.

<span style="color:lime">rickroll > </span> exit

## Edit

The edit command will change the mode to editing mode and start editing at the next line.

<span style="color:lime">rickroll > </span> edit

<span style="color:yellow">  2 > </span> 

## Delete

The delete command deletes a line (1-indexed) from the code.

<span style="color:lime">rickroll > </span> delete 3

## Insert

The insert command inserts a line (1-indexed) to the code. It will prompt you for the line.

<span style="color:lime">rickroll > </span> insert 2

<span style="color:yellow">  2 > </span> Some code here

## Replace

The replace command replaces a line (1-indexed) in the code. It will prompt you for the line.

<span style="color:lime">rickroll > </span> replace 2

<span style="color:yellow">  2 > </span> Some code here

## Display

The display command displays all the code saved in the editor.

<span style="color:lime">rickroll > </span> display

<span style="color:yellow">  1 > </span> Some code here

<span style="color:yellow">  2 > </span> Some code here

<span style="color:yellow">  3 > </span> Some code here

## New

The new command deletes everything saved in the editor and makes a new file.

<span style="color:lime">rickroll > </span> new