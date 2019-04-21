import socket
import tkinter
import threading
import random

Ip = '127.0.0.1'
Port = 50007
ServerAddr = (Ip, Port)
Port = random.randint(50008,60000)
client_addr = ('127.0.0.1', Port)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(client_addr)

Channel = '0'
UserName = '0'    # 表示还未进入聊天室，没有username
UserId = '0'     # 表示还未进入聊天室，没有username

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
def login(event=0):
    global Ip, Port, WindowUserName
    Ip, Port = entryIP.get().split(':')  # 获取IP和端口号
    Port = int(Port)  # 端口号需要为int类型
    WindowUserName = entryUser.get()
    root1.destroy()  # 关闭窗口


root1.bind('<Return>', login)  # 回车绑定登录功能
but = tkinter.Button(root1, text='登录', command=login)
but.place(x=90, y=70, width=70, height=30)

root1.mainloop()


# 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title('Welcome to our chat rooms! ' + WindowUserName)  # 窗口命名为用户名
root['height'] = 330
root['width'] = 450

# 创建多行文本框
listbox = tkinter.Listbox(root, width=300)
listbox.place(x=5, y=0, width=440, height=280)

# 创建输入文本框和关联变量
msg = tkinter.StringVar()
msg.set('')
entry = tkinter.Entry(root, width=120, textvariable=msg)
entry.place(x=5, y=285, width=300, height=30)


def send(event=0):
    global Channel, UserName, UserId
    m = entry.get()
    # 应用层协议格式
    # parameter_number
    # command type
    # sender_channel
    # parameters
    # msg(if any)
    mes = m.split(' ', 1)
    if mes[0] == '/channels':
        message = UserName + ' ' + UserId + ':09:' + Channel
    elif mes[0] == '/join':
        if UserId == '0':
            message = UserName + ' ' + UserId + ':10:' + Channel + ':' + mes[1]
        else:
            listbox.insert(tkinter.END, "You have to leave this room then you can join another room.")
    elif mes[0] == '/list':
        message = UserName + ' ' + UserId + ':11:' + Channel
    elif mes[0] == '/msg':
        message = UserName + ' ' + UserId + ':12:' + Channel + ':' + mes[1]
        listbox.insert(tkinter.END, "(private) To "+mes[1])
    elif mes[0] == '/leave':
        message = UserName + ' ' + UserId + ':13:' + Channel
    else:
        if len(mes) == 1:
            message = UserName + ' ' + UserId + ':08:' + Channel + ':' + mes[0]
        else:
            message = UserName + ' ' + UserId + ':08:' + Channel + ':' + mes[0] + ' ' + mes[1]
    s.sendto(message.encode(), ServerAddr)
    msg.set('')  # 发送后清空文本框


def rec():
    def client_recv(user, recv_data):
        user_info = user.split(' ', 1)
        user_id = user_info[1]
        # user_id == 0 表示服务器发送的
        m = 'From ' + user_id + ' :' + recv_data
        listbox.insert(tkinter.END, m)

    def client_join(user):
        global UserName, UserId, Channel
        user_info = user.split(' ', 2)
        UserName = user_info[0]
        UserId = user_info[1]
        Channel = user_info[2]
        listbox.insert(tkinter.END, "You are now in room: "+Channel)

    def client_leave(data):
        global Channel, UserName, UserId
        listbox.insert(tkinter.END, data)
        Channel = '0'
        UserName = '0'
        UserId = '0'

    while True:
        data, r_addr = s.recvfrom(512)
        data = data.decode()
        recv_mes = data.split(':', 3)
        # [user_info,command,channel,parameters]
        if recv_mes[1] == '15':
            client_recv(recv_mes[0], recv_mes[3])
        elif recv_mes[1] == '16':
            client_leave(recv_mes[3])
        elif recv_mes[1] == '17':
            client_join(recv_mes[3])


t = threading.Thread(target=rec)
t.start()

# 创建发送按钮
send_button = tkinter.Button(root, text='发送', command=send)
send_button.place(x=310, y=285, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息

root.mainloop()

s.close()
