# server-alpha.py

import asyncio
import aiosqlite
import json

TRUNCATE = (True, True, False)
DATABASE = 'database.db'

async def handle_client(reader, writer): #MISSING KEYS ARE NOT HANDLED
    data = await reader.read()
    message = json.loads(data.decode())
    addr = writer.get_extra_info('peername')

            

    print(f"Received {message!r} from {addr!r}")
    
    async with aiosqlite.connect(DATABASE) as db:
        async with db.cursor() as c:

            await c.execute("SELECT rowid FROM Users WHERE name=:name AND pass=:pass",
                                {'name': message['auth']['username'], 'pass': message['auth']['token']})

            try:
                rid = await c.fetchone()
                rid = rid[0] #BUG: rid becomes none when there is no auth. none can't be subscripted!!!!!
                
            except IndexError: #This will be frustrating for clients
                message_out = "-----------ZERO-LENGTH: MISSING USER/TOKEN---------------"
                
            except TypeError:
                message_out = "-----------MISSING USER/TOKEN---------------"
                    
            else:
                if message['mode'] == 'record':
                
                    await c.execute("SELECT rowid FROM Facilities WHERE name=:name",
                                    {'name': message['payload']['fname']})
                    
                    try:
                        fid = await c.fetchone()
                        fid = fid[0] #BUG: fid becomes none when there is no auth. none can't be subscripted!!!!!
                         
                    except IndexError:
                        message_out = "-----------ZERO-LENGTH: MISSING FACILITY---------------"

                    except TypeError:
                        message_out = "-----------MISSING FACILITY---------------"
                        
                    else:
                        print(f'Rid = {rid}, Fid = {fid}')
                        await c.execute("INSERT INTO Records (rid, fid, time, num) VALUES (:rid, :fid, strftime('%s','now'), :num)",
                                        {'rid': rid, 'fid': fid, 'num': int(message['payload']['number'])})

                        await db.commit()

                        await c.execute("SELECT rowid,* FROM Records")
                        message_out = await c.fetchall()
 
                
                elif message['mode'] == 'remove':
                    pass

                elif message['mode'] == 'fetchall':

                    if message['payload'] in range (4):
                        if message['payload'] == 0:
                            tempsql = "SELECT rowid,* FROM Facilities"
                            keys = ['id', 'name', 'area'] #############################################################################################################Change this when change table
                            
                        elif message['payload'] == 1:
                            tempsql = "SELECT rowid,* FROM Users"
                            keys = ['id', 'name', 'pass', 'zero']
                        elif message['payload'] >= 2: #2 or 3
                            tempsql = "SELECT rowid,* FROM Records"
                            keys = ['id', 'userid', 'locid', 'unixtime', 'pollres']
                            if message['payload'] == 3:
                                await c.execute("SELECT rowid, name FROM Facilities")
                                fdiction = dict(await c.fetchall())
                                await c.execute("SELECT rowid, name FROM Users")
                                udiction = dict(await c.fetchall())
                                

                        await c.execute(tempsql)
                        results_table = await c.fetchall()

                        message_out = [dict(zip(keys, temprow)) for temprow in results_table]

                        if message['payload'] == 3: #translation
                                await c.execute("SELECT rowid, name FROM Users")
                                udiction = dict(await c.fetchall())
                                await c.execute("SELECT rowid, name FROM Facilities")
                                fdiction = dict(await c.fetchall())

                                
                                for ndx in range(len(message_out)):
                                    message_out[ndx]['userid'] = udiction[message_out[ndx]['userid']]
                                    message_out[ndx]['locid'] = fdiction[message_out[ndx]['locid']]
                                    

                    else:
                        message_out = "-------------------BAD PAYLOAD------------------"


                elif message['mode'] == 'calculate':
                    pass
                
                else:
                    message_out = "-----------INVALID MODE---------------"

                

            await db.commit()

            """
            if message['command'] == "write":
                await c.executemany("INSERT INTO Facilities (name, area) VALUES (:name, :area)", [message['payload']])
                await db.commit()
                message_out = "probably wrote something"
                ##-----------------------------------------------------------------------------SQL
            elif message['command'] == "read":
                await c.execute("SELECT * FROM Facilities")
                message_out = await c.fetchall()
            elif message['command'] == "clear":
                await c.execute("DELETE FROM Facilities")
                await db.commit()
                message_out = "table probably truncated"
            """
    
    #Some Calculator Here
    await asyncio.sleep(1)

    data_out = json.dumps(message_out).encode()
            
    print(f"Send: {message!r}")
    writer.write(data_out)
    writer.write_eof()
    await writer.drain()

    print("Close the connection")
    writer.close()
        

async def main():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.cursor() as c:

            await c.execute("""CREATE TABLE IF NOT EXISTS Facilities (
                            name TEXT,
                            area INTEGER,
                            UNIQUE (name))""")

            await c.execute("""CREATE TABLE IF NOT EXISTS Users (
                            name TEXT,
                            pass TEXT,
                            admin INTEGER,
                            UNIQUE (name))""")

            await c.execute("""CREATE TABLE IF NOT EXISTS Records (
                            rid INTEGER,
                            fid INTEGER,
                            time INTEGER,
                            num INT,
                            FOREIGN KEY (rid) REFERENCES Users (rowid),
                            FOREIGN KEY (fid) REFERENCES Facilities (rowid))""")

            if TRUNCATE[0]:
                await c.execute("DELETE FROM Facilities")
                await c.executemany("INSERT INTO Facilities (name, area) VALUES (:name, :area)",
                                    [
                                        {'name': 'Grocery Store', 'area': 40000},
                                        {'name': 'Gym', 'area': 4000},
                                        {'name': 'Store', 'area': 1000},
                                        {'name': 'Park', 'area': 30000},
                                        {'name': 'Restaurant', 'area': 175},
                                        {'name': 'Washroom', 'area': 50}
                                    ])
                print("!Truncated Facilities!")

            if TRUNCATE[1]:
                await c.execute("DELETE FROM Users")
                await c.execute("INSERT INTO Users (name, pass) VALUES ('superadmin','password')")
                print("!Truncated Users!")

            if TRUNCATE[2]:
                await c.execute("DELETE FROM Records")
                print("!Truncated Records!")
            
            await db.commit()
            
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
                                                
    async with server:
        await server.serve_forever()

asyncio.run(main(), debug=True)
    
