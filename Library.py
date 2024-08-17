import sqlite3
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mb
from tkinter import simpledialog as sd

# Connecting to Database
connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
    'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT)'
)

# Functions
def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')

    if not Cid:
        mb.showerror('Issuer ID cannot be zero!', 'Can\'t keep Issuer ID empty, it must have a value')
    else:
        return Cid


def display_records():
    tree.delete(*tree.get_children())

    curr = connector.execute('SELECT * FROM Library')
    data = curr.fetchall()

    for records in data:
        tree.insert('', tk.END, values=records)


def clear_fields():
    bk_status.set('Available')
    for i in ['bk_id', 'bk_name', 'author_name', 'card_id']:
        globals()[i].set('')
    bk_id_entry.config(state='normal')
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass


def clear_and_display():
    clear_fields()
    display_records()


def add_record():
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    else:
        card_id.set('N/A')

    surety = mb.askyesno('Are you sure?',
                'Are you sure this is the data you want to enter?\nPlease note that Book ID cannot be changed in the future')

    if surety:
        try:
            connector.execute(
            'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get()))
            connector.commit()

            clear_and_display()

            mb.showinfo('Record added', 'The new record was successfully added to your database')
        except sqlite3.IntegrityError:
            mb.showerror('Book ID already in use!',
                    'The Book ID you are trying to enter is already in the database, please alter that book\'s record or check any discrepancies on your side')


def view_record():
    if not tree.focus():
        mb.showerror('Select a row!', 'To view a record, you must select it in the table. Please do so before continuing.')
        return

    current_item_selected = tree.focus()
    values_in_selected_item = tree.item(current_item_selected)
    selection = values_in_selected_item['values']

    bk_name.set(selection[0])
    bk_id.set(selection[1])
    bk_status.set(selection[3])
    author_name.set(selection[2])
    try:
        card_id.set(selection[4])
    except:
        card_id.set('')


def update_record():
    def update():
        if bk_status.get() == 'Issued':
            card_id.set(issuer_card())
        else:
            card_id.set('N/A')

        cursor.execute('UPDATE Library SET BK_NAME=?, BK_STATUS=?, AUTHOR_NAME=?, CARD_ID=? WHERE BK_ID=?',
                        (bk_name.get(), bk_status.get(), author_name.get(), card_id.get(), bk_id.get()))
        connector.commit()

        clear_and_display()

        edit.destroy()
        bk_id_entry.config(state='normal')
        clear.config(state='normal')

    view_record()

    bk_id_entry.config(state='disable')
    clear.config(state='disable')

    edit = tk.Button(left_frame, text='Update Record', font=btn_font, bg=btn_hlb_bg, width=20, command=update)
    edit.place(x=50, y=375)


def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]

    cursor.execute('DELETE FROM Library WHERE BK_ID=?', (selection[1], ))
    connector.commit()

    tree.delete(current_item)

    mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')

    clear_and_display()


def delete_inventory():
    if mb.askyesno('Are you sure?', 'Are you sure you want to delete the entire inventory?\n\nThis command cannot be reversed'):
        tree.delete(*tree.get_children())

        cursor.execute('DELETE FROM Library')
        connector.commit()
    else:
        return


def change_availability():
    if not tree.selection():
        mb.showerror('Error!', 'Please select a book from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    BK_id = values['values'][1]
    BK_status = values["values"][3]

    if BK_status == 'Issued':
        surety = mb.askyesno('Is return confirmed?', 'Has the book been returned to you?')
        if surety:
            cursor.execute('UPDATE Library SET bk_status=?, card_id=? WHERE bk_id=?', ('Available', 'N/A', BK_id))
            connector.commit()
        else:
            mb.showinfo('Cannot be returned', 'The book status cannot be set to Available unless it has been returned')
    else:
        cursor.execute('UPDATE Library SET bk_status=?, card_id=? where bk_id=?', ('Issued', issuer_card(), BK_id))
        connector.commit()

    clear_and_display()


def search_records():
    search_query = search_entry.get()
    cursor.execute("SELECT * FROM Library WHERE BK_NAME LIKE ? OR BK_ID LIKE ? OR AUTHOR_NAME LIKE ?", ('%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%'))
    search_result = cursor.fetchall()

    tree.delete(*tree.get_children())

    for record in search_result:
        tree.insert('', tk.END, values=record)


# Initializing the main GUI window
root = tk.Tk()
root.title('PythonGeeks Library Management System')
root.geometry('1010x530')
root.resizable(0, 0)

# StringVars
bk_status = tk.StringVar(value='Available')
bk_name = tk.StringVar()
bk_id = tk.StringVar()
author_name = tk.StringVar()
card_id = tk.StringVar()

# Frames
left_frame = tk.Frame(root, bg='LightSkyBlue')
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

RT_frame = tk.Frame(root, bg='DeepSkyBlue')
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

RB_frame = tk.Frame(root)
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Left Frame
tk.Label(left_frame, text='Book Name', bg='LightSkyBlue', font=('Georgia', 13)).place(x=98, y=25)
tk.Entry(left_frame, width=25, font=('Times New Roman', 12), textvariable=bk_name).place(x=45, y=55)

tk.Label(left_frame, text='Book ID', bg='LightSkyBlue', font=('Georgia', 13)).place(x=110, y=105)
bk_id_entry = tk.Entry(left_frame, width=25, font=('Times New Roman', 12), textvariable=bk_id)
bk_id_entry.place(x=45, y=135)

tk.Label(left_frame, text='Author Name', bg='LightSkyBlue', font=('Georgia', 13)).place(x=90, y=185)
tk.Entry(left_frame, width=25, font=('Times New Roman', 12), textvariable=author_name).place(x=45, y=215)

tk.Label(left_frame, text='Status of the Book', bg='LightSkyBlue', font=('Georgia', 13)).place(x=75, y=265)
style = ttk.Style()
style.configure('TMenubutton', font=('Times New Roman', 12))  # Set the font for OptionMenu
dd = ttk.OptionMenu(left_frame, bk_status, 'Available', 'Available', 'Issued', style='TMenubutton')
dd.place(x=75, y=300)

submit = tk.Button(left_frame, text='Add new record', font=('Gill Sans MT', 13), bg='SteelBlue', width=20, command=add_record)
submit.place(x=50, y=375)

clear = tk.Button(left_frame, text='Clear fields', font=('Gill Sans MT', 13), bg='SteelBlue', width=20, command=clear_fields)
clear.place(x=50, y=435)

# Right Top Frame
tk.Button(RT_frame, text='Delete book record', font=('Gill Sans MT', 13), bg='SteelBlue', width=17, command=remove_record).place(x=8, y=30)
tk.Button(RT_frame, text='Delete full inventory', font=('Gill Sans MT', 13), bg='SteelBlue', width=17, command=delete_inventory).place(x=178, y=30)
tk.Button(RT_frame, text='Update book details', font=('Gill Sans MT', 13), bg='SteelBlue', width=17, command=update_record).place(x=348, y=30)
tk.Button(RT_frame, text='Change Book Availability', font=('Gill Sans MT', 13), bg='SteelBlue', width=19, command=change_availability).place(x=518, y=30)

# Right Bottom Frame
tk.Label(RB_frame, text='BOOK INVENTORY', bg='DodgerBlue', font=("Noto Sans CJK TC", 15, 'bold')).pack(side=tk.TOP, fill=tk.X)

search_entry = tk.Entry(RB_frame, width=30)
search_entry.pack(pady=10)
search_button = tk.Button(RB_frame, text='Search', font=('Gill Sans MT', 13), bg='SteelBlue', command=search_records)
search_button.pack()

tree = ttk.Treeview(RB_frame, selectmode=tk.BROWSE, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID'))

XScrollbar = ttk.Scrollbar(tree, orient=tk.HORIZONTAL, command=tree.xview)
YScrollbar = ttk.Scrollbar(tree, orient=tk.VERTICAL, command=tree.yview)
XScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
YScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)

tree.heading('Book Name', text='Book Name', anchor=tk.CENTER)
tree.heading('Book ID', text='Book ID', anchor=tk.CENTER)
tree.heading('Author', text='Author', anchor=tk.CENTER)
tree.heading('Status', text='Status of the Book', anchor=tk.CENTER)
tree.heading('Issuer Card ID', text='Card ID of the Issuer', anchor=tk.CENTER)

tree.column('#0', width=0, stretch=tk.NO)
tree.column('#1', width=225, stretch=tk.NO)
tree.column('#2', width=70, stretch=tk.NO)
tree.column('#3', width=150, stretch=tk.NO)
tree.column('#4', width=105, stretch=tk.NO)
tree.column('#5', width=132, stretch=tk.NO)

tree.pack(expand=True, fill=tk.BOTH)

clear_and_display()

# Finalizing the window
root.mainloop()
