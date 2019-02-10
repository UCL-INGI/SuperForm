import sqlite3
from requests import get
from json import dumps

db = sqlite3.connect('/tmp/ictv_database.sqlite')
c = db.cursor()
conf = {'enable_rest_api': 'true', 'api_key': 'azertyuiop'}

for i in range(1,4):
    c.execute('INSERT INTO channel VALUES (' + str(i) + ', "channel-' + str(i) +' ", ?, 1, "public", "azerty' + str(i) + '", "PluginChannel")', (None,)).fetchall()

    c.execute('INSERT INTO plugin_channel VALUES (' + str(i) + ', 1, ?, 1, 60, 0, ?)', (dumps(conf),None,)).fetchall()

db.commit()

for i in range(1,4):
    get('http://0.0.0.0:8000/hack/' + str(i))




