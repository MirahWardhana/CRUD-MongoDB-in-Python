from tkinter import *
import tkinter.ttk as ttk
from pymongo import MongoClient

#replace with your mongo client server
client = MongoClient("mongodb+srv://")
db = client["dbLagufy"]
collection = db["users"]
collection2 = db["playlists"]

def deleteUser():
    selected_item = table.focus()  
    if selected_item:
        user_id = table.item(selected_item)["values"][0]  
        collection.delete_one({"_id": user_id}) 
        refresh_table_user()  
        
def insertUser():
    id = str(text_id.get())
    username = text_username.get()
    playlist = text_playlist.get().split(',')

    document = {
        "_id": id,
        "username": username,
        "playlist": playlist
    }
    collection.insert_one(document)
    refresh_table_user()

def refresh_table_user():
    table.delete(*table.get_children())
    results = collection.find()

    for result in results:
        id = str(result["_id"])  
        username = result["username"]
        playlist = [str(item) for item in result["playlist"][::-1]]  

        table.insert("", "end", values=(id, username, ", ".join(playlist)))

def showUser():
    selected_item = table.focus()
    if not selected_item:
        return

    item_values = table.item(selected_item, "values")
    if not item_values:
        return

    id = item_values[0]
    username = item_values[1]
    playlist = item_values[2]

    text_id.delete(0, END)
    text_id.insert(END, id)
    text_username.delete(0, END)
    text_username.insert(END, username)
    text_playlist.delete(0, END)
    text_playlist.insert(END, playlist)

def updateUser():
    id = str(text_id.get())

    username = text_username.get()
    playlist = text_playlist.get().split(',')

    selected_item = table.focus()
    if not selected_item:
        return
    table.item(selected_item, values=(id, username, ", ".join(playlist)))

    collection.update_one({"_id": id}, {"$set": {"username": username, "playlist": playlist}})
    
def refresh_table_playlist():
    table2.delete(*table2.get_children())

    results = collection2.aggregate([
        {
            "$lookup": {
                "from": "songs",
                "localField": "songs",
                "foreignField": "_id",
                "as": "songDetails"
            }
        },
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "songs": "$songDetails.title"
            }
        }
    ])

    for result in results:
        id = str(result["_id"])
        title = result["title"]
        songs = ", ".join(result["songs"])

        table2.insert("", "end", values=(id, title, songs))


root = Tk()
root.title("Input Tabel User")
root.geometry("1210x400")
root.configure(bg='white')

label = Label(root, text="Tabel Users")
label.grid(row=0, column=0, columnspan=2)

label = Label(root, text="ID")
label.grid(row=1, column=0)
label = Label(root, text="Username")
label.grid(row=2, column=0)
label = Label(root, text="Playlist")
label.grid(row=3, column=0)

text_id = Entry(root, width=70)
text_id.grid(row=1, column=1)
text_username = Entry(root, width=70)
text_username.grid(row=2, column=1)
text_playlist = Entry(root, width=70)
text_playlist.grid(row=3, column=1)

buttonCommit = Button(root, height=1, width=20, text="Insert", command=insertUser)
buttonCommit.grid(row=4, column=1, sticky="w")

buttonDelete = Button(root, height=1, width=20, text="Delete", command=deleteUser)
buttonDelete.grid(row=4, column=1, sticky="e")

buttonUpdate = Button(root, height=1, width=20, text="Update", command=updateUser)
buttonUpdate.grid(row=4, column=1)

buttonShow = Button(root, height=1, width=20, text="Show User", command=showUser)
buttonShow.grid(row=4, column=0)

table = ttk.Treeview(root, columns=("id", "username", "playlist"), show="headings")
table.grid(row=5, column=0, columnspan=2, sticky="nsew")

table.heading("id", text="ID")
table.heading("username", text="Username")
table.heading("playlist", text="Playlist")

scrollbar = ttk.Scrollbar(root, orient="vertical", command=table.yview)
scrollbar.grid(row=5, column=2, sticky="ns")
table.configure(yscrollcommand=scrollbar.set)

scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=table.xview)
scrollbar_x.grid(row=6, column=0, columnspan=2, sticky="ew")
table.configure(xscrollcommand=scrollbar_x.set)

refresh_table_user()

table2 = ttk.Treeview(root, columns=("id", "title", "songs"), show="headings")
table2.grid(row=1, column=2, rowspan=5, sticky="nsew")

table2.heading("id", text="ID")
table2.heading("title", text="Title")
table2.heading("songs", text="Songs")

refresh_table_playlist()

root.mainloop()
