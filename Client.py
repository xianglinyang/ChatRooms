import socket
import tkinter
import threading
import random
import tkinter.messagebox

Ip = '127.0.0.1'
Port = 50007
ServerAddr = (Ip, Port)
Port = random.randint(50008, 60000)
client_addr = ('127.0.0.1', Port)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(client_addr)

Channel = '0'
UserName = '0'    # 表示还未进入聊天室，没有username
UserId = '0'      # 表示还未进入聊天室，没有username

# 登录窗口
root1 = tkinter.Tk()
root1.title('选择UDP服务器')
root1['height'] = 110
root1['width'] = 280

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:50007')  # 默认显示的ip和端口
User = tkinter.StringVar()
User.set('')


# 服务器标签
labelIP = tkinter.Label(root1, text='服务器地址')
labelIP.place(x=20, y=10, width=80, height=20)

entryIP = tkinter.Entry(root1, width=80, textvariable=IP1)
entryIP.place(x=110, y=10, width=110, height=20)

# 用户名标签
labelUser = tkinter.Label(root1, text='用户名')
labelUser.place(x=20, y=40, width=80, height=20)

entryUser = tkinter.Entry(root1, width=80, textvariable=User)
entryUser.place(x=110, y=40, width=110, height=20)


# 登录按钮
# 用户名不能为空
def login(event=0):
    global Ip, Port, WindowUserName
    Ip, Port = entryIP.get().split(':')  # 获取IP和端口号
    Port = int(Port)  # 端口号需要为int类型
    WindowUserName = entryUser.get()
    if WindowUserName == "":
        tkinter.messagebox.showinfo(title="Reminder", message="Please input username")
    else:
        root1.destroy()  # 关闭窗口


root1.bind('<Return>', login)  # 回车绑定登录功能
but = tkinter.Button(root1, text='登录', command=login)
but.place(x=90, y=70, width=70, height=30)

root1.mainloop()


# 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title('Welcome to our chat rooms! ' + WindowUserName)  # 窗口命名为用户名
root['height'] = 380
root['width'] = 600

UserName = WindowUserName

# 创建多行文本框，聊天内容
listbox = tkinter.Listbox(root)
listbox.place(x=130, y=0, width=300, height=300)

# 创建输入文本框和关联变量
msg = tkinter.StringVar()
msg.set('')
entry = tkinter.Entry(root, width=120, textvariable=msg)
entry.place(x=130, y=310, width=230, height=50)

# channel list
channel_list = tkinter.Listbox(root)
channel_list.place(x=0, y=20, width=130, height=280)


# 请求channel的按钮
def channels_butt():
    message = UserName + ' ' + UserId + ':09:' + Channel
    s.sendto(message.encode(), ServerAddr)


channel_button = tkinter.Button(root, text="Channels:", command=channels_butt)
channel_button.place(x=25, y=0, width=80, height=20)


# 清除channel列表
def clear_channels():
    channel_list.delete(0, tkinter.END)


# channel列表
# 如果在其他房间，要先离开
def join(event):
    global UserName, UserId, Channel
    me = channel_list.get(channel_list.curselection())
    if Channel == '0':
        message = UserName + ' ' + UserId + ':10:' + Channel + ':' + me+' '+UserName
        s.sendto(message.encode(), ServerAddr)
    else:
        tkinter.messagebox.showerror(title="error", message="You have to leave this room before you join another room !")


# double click 加入 channel
channel_list.bind('<Double-Button>', join)


# online users
online_user_list = tkinter.Listbox(root)
online_user_list.place(x=430, y=00, width=170, height=300)


# 清除user list
def init_user_list():
    online_user_list.delete(0, tkinter.END)
    online_user_list.insert(tkinter.END, "----------Online Users--------")
    online_user_list.itemconfig(tkinter.END, fg='blue')


init_user_list()


# 清除user list
def clear_user_list():
    online_user_list.delete(0, tkinter.END)
    online_user_list.insert(tkinter.END, "----------Online Users--------")
    online_user_list.itemconfig(tkinter.END, fg='blue')


# 更新user list
def update_user_list(parameter):
    clear_user_list()
    para = parameter.split(' ')
    for item in para:
        online_user_list.insert(tkinter.END, item)


# msg
def client_msg(event):
    dstId = online_user_list.get(online_user_list.curselection())
    # 本窗口
    m = entry.get()
    if m == "":
        tkinter.messagebox.showinfo(title="Reminder", message="Please input message")
    else:
        listbox.insert(tkinter.END, "(private) To " + dstId + ': ' + m)
        listbox.itemconfig(tkinter.END, fg='blue')
        # 发送
        m = UserName + ' ' + UserId + ':12:' + Channel + ':' + dstId + ' ' + m
        s.sendto(m.encode(), ServerAddr)
        msg.set('')  # 发送后清空文本框


# 发送私人消息
# 消息不能为空
online_user_list.bind('<Double-Button>', client_msg)


def init():
    global Channel, UserId
    Channel = '0'
    UserId = '0'
    # 清空用户列表
    clear_user_list()
    # 清空文本框
    listbox.delete(0, tkinter.END)
    # 标题
    root.title('Welcome to our chat rooms! ' + UserName)
    # 请求新的channel
    channels_butt()


def leave_butt():
    if Channel == '0':
        tkinter.messagebox.showerror(title="ERROR", message="You are not in any channel!")
    else:
        message = UserName + ' ' + UserId + ':13:' + Channel
        s.sendto(message.encode(), ServerAddr)


leave_butt = tkinter.Button(root, text='Leave', command=leave_butt)
leave_butt.place(x=25, y=310, width=80, height=20)


# 滚动条
scrollbar = tkinter.Scrollbar(listbox, command=listbox.yview)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
listbox.config(yscrollcommand=scrollbar.set)


# 收到服务器回复的允许离开
def client_leave():
    tkinter.messagebox.showwarning(title="Attention", message="You have left channel!")
    init()


def client_recv(user, recv_data):
    user_info = user.split(' ', 1)
    user_id = user_info[1]
    # user_id == 0 表示服务器发送的
    m = 'From ' + user_id + ' :' + recv_data
    listbox.insert(tkinter.END, m)
    listbox.insert(tkinter.END, " ")


# 收到私人信息，变蓝
def private_msg(user, recv_data):
    user_info = user.split(' ', 1)
    user_id = user_info[1]
    m = 'From ' + user_id + ' :' + recv_data
    listbox.insert(tkinter.END, m)
    listbox.itemconfig(tkinter.END, fg='blue')


# 得到服务器回复准许加入
def client_join(user):
    global UserName, UserId, Channel
    user_info = user.split(' ', 2)
    UserId = user_info[1]
    Channel = user_info[2]
    # 标题
    root.title(Channel + " : " + UserId)


# 被服务器踢出channel
def kicked_out():
    tkinter.messagebox.showwarning(title="Attention", message="You have been kicked out!")
    init()


# 请求channel
def client_channel(parameter):
    if len(parameter) == 0:
        tkinter.messagebox.showinfo(title="Channels", message="There is no channel now!")
        clear_channels()
    else:
        clear_channels()
        para = parameter.split(' ')
        for item in para:
            channel_list.insert(tkinter.END, item)


def sb_leave(u):
    m = u + " has left!"
    tkinter.messagebox.showinfo(title="Attention", message=m)


def channel_closed():
    tkinter.messagebox.showwarning(title="Attention", message="Channel has been closed")
    init()


def send(event=0):
    # 应用层协议格式
    # user info
    # command type
    # sender_channel
    # parameters(if any)
    # msg(if any)
    global Channel, UserName, UserId
    m = entry.get()
    if m == "":
        tkinter.messagebox.showerror(title="ERROR", message="textbox cannot be null!")
    elif Channel == '0':
        tkinter.messagebox.showinfo(title="Reminder", message="Please join in channel first")
    else:
        m = UserName + ' ' + UserId + ':08:' + Channel + ':' + m
        s.sendto(m.encode(), ServerAddr)
        msg.set('')  # 发送后清空文本框


def rec():

    while True:
        data, r_addr = s.recvfrom(512)
        data = data.decode()
        recv_mes = data.split(':', 3)
        # [user_info,command,channel,parameters]
        if recv_mes[1] == '15':
            client_recv(recv_mes[0], recv_mes[3])
        elif recv_mes[1] == '16':
            client_leave()
        elif recv_mes[1] == '17':
            client_join(recv_mes[3])
        elif recv_mes[1] == '18':
            private_msg(recv_mes[0], recv_mes[3])
        elif recv_mes[1] == '19':
            client_channel(recv_mes[3])
        elif recv_mes[1] == '20':
            update_user_list(recv_mes[3])
        elif recv_mes[1] == '22':
            sb_leave(recv_mes[3])
        elif recv_mes[1] == '21':
            kicked_out()
        elif recv_mes[1] == '23':
            channel_closed()
        else:
            tkinter.messagebox.showerror(title="ERROR", message="Unknown message from server")


# 接收消息线程
t = threading.Thread(target=rec)
t.start()

# 创建发送按钮
send_button = tkinter.Button(root, text='发送', command=send)
send_button.place(x=370, y=310, width=60, height=50)

# 绑定回车发送信息
root.bind('<Return>', send)
root.mainloop()

s.close()
