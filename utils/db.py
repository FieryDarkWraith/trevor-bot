import sqlite3

dbFile = "../data/trev.db"
db = sqlite3.connect(dbFile)
cursor = db.cursor()

#@param info == dictionary with necessary information
def addLawyer( info ):  
    client = checkWaitList( info['currState'] )
    pair = ''
    if client is None:
        pair = "N/A"
    else:
        pair = client
        q = "UPDATE clients SET pair = '%s';"%(info['id'])
        cursor.execute(q);
        q = "DELETE FROM clients WHERE id = '%s';"%(client)
        
    p = "INSERT INTO lawyers VALUES ( '%s', '%s', '%s', '%s', %d );"%( info['id'], pair, info['name'], info['currState'], 3 );
    cursor.execute(p)
    db.commit()

#@param info == dictionary with necessary information
def addClient( info ):
    q = "SELECT * FROM lawyers WHERE pair = 'N/A' AND currState = '%s';"%( info['currState'] )
    result = cursor.execute(q).fetchone()
    pair = ''
    print result
    if result is None:
        q = "SELECT * FROM lawyers WHERE pair = 'N/A';"
        result = cursor.execute( q ).fetchone()
        if result is None:
            q = "INSERT INTO waitlist VALUES ( '%s' );"%( info['id'])
            cursor.execute(q)
            pair = "N/A"
        else:
            pair = result[0]
            q = "UPDATE lawyers SET pair = '%s' WHERE ID = '%s';"%( info['id'], result[0] )
            cursor.execute(q)
    else:
        pair = result[0]
        q = "UPDATE lawyers SET pair = '%s' WHERE ID = '%s';"%( info['id'], result[0] )
        cursor.execute(q)

        
    p = "INSERT INTO clients VALUES ( '%s', '%s', %d, '%s', '%s' );"%( info['id'], pair, info['age'], info['currState'], info['focus'] )
    cursor.execute(p)
    db.commit()

#@param info 
def findMatchingId( _id ):
    #finds the matching id to a given id.
    #checks through both client and lawyer tables
    q = "SELECT * FROM clients, lawyers WHERE clients.ID = %s OR lawyers.ID = %s"%( _id, _id )
    result = cursor.execute( q ).fetchone()
    if result is None:
        return None
    else:
        return result[1]

def checkWaitList( state ):
    #checks the waitlist table of clients.
    #returns the first client.
    q = "SELECT * FROM waitlist, clients WHERE clients.ID = waitlist.ID AND clients.currState = '%s';"%( state )
    result = cursor.execute( q ).fetchone()
    if result is None:
        q = "SELECT * FROM waitlist, clients WHERE clients.ID = waitlist.ID"
        result = cursor.execute( q ).fetchone()
        if result is None:
            #The waitlsit is empty
            return None
        else:
            return result[0]
    else:
        return result[0]

def unpair( client_id, lawyer_id ):
    q = "DELETE FROM clients WHERE ID = '%s' ;"%(client_id)
    cursor.execute(q)
    client = checkWaitList( info['currState'] )
    pair = ''
    if client is None:
        pair = "N/A"
    else:
        pair = client
        q = "UPDATE clients SET pair = '%s';"%(info['id'])
        cursor.execute(q);
    q = "UPDATE lawyers WHERE ID = '%s' SET pair = '%s';"%(lawyer_id, pair)
    cursor.execute(q)
    db.commit()
