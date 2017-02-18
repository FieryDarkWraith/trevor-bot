import sqlite3

dbFile = "data/trev.db"
db = sqlite3.connect(dbFile)
cursor = db.cursor()

#@param info == dictionary with necessary information
def addLawyer( info ):    
    for k in info:
        p = "INSERT INTO lawyer VALUES (\'"+k['name']+"\',"+k['currState']+","+k['rating']+");"
        cursor.execute(p)
    #runs checkWaitList for clients
    pass

#@param info == dictionary with necessary information
def addClient( info ):
    for k in info:
        p = "INSERT INTO client VALUES (\'"+k['age']+"\',"+k['currState']+");"
        cursor.execute(p)
    pass

#@param info 
def findMatchingId( _id ):
    #finds the matching id to a given id.
    #checks through both client and lawyer tables
    pass

def checkWaitList( ):
    #checks the waitlist table of clients.
    #returns the first client.
    pass

def unpair( first_id, second_id ):
    # unpairs client and lawyer
    # removes the client from the database.
    # frees the lawyer to receive a new client ( runs checkWaitList )
    pass
