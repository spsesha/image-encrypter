import os
from tkinter import Tk, Frame, filedialog, Button, Label, \
    LEFT, Scrollbar, VERTICAL, RIGHT, Y, DISABLED, NORMAL, Toplevel, \
    Menu, messagebox, simpledialog, IntVar, Checkbutton, ttk, BooleanVar
from pathlib import Path
from PIL import ImageTk, Image, ImageOps
from io import BytesIO
import file_processing as fp
from google_auth import GoogleAuth


class MainWindow:
    def __init__(self):
        self.app = None
        self.list_frame = None
        self.key = None
        self.scale_check = None
        self.is_file_selected = False
        self.current_path = None
        self.current_file = None
        self.dir_view = None
        self.file_view = None
        self.upload_btn = None
        self.open_btn = None
        self.delete_btn = None
        self.export_btn = None
        self.ishidden = None
        self.is_google = False
        self.google = None
        self.screen_width = None
        self.screen_height = None
        self.create_initial_view()

    def create_initial_view(self):
        self.current_path = str(Path.home())
        self.app = Tk()
        self.get_screen_resolution()
        self.app.title('Image directory')
        self.app.geometry('800x500')
        self.scale_check = IntVar()
        self.ishidden = BooleanVar()
        self.is_google = BooleanVar()
        self.app.resizable(False, False)
        self.list_frame = Frame(master=self.app)
        self.list_frame.pack()
        self.dir_view = self.create_list_frame('Directory')
        self.file_view = self.create_list_frame('Files')
        self.dir_view.insert('', '0', self.current_path, text='Home')
        self.dir_view.bind('<<TreeviewSelect>>', lambda e: self.on_select(e))
        self.file_view.bind('<<TreeviewSelect>>', lambda e: self.selected_file(e))
        self.check_and_populate(self.current_path)
        btn_frame = Frame(master=self.app)
        btn_frame.pack()
        self.upload_btn = Button(master=btn_frame, text='Upload', command=lambda: self.upload_files())
        self.upload_btn['state'] = DISABLED
        self.upload_btn.pack(side=LEFT)
        self.open_btn = Button(master=btn_frame, text='Open', command=lambda: self.open_image())
        self.open_btn['state'] = DISABLED
        self.open_btn.pack(side=LEFT)
        self.delete_btn = Button(master=btn_frame, text='Delete file', command=lambda: self.delete_file())
        self.delete_btn.pack(side=LEFT)
        self.delete_btn['state'] = DISABLED
        self.export_btn = Button(master=btn_frame, text='Export file', command=lambda: self.export_files())
        self.export_btn.pack(side=LEFT)
        self.export_btn['state'] = DISABLED
        check_btn = Checkbutton(btn_frame, text='Scale Image', variable=self.scale_check, onvalue=True, offvalue=False)
        check_btn.select()
        check_btn.pack()
        hidden_btn = Checkbutton(btn_frame, text='Hidden folder', variable=self.ishidden, command=lambda: self.check_and_populate(self.current_path), onvalue=True, offvalue=False)
        hidden_btn.deselect()
        hidden_btn.pack()
        menu = Menu(self.app)
        self.app.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='New folder', command=lambda: self.open_new_folder())
        filemenu.add_command(label='Set Password', command=lambda: self.set_password())
        filemenu.add_separator()
        filemenu.add_checkbutton(label='Google Drive', onvalue=True, offvalue=False, variable=self.is_google, command=lambda: self.google_signin())
        filemenu.add_command(label='Logout Google', command=lambda: self.google_signout())

    def start(self):
        initial_path = self.current_path
        initial_path = simpledialog.askstring(title='Initial Path', prompt='Please enter a path',
                                              initialvalue=initial_path)
        self.current_path = initial_path
        self.refresh_dir_view(initial_path, 'Home')
        self.app.mainloop()

    def get_screen_resolution(self):
        self.screen_width = self.app.winfo_screenwidth() * 0.9
        self.screen_height = self.app.winfo_screenheight() * 0.9

    def create_list_frame(self, title):
        frame = Frame(master=self.list_frame)
        frame.pack(side=LEFT)
        view = ttk.Treeview(frame, height=20)
        ybar = Scrollbar(frame, orient=VERTICAL, command=view.yview)
        view.configure(yscroll=ybar.set)
        ybar.pack(side=RIGHT, fill=Y)
        view.heading('#0', text=title, anchor='w')
        view.column('#0', width=350)
        view.pack()
        return view

    def google_signin(self):
        if self.is_google.get():
            self.google = GoogleAuth()
            self.current_path = 'root'
            self.upload_btn['state'] = DISABLED
            self.open_btn['state'] = DISABLED
            self.export_btn['state'] = DISABLED
            self.delete_btn['state'] = DISABLED
            # for item in self.dir_view.get_children():
            #     self.dir_view.delete(item)
            # self.file_view.delete(*self.file_view.get_children())
            # self.dir_view.insert('', '0', 'root', text='Drive')
            self.refresh_dir_view('root', 'Drive')
            self.check_and_populate(self.current_path)
        else:
            # self.google.logout()
            self.current_path = str(Path.home())
            # for item in self.dir_view.get_children():
            #     self.dir_view.delete(item)
            # self.file_view.delete(*self.file_view.get_children())
            # self.dir_view.insert('', '0', self.current_path, text='Home')
            self.refresh_dir_view(self.current_path, 'Home')

    def refresh_dir_view(self, path, text):
        for item in self.dir_view.get_children():
            self.dir_view.delete(item)
        self.file_view.delete(*self.file_view.get_children())
        self.dir_view.insert('', '0', path, text=text)

    def google_signout(self):
        self.google.logout()
        self.is_google.set(False)
        self.google_signin()

    def check_and_populate(self, path):
        if self.is_google.get():
            files, dirs = self.google.get_list(path)
            if not path == '':
                has_child = len(self.dir_view.get_children(path))
                if has_child:
                    self.dir_view.delete(*self.dir_view.get_children(path))
                self.populate_dir_list(path, dirs)
            self.populate_files(path, files)
        else:
            files, dirs = fp.get_items_list(path, self.ishidden.get())
            if not path == '':
                has_child = len(self.dir_view.get_children(path))
                if has_child:
                    self.dir_view.delete(*self.dir_view.get_children(path))
                self.populate_dir_list(path, dirs)
            self.populate_files(path, files)

    def populate_dir_list(self, path, dirs):
        for d in dirs:
            if self.is_google.get():
                self.dir_view.insert(path, 'end', d['id'], text=d['name'])
            else:
                iid = os.path.join(path, d)
                self.dir_view.insert(path, 'end', iid, text=d)

    def populate_files(self, path, files):
        self.file_view.delete(*self.file_view.get_children())
        for f in files:
            if self.is_google.get():
                self.file_view.insert('', 'end', f['id'], text=f['name'])
            else:
                file_path = os.path.join(path, f)
                self.file_view.insert('', 'end', file_path, text=f)

    def upload_files(self):
        filenames = filedialog.askopenfilenames(multiple=True,
                                                title='Select images',
                                                filetypes=(
                                                    ('PNG files', '*.png'),
                                                    ('JPG files', '*.jpg'),
                                                    ('JPEG files', '*.jpeg')
                                                ))
        for file in filenames:
            fp.encrypt_file(file, self.current_path, self.key)
        self.check_and_populate(self.current_path)

    def export_files(self):
        if self.key is not None:
            content = fp.decrypt_file(self.current_file, self.key)
            original_file = '.'.join(self.current_file.split('.')[:-1])
            fp.write_raw(content, original_file)
        else:
            messagebox.showerror('Error', 'Please set a password before reading the file')

    def open_image(self):
        if self.key is not None:
            win = Toplevel()
            win.wm_title('Image Viewer')
            if self.is_google.get():
                content = self.google.get_image_content(self.current_file, self.key)
            else:
                content = fp.decrypt_file(self.current_file, self.key)
            image = Image.open(BytesIO(content))
            image = ImageOps.exif_transpose(image)
            width, height = image.size
            if self.scale_check.get():
                scaled = self.scale_size(width, height)
            else:
                scaled = image.size
            photo = ImageTk.PhotoImage(image.resize(scaled))
            # photo = ImageTk.PhotoImage(image)
            label = Label(master=win, image=photo)
            label.image = photo
            label.pack()
        else:
            messagebox.showerror('Error', 'Please set a password before reading the file')

    def set_password(self):
        self.key = simpledialog.askstring('Password', 'Please enter your password', show='*', parent=self.app)

    def delete_file(self):
        fp.check_and_delete(self.current_file)
        self.check_and_populate(self.current_path)

    def scale_size(self, width, height):
        ratio = 1
        if width > height:
            if width > self.screen_width:
                ratio = self.screen_width / width
        else:
            if height > self.screen_height:
                ratio = self.screen_height / height
        scaled_width = int(width * ratio)
        scaled_height = int(height * ratio)
        #
        # reverse = width < height
        # if reverse:
        #     width, height = height, width
        # ratio = 1000/width
        # scaled_width = int(width * ratio)
        # scaled_height = int(height * ratio)
        # if reverse:
        #     scaled_width, scaled_height = scaled_height, scaled_width
        return scaled_width, scaled_height

    def on_select(self, event):
        iid, = event.widget.selection()
        self.check_and_populate(iid)
        self.current_path = iid
        self.open_btn['state'] = DISABLED
        if not self.is_google.get():
            self.upload_btn['state'] = NORMAL
            self.export_btn['state'] = DISABLED
            self.export_btn['state'] = DISABLED

    def selected_file(self, event):
        self.current_file, = event.widget.selection()
        self.open_btn['state'] = NORMAL
        if not self.is_google.get():
            self.export_btn['state'] = NORMAL
            self.delete_btn['state'] = NORMAL

    def open_new_folder(self):
        folder_name = simpledialog.askstring('New folder', 'Please enter the new folder name', parent=self.app)
        if folder_name is not None:
            result = fp.create_directory(self.current_path, folder_name)
            if not result:
                messagebox.showerror('Error', 'Error creating directory')
            else:
                messagebox.showinfo('Success', 'Directory created successfully')

    def create_folder(self, new_folder):
        result = fp.create_directory(self.current_path, new_folder)
        if result:
            messagebox.showinfo('Success', 'Directory created successfully')
        else:
            messagebox.showerror('Error', 'Error creating directory')