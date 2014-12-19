#!/usr/bin/python

import time
import sqlite3
from math import sqrt

from CONSTANTS import LOG_FILE, DB_FILE, TABLES, VALUES, PAR_ID
from CONSTANTS import ACCOUNT_DB, ACCOUNT_TABLE, PLAYER_DB, WORLD_DB

LEVELS = ["islands", "regions", "locations"] # The table names


class Conn:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)

    def close(self):
        self.conn.close()

    def save(self):
        self.conn.commit()

    def select(self, columns, table, target):
        # called with obj.select(["col1", "col2"], "table", [("col", "value")])
        command = "SELECT {0} FROM {1} WHERE {2}"
        target = " AND ".join(v[0] + '=' + self.sanitize(v[1]) for v in target)
        fullCommand = command.format(", ".join(columns), table, target)
        c = self.conn.cursor()
        c.execute(fullCommand)
        result = c.fetchall()
        return result

    def update(self, table, colVals, target):
        # called with
        # obj.update("table_name", {"col":"new_value"}, ("col", "value))
        command = "UPDATE {0} SET {1} WHERE {2}"
        target = target[0] + "=" + self.sanitize(target[1])
        keys = colVals.keys()
        newValues = ", ".join(key + "=" + self.sanitize(colVals[key])
                              for key in keys)
        fullCommand = command.format(table, newValues, target)
        c = self.conn.cursor()
        c.execute(fullCommand)
        self.save()

    def exists(self, table, target):
        # called with obj.exists("table_name", ("column", "value"))
        command = "SELECT count(*) FROM {0} WHERE {1}"
        target = target[0] + "=" + self.sanitize(target[1])
        c = self.conn.cursor()
        fullCommand = command.format(table, target)
        c.execute(fullCommand)
        result = c.fetchone()
        # Might be able to replace the below with 'return bool(result)'
        return bool(len(result) and result[0])
    
    def table_exists(self, table):
        # called with obj.table_exists("table")
        command = """SELECT count(*) FROM sqlite_master
                     WHERE type='table' and name='{0}';"""
        c = self.conn.cursor()
        c.execute(command.format(table))
        result = c.fetchone()
        # Might be able to replace the below with 'return bool(result)'
        return bool(len(result) and result[0])

    def insert(self, table, columnValues):
        # called with obj.insert("table", {"col1": "value", "col2":int_val})
        command = "INSERT INTO {0} ({1}) VALUES ({2})"
        keys = columnValues.keys()
        cols = ", ".join(keys)
        vals = ", ".join(self.sanitize(columnValues[key]) for key in keys)
        fullCommand = command.format(table, cols, vals)
        c = self.conn.cursor()
        c.execute(fullCommand)
        self.save()

    def create_table(self, table, columns):
        # called with obj.create_table("table", ["col1", "col2"])
        command = "CREATE TABLE {0} ({1})"
        fullCommand = command.format(table, ", ".join(columns))
        c = self.conn.cursor()
        c.execute(fullCommand)
        self.save()

    def existing_tables(self):
        results = self.select(["name"], "sqlite_master", [("type", "table")])
        if not results: return []
        else: return [result[0] for result in results]

    def count_columns(self, table):
        if table not in self.existing_tables(): return 0
        command = "PRAGMA table_info({0})".format(table)
        fullCommand = command.format(table)
        c = self.conn.cursor()  
        c.execute(fullCommand)
        return len(c.fetchall())

    def count_rows(self, table):
        if table not in self.existing_tables(): return 0
        command = "SELECT count() FROM " + table
        c = self.conn.cursor()
        c.execute(command)
        return c.fetchone()[0]

    def sanitize(self, entry):
        if type(entry) == type(0):
            return str(entry)
        else:
            return "'" + entry.replace("'", "''") + "'"


class World:
    def __init__(self, conn, pid):
        self.conn = conn
        self.pid = pid

        self.set_location()

    def set_location(self):
        target = [("pid", self.pid)]
        result = self.conn.select(["level", "id"], "player_location", target)
        self.level, self.curID = result[0]
        self.level -= 1 # List starts from zero and DBs from 1

        self.curTable = LEVELS[self.level]

        result = self.conn.select("*", self.curTable, [("ROWID", self.curID)])
        self.name, self.parID, self.x, self.y = result[0]

        self.parent = self.parID and self.level
        self.child = len(LEVELS) > self.level+1

    def get_location(self):
        return self.curTable[:-1], self.name
   
    def get_children(self):
        if not self.child: return []
        table = LEVELS[self.level+1]
        cols = ["ROWID", "name"]
        result = self.conn.select(cols, table, [(PAR_ID, self.curID)])
        distance = 0
        places = [[ID, name, distance] for ID, name in result]
        return places
       
    def get_parent(self):
        if not self.parent: return []
        table = LEVELS[self.level-1]
        cols = ["ROWID", "name"]
        result = self.conn.select(cols, table, [("ROWID", self.parID)])
        ID, name = result[0]
        distance = 0
        return ID, name, distance
   
    def get_nearby(self):
        cols = ["ROWID", "name", "x", "y"]
        result = self.conn.select(cols, self.curTable, [(PAR_ID, self.parID)])
        nearby_places = []
        for place in result:
            ID, name, x, y = place
            distance = self.get_distance(self.x, self.y, x, y)
            nearby_places.append([ID, name, distance])
        return nearby_places

    def get_distance(self, x1, y1, x2, y2):
        return round(sqrt((x1-x2)**2 + (y1-y2)**2), 2)

    def move(self, target, ID):
        if target == "u":
            if not self.parent: return
            offset = 0
        elif target == "s":
            offset = 1
        elif target == "d":
            if not self.child: return
            offset = 2
            
        newVals = {"level":self.level+offset, "id":ID}
        self.conn.update("player_location", newVals, ("pid", self.pid))
        self.set_location()


class Player:
    def __init__(self, pid=None, db=DB_FILE):
        try: pid = int(pid)
        except: pid = 0
        
        self.conn = Conn(db)
        self.pid = pid
        self.valid_pid = self.is_valid_pid()
        if not self.is_valid_pid(): return

        self.world = World(self.conn, self.pid)

    def do_action(self, action):
        if not len(action): return
        target = action[0]
        ID = int(action[1:])

        if target in ["s", "d", "u"]: # Sideways, down, and up movement
            self.world.move(target, ID)

    def is_valid_pid(self):
        return self.conn.exists("player_location", ("pid", self.pid))

    def get_location(self):
        level, name = self.world.get_location()
        return "Current {0}: {1}".format(level, name)

    def make_links(self, places, direction):
        links = []
        target = {"up":"u", "down":"d", "sideways":"s"}[direction]
        prefix = {"up":"P: ", "down":"C: ", "sideways":""}[direction]
        for place in places:
            if not place: continue
            ID, name, distance = place
            get = dict_to_GET({"a":target + str(ID), "pid":self.pid})
            string = "{0}{1} ({2}): {3}".format(prefix, name, distance, ID)
            links.append((get, string))
        return links

    def get_links(self):
        links = []
        links += self.make_links([self.world.get_parent()], "up")
        links += self.make_links(self.world.get_nearby(), "sideways")
        links += self.make_links(self.world.get_children(), "down")

        return links


def GET_to_dict(get):
    if not get: return {}
    pairs = get[0].split('&')
    return dict([tuple([pair.split('=')[0], pair.split('=')[1]])
                 for pair in pairs if len(pair.split('=')) > 1])

def dict_to_GET(d):
    pairs = [str(key) + "=" + str(d[key]) for key in d]
    return "?" + "&".join(pairs)

def log(message):
    time_stamp = time.strftime("%Y %b %d %H:%M:%S", time.gmtime())
    with open(LOG_FILE, "a") as f:
        f.write(time_stamp + " -- " + message + "\n")

def db_check():
    conn = Conn(DB_FILE)

    tablesAdded = []
    existingTables = conn.existing_tables()
    for table in TABLES:
        if table in existingTables: continue
        tablesAdded.append(table)
        log("db_check creating table: " + table + ".")
        conn.create_table(table, TABLES[table])
    if not tablesAdded: log("db_check created no tables.")

    for value in VALUES:
        table = value[0]
        if table in tablesAdded:
            colVals = dict(zip(TABLES[table], value[1:]))
            conn.insert(table, colVals)
    if tablesAdded and VALUES:
        log("db_check added values to tables: " + ", ".join(tablesAdded))
    else:
        log("db_check added no values.")

    log("Initial db checks passed.")

def table(name, values):
    t = "<table border='1'>{0}</table>"
    titleRow = "<tr><td>" + name + "</td></tr>"
    row = "<tr><td>{0}</td><td>{1}</td></tr>"
    rows = "".join(row.format(str(val), str(values[val])) for val in values)
    return t.format(titleRow + rows)

def is_valid_login(username, password):
    conn = Conn(ACCOUNT_DB)
    target = {"username":username, "password":password}
    return conn.exists(ACCOUNT_TABLE, target)
