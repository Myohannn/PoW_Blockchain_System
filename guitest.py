from tkinter import *

root = Tk()
root.title("aaa")
root.geometry("400x600")

my_frame = Frame(root)
my_sb = Scrollbar(my_frame, orient=VERTICAL)

my_listbox = Listbox(my_frame, width=50, yscrollcommand=my_sb.set)

my_sb.config(command=my_listbox.yview())
my_sb.pack(side=RIGHT, fill=Y)
my_frame.pack()

my_listbox.pack(pady=15)

my_listbox.insert(END, "abcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "asdsada")
my_listbox.insert(END, "asadsadbcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "asdsada")
my_listbox.insert(END, "asadsadbcd")
my_listbox.insert(END, "absdsadsadcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "asdsada")
my_listbox.insert(END, "asadsadbcd")
my_listbox.insert(END, "absdsadsadcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "asdsada")
my_listbox.insert(END, "asadsadbcd")
my_listbox.insert(END, "absdsadsadcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "asdsada")
my_listbox.insert(END, "asadsadbcd")
my_listbox.insert(END, "absdsadsadcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "asdsada")
my_listbox.insert(END, "asadsadbcd")
my_listbox.insert(END, "absdsadsadcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "abcd")
my_listbox.insert(END, "asdsada")
my_listbox.insert(END, "asadsadbcd")
my_listbox.insert(END, "absdsadsadcd")

my_listbox.insert(END, "absdsadsadcd")

root.mainloop()