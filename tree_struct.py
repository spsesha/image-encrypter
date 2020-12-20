from tkinter import Tk, Frame, filedialog, Button, Label, \
    LEFT, Scrollbar, VERTICAL, RIGHT, Y, DISABLED, NORMAL, Toplevel, \
    Menu, messagebox, simpledialog, IntVar, Checkbutton
from tkinter import ttk
from pathlib import Path
from utils import check_and_populate, encrypt_file, decrypt_file, \
    create_directory, scale_size, check_and_delete
from PIL import ImageTk, Image
from io import BytesIO


home = str(Path.home())
app = Tk()
app.title('Image Directory')
list_frame = Frame(master=app)
list_frame.pack()
key = None
scale_check = IntVar()


is_file_selected = False
current_path = home
current_file = ''


def create_list_frame(parent, title):
    frame = Frame(master=parent)
    frame.pack(side=LEFT)
    view = ttk.Treeview(frame, height=20)
    ybar = Scrollbar(frame, orient=VERTICAL, command=view.yview)
    view.configure(yscroll=ybar.set)
    ybar.pack(side=RIGHT, fill=Y)
    view.heading('#0', text=title, anchor='w')
    view.column('#0', width=350)
    view.pack()
    return frame, view


def upload_files():
    global current_path
    filenames = filedialog.askopenfilenames(multiple=True,
                                           title='Select images',
                                           filetypes=(
                                               ('All files', '*.*'),
                                               ('PNG files', '*.png'),
                                               ('JPG files', '*.jpg'),
                                               ('JPEG files', '*.jpeg')
                                           ))
    for file in filenames:
        encrypt_file(file, current_path, key)
    check_and_populate(dir_view, file_view, current_path)


def open_image():
    global key, current_file
    if key is not None:
        win = Toplevel()
        win.wm_title('Image viewer')
        content = decrypt_file(current_file, key)
        image = Image.open(BytesIO(content))
        width, height = image.size
        if scale_check.get():
            scaled = scale_size(width, height)
        else:
            scaled = image.size
        photo = ImageTk.PhotoImage(image.resize(scaled))
        label = Label(master=win, image=photo)
        label.image = photo
        label.pack()
    else:
        messagebox.showerror('Error', 'Please set a password before reading the file')


def set_password():
    global key
    key = simpledialog.askstring('Password', 'Please enter your password', parent=app)


def delete_file():
    global current_file, current_path
    check_and_delete(current_file)
    check_and_populate(dir_view, file_view, current_path)


dir_frame, dir_view = create_list_frame(list_frame, 'Directory')
file_frame, file_view = create_list_frame(list_frame, 'Files')
dir_view.insert('', '0', home, text="Home")
check_and_populate(dir_view, file_view, home)
btn_frame = Frame(master=app)
btn_frame.pack()
upload_btn = Button(master=btn_frame, text='Upload', command=upload_files)
upload_btn['state'] = DISABLED
upload_btn.pack(side=LEFT)
open_btn = Button(master=btn_frame, text='Open', command=open_image)
open_btn['state'] = DISABLED
open_btn.pack(side=LEFT)
delete_btn = Button(master=btn_frame, text='Delete file', command=delete_file)
delete_btn.pack(side=LEFT)
check_btn = Checkbutton(btn_frame, text="Scale Image", variable=scale_check, onvalue=True, offvalue=False)
check_btn.select()
check_btn.pack()


def on_select(event):
    global is_file_selected, current_path
    iid, = event.widget.selection()
    check_and_populate(dir_view, file_view, iid)
    current_path = iid
    upload_btn['state'] = NORMAL
    open_btn['state'] = DISABLED


def selected_file(event):
    global current_file
    file, = event.widget.selection()
    current_file = file
    open_btn['state'] = NORMAL


def open_new_folder():
    folder_name = simpledialog.askstring('New folder', 'Please enter the new folder name', parent=app)
    if folder_name is not None:
        create_folder(folder_name)


def create_folder(new_folder):
    global current_path
    result = create_directory(current_path, new_folder)
    if not result:
        messagebox.showerror('Error', 'Error creating directory')
    else:
        messagebox.showinfo('Success', 'Directory created successfully')


menu = Menu(app)
app.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label='New folder', command=open_new_folder)
filemenu.add_command(label='Set Password', command=set_password)

dir_view.bind('<<TreeviewSelect>>', on_select)
file_view.bind('<<TreeviewSelect>>', selected_file)

app.geometry('800x500')
app.resizable(False, False)
app.mainloop()