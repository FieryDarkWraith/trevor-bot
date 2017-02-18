import sqlite3

dbFile = "data/trev.db"
db = sqlite3.connect(dbFile)
cursor = db.cursor()

def addLawyer( id ):
    #adds lawyer to database
    #runs checkWaitList for clients
    pass

def addClient( id ):
    #adds a client
    pass

def findMatchingId( id ):
    #finds the matching id to a given id.
    #checks through both client and lawyer tables
    pass

def checkWaitList( ):
    #checks the waitlist table of clients.
    #returns the first client. 
    pass

def unpair( firstId, secondId ):
    # unpairs client and lawyer
    # removes the client from the database.
    # frees the lawyer to receive a new client ( runs checkWaitList )
    pass


