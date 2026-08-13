' Double-click this file to start Tick-IT without showing a Command Prompt window.
Option Explicit

Dim shell, projectFolder, appScript
Set shell = CreateObject("WScript.Shell")

projectFolder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
appScript = projectFolder & "\Tick-IT.pyw"

' pyw.exe is Python's windowless launcher.  The final two arguments hide the
' launcher itself and let this script return immediately.
shell.Run "pyw.exe -3 " & Chr(34) & appScript & Chr(34), 0, False
