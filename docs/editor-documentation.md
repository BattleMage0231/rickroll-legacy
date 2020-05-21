# Editor Documentation

The editor is a built-in part of the rickroll language that allows the user to type code directly on the command line.

There are two modes to the editor, console and editing.

The console looks like this.

```
rickroll >
```

The editor looks like this.

```
  1 > 
```

The editor is pretty self-explanatory. You can type code and each line is marked by its index. To exit out of the editor, type 'exit' on a line. That line will not be saved.

Due to the nature of the command line, you cannot go back a line.

```
  1 > exit
```

The console has several commands that can be used to revise or delete lines, however.

## Exit

The exit command exits out of the shell.

```
rickroll > exit
```

## Edit

The edit command will change the mode to editing mode and start editing at the next line.

```
rickroll > edit
  2 > 
```

## Delete

The delete command deletes a line (1-indexed) from the code.

```
rickroll > delete 3
```

## Insert

The insert command inserts a line (1-indexed) to the code. It will prompt you for the line.

```
rickroll > insert 2
  2 > 
```

## Replace

The replace command replaces a line (1-indexed) in the code. It will prompt you for the line.

```
rickroll > replace 2
  2 > 
```

## Display

The display command displays all the code saved in the editor.

```
rickroll > display
  1 > Some code here
  2 > Some code here
  3 > Some code here
```

## New

The new command deletes everything saved in the editor and makes a new file.

```
rickroll > new
```