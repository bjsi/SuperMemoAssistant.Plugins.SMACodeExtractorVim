import urllib, urllib.request
import json
import sqlite3
from sqlite3 import Error
import os

try:
  import vim
except:
  print("No vim module available outside vim")
  pass


# Extracts will be saved here:
db_fp = "/mnt/c/Users/james/Desktop/vim_extracts.db"

# Recognized languages dictionary
langs = {
        ".py": "python",
        ".cpp": "c++",
        ".c": "c",
        ".hs": "haskell"
        }


def _get_conn():
    """
    Get a connection to the database.
    """
    conn = None
    try:
       conn = sqlite3.connect(db_fp)
    except Error as e:
        print(e)
    return conn


def _get_fullpath() -> str:
    """
    Get the fullpath of the current vim session.
    """
    return vim.eval("expand('%:p')")


def _get_priority() -> float:
    """
    Get the priority input from the user.
    """

    vim.eval("inputsave()")
    p = vim.eval("input('Enter priority (0-100%): ')")
    vim.eval("inputrestore()")

    try:
        priority = float(p)
    except ValueError:
        print("Priority must be a float between 0 and 100")
        return -1

    if priority < 0 or priority > 100:
        priority = -1

    return priority


def _get_confirmation() -> bool:
    """
    Get confirmation from the user to save the extract.
    """
    res = vim.eval("confirm('Confirm Extract?', '&extract\n&cancel')")
    if res == "1":
        return True
    return False


def _get_selected() -> str:
    """
    Get the currently selected (visual mode) text in vim.
    """
    line_start, col_start = vim.eval("getpos(\"'<\")[1:2]")
    line_end, col_end = vim.eval("getpos(\"'>\")[1:2]")
    lines = vim.eval(f'getline({line_start}, {line_end})')
    if len(lines) == 0:
        return ''
    lines[0] = lines[0][int(col_start) - 1:]
    lines[-1] = lines[-1][: int(col_end) - 2]
    return "\n".join(lines)


def _create_table(conn):
    """
    Create the database table.
    """
    cur = conn.cursor()
    sql = """CREATE TABLE IF NOT EXISTS Extract
    (Id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    timestamp integer NOT NULL DEFAULT CURRENT_TIMESTAMP,
    selectedCode text NOT NULL,
    comment text NOT NULL,
    priority float NOT NULL,
    exported boolean NOT NULL DEFAULT 0,
    file text NOT NULL,
    language text NOT NULL,
    project text NOT NULL)"""
    cur.execute(sql)
    conn.commit()
    cur.close()


def _get_comment():
    """
    Get comment input from the user.
    """
    vim.eval("inputsave()")
    comment = vim.eval("input('Enter comment (optional): ')")
    vim.eval("inputrestore()")
    return comment


def _insert(sel_text, comment, priority, file, language, project):
    """
    Insert the extract into the database
    """
    conn = _get_conn()
    _create_table(conn)
    sql = """
    INSERT INTO extract(selectedCode, comment, priority, file, language, project)
    VALUES(?, ?, ?, ?, ?, ?)
    """
    cur = conn.cursor()
    cur.execute(sql, (sel_text, comment, priority, file, language, project))
    conn.commit()
    cur.close()
    conn.close()
    return cur.lastrowid


def create_extract():
    """
    Main function
    """
    file = _get_fullpath()
    sel_text = _get_selected()
    if not sel_text:
        return
    print(f"```\n{sel_text}\n```")
    priority = _get_priority()
    if priority == -1:
        print("Cancelled Extract.")
        return
    comment = _get_comment()
    # TODO
    project = "Unknown"
    file_ext = os.path.splitext(file)[1]
    lang = langs.get(file_ext)
    if not lang:
        print(f"Language for extension {file_ext} is unknown.")
    if _get_confirmation():
        if _insert(sel_text, comment, priority, file, lang, project):
            print("Extract Succeeded.")
        else:
            print("Extract Failed.")
    else:
        print("Cancelled Extract.")
