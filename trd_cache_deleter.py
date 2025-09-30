# -*- coding: utf-8 -*-
# WeeChat script to delete unwanted rows from MariaDB via IRC commands
#
# Commands (from channel):
#   !dtvmaze <releasname cleaned>
#   !dimdb <releasename cleaned>
#
# Deletes from trd.data_cache where k = 'tvmaze:mud and sand' or 'imdb:superman 2025'
# and sends feedback message to the channel.
# Reqires pymysql (pip install pymysql or sudo apt install python3-pymysql)

import weechat
import pymysql

weechat.register("trd_cache_delete", "viceroy", "1.0", "GPL3",
                 "Delete rows from MariaDB via IRC commands", "", "")

# -------------------------------------------------------------------
# CONFIGURATION (edit these!)
# -------------------------------------------------------------------
CONFIG = {
    "network": "MyNet",       # IRC network name in WeeChat (use /network list to check)
    "channel": "#mydatachannel",     # Channel name where commands are accepted
    "mysql_host": "localhost",   # Database host
    "mysql_user": "mysqluser", # Database username
    "mysql_pass": "mysqlpassword",    # Database password
    "mysql_db": "trd",           # Database name
}
# -------------------------------------------------------------------


def run_delete(bufferp, prefix, message, source):
    """Delete matching row from database and give feedback in channel"""
    term = message.strip()
    if not term:
        return

    key = f"{source}:{term}"

    try:
        # Connect to database
        conn = pymysql.connect(
            host=CONFIG["mysql_host"],
            user=CONFIG["mysql_user"],
            password=CONFIG["mysql_pass"],
            database=CONFIG["mysql_db"],
            charset="utf8mb4",
            autocommit=True
        )
        cursor = conn.cursor()

        cursor.execute("DELETE FROM data_cache WHERE k = %s", (key,))
        rows_deleted = cursor.rowcount

        cursor.close()
        conn.close()

        if rows_deleted > 0:
            weechat.command(bufferp, f"/msg {CONFIG['channel']} {source.upper()} :: Deleted :: {term}")
        else:
            weechat.command(bufferp, f"/msg {CONFIG['channel']} {source.upper()} :: Not found :: {term}")

    except Exception as e:
        weechat.prnt("", f"dtdelete error: {e}")
        weechat.command(bufferp, f"/msg {CONFIG['channel']} {source.upper()} :: Error :: {term}")


def irc_message_cb(data, bufferp, date, tags, displayed, highlight, prefix, message):
    """Callback for messages in IRC"""
    server = weechat.buffer_get_string(bufferp, "localvar_server")
    chan   = weechat.buffer_get_string(bufferp, "localvar_channel")

    if server != CONFIG["network"] or chan.lower() != CONFIG["channel"].lower():
        return weechat.WEECHAT_RC_OK

    if message.startswith("!dtvmaze "):
            run_delete(bufferp, prefix, message[len("!dtvmaze "):], "tvmaze")

    elif message.startswith("!dimdb "):
            run_delete(bufferp, prefix, message[len("!dimdb "):], "imdb")

    return weechat.WEECHAT_RC_OK


# Hook PRIVMSGs
weechat.hook_print("", "irc_privmsg", "", 1, "irc_message_cb", "")
