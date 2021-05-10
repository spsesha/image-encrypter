from pathlib import Path
import os
import re

home = str(Path.home())
arr = os.listdir(home)

files = [f for f in arr if os.path.isfile(os.path.join(home, f)) and re.search('\.enc$', f)]
files.sort(key=lambda y: y.lower())
print(files)
print('==============')
direc = [d for d in arr if os.path.isdir(os.path.join(home, d)) and not d.startswith('.')]
direc.sort(key=lambda y: y.lower())
print(direc)

# from tkinter import *
# from tkinter import ttk
#
# app = Tk()
# app.title('GUI Application of python')
#
# ttk.Label(app, text="Treeview(hierarchical)").pack()
#
# def on_select(event):
#     print(event.widget.selection())
#
# treeview = ttk.Treeview(app)
# treeview.pack()
#
# treeview.insert('', '0', 'item1', text='GeeksForGeeks')
# treeview.insert('', '1', 'item2', text='Computer Science')
# treeview.insert('', '2', 'item3', text='GATE papers')
# treeview.insert('', 'end', 'item4', text='Programming Languages')
#
# treeview.insert('item2', 'end', 'Algorithm', text='Algorithm')
# treeview.insert('item2', 'end', 'Data structure', text='Data structure')
# treeview.insert('item3', 'end', '2018 paper', text='2018 paper')
# treeview.insert('item3', 'end', '2019 paper', text='2019 paper')
# treeview.insert('item4', 'end', 'Python', text='Python')
# treeview.insert('item4', 'end', 'Java', text='Java')
#
# treeview.move('item2', 'item1', 'end')
# treeview.move('item3', 'item1', 'end')
# treeview.move('item4', 'item1', 'end')
#
# treeview.bind('<<TreeviewSelect>>', on_select)
#
# app.mainloop()