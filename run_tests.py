#!/usr/bin/python

import os
import sys
import time

from tools import Conn

if len(sys.argv) > 1:
    try: COUNT = int(sys.argv[1])
    except: COUNT = 100
else:
    COUNT = 1
DB = "Test.db"


def clean_env():
    if DB in os.listdir(os.getcwd()):
        print("Cleaning test environment...")
        os.remove(DB)
    print("Test environment clean.")

def run_tests(tests):
    if not tests: print("No tests to run.")
    for i, test in enumerate(tests):
        print("=" * 30)
        start = time.time()
        result, _ = test(COUNT, COUNT)
        length = time.time() - start
        if not result: print("Test #" + str(i) + " failed.")
        print("Test #" + str(i) + " took " + str(length) + " seconds.")

def table_creation(tables=100, cols=10):
    existingTables = C.existing_tables()
    baseName = "table"
    cols = ["column" + str(i) for i in range(cols)]

    if C.table_exists(baseName + "0"):
        print("Table exists that shouldn't.")
        return False, 0

    start = time.time()
    for i in range(tables):
        tableName = baseName + str(i)
        C.create_table(tableName, cols)
    testTime = time.time() - start

    if not C.table_exists(baseName + "0"):
        print("Table doesn't exist that should")
        return False, 0

    newTables = len(C.existing_tables()) - len(existingTables)
    successfulTest = newTables == tables
    print(str(newTables) + " tables added in " + str(testTime))
    return successfulTest, testTime

def row_insert(rows=100, count=100):
    existingTables = C.existing_tables()
    if not len(existingTables):
        print("Creating table for row insert")
        table = "some_table"
        cols = ["column" + str(i) for i in range(10)]
        C.create_table(table, cols)
    else:
        table = existingTables[0]

    startingRows = C.count_rows(table)

    colCount = C.count_columns(table)
    cols = ["column" + str(i) for i in range(colCount)]
    colVals = dict(zip(cols, ["value" for i in range(colCount)]))

    start = time.time()
    for i in range(rows):
        C.insert(table, colVals)
    testTime = time.time() - start

    rowsAdded = C.count_rows(table) - startingRows

    print(str(rowsAdded) + " rows inserted in " + str(testTime))
    return True, testTime

def test_select(count=100, c=100):
    existingTables = C.existing_tables()
    if not len(existingTables):
        print("Creating table for select")
        table = "some_table"
        cols = ["column" + str(i) for i in range(10)]
        C.create_table(table, cols)
    else:
        table = existingTables[0]

    rows = C.count_rows(table)
    if not rows:
        print("Creating a row for select")
        colCount = C.count_columns
        cols =  ["column" + str(i) for i in range(colCount)]
        colVals = dict(zip(cols, ["value" for i in range(colCount)]))
        C.insert(table, colVals)

    rows = C.count_rows(table)

    result = C.select(["ROWID"], table, [("ROWID", rows)])
    if not result:
        print("Row could not be found.")
        return False, 0

    result = C.select(["ROWID"], table, [("ROWID", rows+1)])
    if result:
        print("A row that should not have been found was found.")
        return False, 0

    start = time.time()
    for i in range(count):
        C.select(["ROWID"], table, [("ROWID", rows)])
    totalTime = time.time() - start

    print(str(count) + " selections made in " + str(totalTime) + " seconds.")
    return True, totalTime

def test_update(count=100, c=100):
    existingTables = C.existing_tables()
    if not len(existingTables):
        print("Creating table to test update")
        table = "some_table"
        cols = ["column" + str(i) for i in range(10)]
        C.create_table(table, cols)
    else:
        table = existingTables[0]

    rows = C.count_rows(table)
    if not rows:
        print("Creating a row to test update")
        colCount = C.count_columns
        cols =  ["column" + str(i) for i in range(colCount)]
        colVals = dict(zip(cols, ["value" for i in range(colCount)]))
        C.insert(table, colVals)

    updateColumn = "column0"
    newValue = "newValue"
    rows = C.count_rows(table)

    result = C.select([updateColumn], table, [(updateColumn, newValue)])
    if result:
        print("Update selected a column that it wasn't supposed to")
        return False, 0
    
    C.update(table, {updateColumn:newValue}, ("ROWID", 1))
    result = C.select([updateColumn], table, [(updateColumn, newValue)])
    if not result:
        print("Update failed to select a column that it should have")
        return False, 0

    start = time.time()
    for i in range(count):
        value = newValue + str(i)
        C.update(table, {updateColumn:value}, ("ROWID", 1))
    totalTime = time.time() - start

    print(str(count) + " updates made in " + str(totalTime) + " seconds.")
    return True, totalTime


db_tests = [table_creation, row_insert, test_select, test_update]

tests = db_tests
#tests = []

print
print("Running tests where COUNT equals {0}".format(str(COUNT)))

clean_env()
C = Conn(DB)

START_TIME = time.time()
run_tests(tests)
END_TIME = time.time() - START_TIME

clean_env()

print("All tests completed in " + str(END_TIME) + " seconds.")
