import os
import winshell
from win32com.client import Dispatch

try:
    startup_path = winshell.startup()
    shortcut_path = os.path.join(startup_path, "ICUTelegramBot.lnk")
    
    # Path to the VBScript and its target
    vbs_path = r"d:\icu telegram bot\last version\coding\run_bot.vbs"
    working_dir = r"d:\icu telegram bot\last version\coding"
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = "wscript.exe"
    # Properly quote the argument for the VBS file
    shortcut.Arguments = f'"{vbs_path}"'
    shortcut.WorkingDirectory = working_dir
    shortcut.Save()
    print(f"Successfully created shortcut at {shortcut_path}")
except Exception as e:
    print(f"Error creating shortcut: {e}")
