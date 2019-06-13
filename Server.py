import socket
import threading
import tkinter
import tkinter.messagebox

# 服务器
Ip = '127.0.0.1'
Port = 50007
ServerAddr = (Ip, Port)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(ServerAddr)

Channel = '0'     # 表示不在任何一个聊天室
UserId = '0'      # 表示还未进入聊天室，没有username
UserName = 'server'


Rooms = []  # 聊天室 [[room_name,[UserName, UserId, Addr],...]
# [room_name,users,users,...]
# 用于存放在线用户的信息  [username, userid, addr]

# 聊天窗口
# 创建图形界面
Root = tkinter.Tk()
Root.title('server')  # 窗口命名为用户名
Root['height'] = 380
Root['width'] = 600

# 创建多行文本框
ListBox = tkinter.Listbox(Root)
ListBox.place(x=130, y=0, width=300, height=300)

# 创建输入文本框和关联变量
msg = tkinter.StringVar()
msg.set('')
entry = tkinter.Entry(Root, width=120, textvariable=msg)
entry.place(x=130, y=310, width=230, height=50)

# 滚动条
scrollbar = tkinter.Scrollbar(ListBox, command=ListBox.yview)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
ListBox.config(yscrollcommand=scrollbar.set)

# new channel输入框
new_channel = tkinter.StringVar()
new_channel.set('')
new_channel_entry = tkinter.Entry(Root, textvariable=new_channel)
new_channel_entry.place(x=50, y=310, width=75, height=20)

# online users
online_user_list = tkinter.Listbox(Root)
online_user_list.place(x=430, y=0, width=170, height=300)


# init online user
def init_online_user():
    online_user_list.delete(0, tkinter.END)
    online_user_list.insert(tkinter.END, "----------Online Users--------")
    online_user_list.itemconfig(tkinter.END, fg='blue')


init_online_user()


# 更新自己的users列表
def update_users(u):
    init_online_user()
    para = u.split(' ')
    for item in para:
        online_user_list.insert(tkinter.END, item)


# 更新用户的user列表
# i表示channel index
def client_update_online_users(i):
    # 把更新后的用户列表发给channel里每一个人
    m = "server 0:20:0:"
    for j in range(1, len(Rooms[i])):
        m = m + Rooms[i][j][1] + " "
    for j in range(1, len(Rooms[i])):
        s.sendto(m.encode(), Rooms[i][j][2])


# channel list
channel_list = tkinter.Listbox(Root)
channel_list.place(x=0, y=0, width=130, height=300)


# 初始化channel list
def init_channel_list():
    channel_list.delete(0, tkinter.END)
    channel_list.insert(tkinter.END, "-------Channels-------")
    channel_list.itemconfig(tkinter.END, fg='blue')


init_channel_list()


# server 离开房间初始化
def init():
    global Channel, UserId
    Channel = '0'
    UserId = '0'
    # 清空用户列表
    init_online_user()
    # 清空文本框
    ListBox.delete(0, tkinter.END)
    # 标题
    Root.title('server')

# enter channel
# 处理自己
# 给其他用户发送消息
# 必须先离开当前channel，才能进入下一个channel
def enter(event):
    global UserId, Channel
    me = channel_list.get(channel_list.curselection())
    if Channel == '0':
        Channel = me
        #  title改成channel名称
        Root.title(channel_list.get(channel_list.curselection()))
        for i in range(len(Rooms)):
            if Rooms[i][0] == me:
                user_id = UserName + '-' + str(len(Rooms[i]))
                UserId = user_id
                Rooms[i].append(['server', user_id, ServerAddr])
                tkinter.messagebox.showinfo(title="Reminder", message="You now in "+me)
                # enter之后把用户列表发给每一个人
                client_update_online_users(i)
                break
    else:
        tkinter.messagebox.showerror(title="ERROR", message="You have to leave this room first!")


channel_list.bind('<Double-Button>', enter)


# 提醒用户，有人离开了房间
# 22
# i index of channel u userid
def client_sb_leave(i, u):
    data = "server 0:22:0:" + u
    for j in range(1, len(Rooms[i])):
        s.sendto(data.encode(), Rooms[i][j][2])


# kick out userid
# 21
def kickout(event):
    dstId = online_user_list.get(online_user_list.curselection())
    if dstId == UserId:
        tkinter.messagebox.showinfo(title="Reminder", message="You cannot kick out yourself")
    else:
        for i in range(len(Rooms)):
            if Rooms[i][0] == Channel:
                for j in range(1, len(Rooms[i])):
                    if Rooms[i][j][1] == dstId:
                        data = "server 0:21:0:"
                        s.sendto(data.encode(), Rooms[i][j][2])
                        del (Rooms[i][j])
                        tkinter.messagebox.showinfo(title="Reminder", message="You kick out " + dstId)
                        break
                # 更新用户列表
                # 20
                client_update_online_users(i)
                # 发送给每个其他的用户，该用户已经离开，
                # 22
                client_sb_leave(i, dstId)
                break


online_user_list.bind('<Double-Button>', kickout)


# 更新channel list,给每个用户发送channel
# 只有在开通channel和关闭channel时需要update
def update_channels():
    init_channel_list()
    m = "server 0:19:0:"
    for i in range(len(Rooms)):
        m = m + Rooms[i][0] + ' '  # 计算要发送的channel
        channel_list.insert(tkinter.END, Rooms[i][0])  # 更新自己列表
    for i in range(len(Rooms)):
        for j in range(1, len(Rooms[i])):
            s.sendto(m.encode(), Rooms[i][j][2])  # 给每个用户更新channel信息


# button open channel
# 检查是否有重名的channel
def open_channel():
    channelname = new_channel_entry.get()
    new_channel.set('')  # 清空
    if channelname == "":
        tkinter.messagebox.showinfo(title="Reminder", message="Please input channel name")
    else:
        flag = 0
        for i in range(len(Rooms)):
            if Rooms[i][0] == channelname:
                tkinter.messagebox.showerror(title="ERROR", message="This room already exists!")
                flag = 1
                break
        if flag == 0:
            room = [channelname]
            Rooms.append(room)
            update_channels()


# open channel
open_channel_butt = tkinter.Button(Root, text='New', command=open_channel)
open_channel_butt.place(x=5, y=310, width=40, height=20)




# leave channel
def leave():
    global Channel, UserId
    if Channel == '0':
        tkinter.messagebox.showinfo(title="Reminder", message="You are not in any channel")
    else:
        for i in range(len(Rooms)):
            if Rooms[i][0] == Channel:
                # 自己退出
                for j in range(1, len(Rooms[i])):
                    if Rooms[i][j][2] == ServerAddr:
                        del (Rooms[i][j])
                        tkinter.messagebox.showinfo(title="Reminder", message="You leave " + Channel)
                        break
                client_sb_leave(i, UserId)
                client_update_online_users(i)
                break
        init()


leave_channel_butt = tkinter.Button(Root, text='Leave', command=leave)
leave_channel_butt.place(x=65, y=340, width=50, height=20)


# close channel
# 一定要选中
def close():
    dstCh = channel_list.get(channel_list.curselection())
    if dstCh == Channel:
        tkinter.messagebox.showerror(title="error", message="You should leave first!")
    else:
        for i in range(len(Rooms)):
            if Rooms[i][0] == dstCh:
                m = "server 0:23:0:"
                for j in range(1, len(Rooms[i])):
                    s.sendto(m.encode(), Rooms[i][j][2])
                del (Rooms[i])
                break
        # server反应
        tkinter.messagebox.showinfo(title="Reminder", message="You closed " + dstCh)
        update_channels()


close_channal_butt = tkinter.Button(Root, text='Close', command=close)
close_channal_butt.place(x=5, y=340, width=50, height=20)


# server 处理转发message
def transmit_message(user, channel, sender_data):
    user_info = user.split(' ', 1)
    user_id = user_info[1]
    user_name = user_info[0]
    m = user_name + ' ' + user_id + ':15:' + channel + ':' + sender_data
    for i in range(len(Rooms)):
        if Rooms[i][0] == channel:
            for j in range(1, len(Rooms[i])):
                s.sendto(m.encode(), Rooms[i][j][2])


# 表示要显示在屏幕上的
def message(user, recv_data):
    user_info = user.split(' ', 1)
    user_id = user_info[1]
    m = 'From ' + user_id + ' :' + recv_data
    ListBox.insert(tkinter.END, m)


# 发送当前channel
def client_channels(recv_data):
    if len(Rooms) == 0:
        m = "server 0:19:0:"
    else:
        m = "server 0:19:0:"
        for i in range(len(Rooms)):
            m = m + Rooms[i][0] + ' '
    s.sendto(m.encode(), recv_data)


def client_join(addr, parameters):
    user_info = parameters.split(' ', 1)
    user_name = user_info[1]
    channel_name = user_info[0]
    for i in range(len(Rooms)):
        if Rooms[i][0] == channel_name:
            # 请求对象更新状态，回复userid
            user_id = user_name+'-'+str(len(Rooms[i]))
            Rooms[i].append([user_name, user_id, addr])
            m = "server 0:17:0:"+user_name+' '+user_id+' '+channel_name
            s.sendto(m.encode(), addr)
            # join 之后把用户列表发给所有用户
            # channel更新
            # 更新用户的channel 列表
            # 这里是防止用户在请求channel之后还未加入channel
            # server又新开了几个channel
            # 加入之后可以马上更新
            client_update_online_users(i)
            update_channels()
            break


# 处理转发private msg
def client_msg(sender_info, channel_name, parameters):
    para = parameters.split(' ', 1)
    recv_id = para[0]
    recv_addr = []
    m = para[1]
    for i in range(len(Rooms)):
        if Rooms[i][0] == channel_name:
            for j in range(1, len(Rooms[i])):
                if Rooms[i][j][1] == recv_id:
                    recv_addr = Rooms[i][j][2]
                    break
            break
    m = sender_info + ':18:' + channel_name + ":(private) " + m
    s.sendto(m.encode(), recv_addr)


# 同意user离开的回复
def client_leave(addr, user, channel_name):
    client = user.split(' ', 1)
    user_id = client[1]
    for i in range(len(Rooms)):
        if Rooms[i][0] == channel_name:
            for j in range(1, len(Rooms[i])):
                if Rooms[i][j][1] == user_id:
                    del (Rooms[i][j])
                    m = 'server 0:16:0:'
                    s.sendto(m.encode(), addr)
                    break
            # 发送给每个其他的用户，该用户已经离开，并且要更新用户列表
            client_sb_leave(i, user_id)
            client_update_online_users(i)
            break


def sb_leave(u):
    tkinter.messagebox.showinfo(title="Attention", message=u + " has left!")


# 接收
def rec():
    # 解析协议
    while True:
        data, r_addr = s.recvfrom(512)
        data = data.decode()
        recv_mes = data.split(':', 3)
        if recv_mes[1] == '08':
            # [addr, username user_id, channel, parameters]
            transmit_message(recv_mes[0], recv_mes[2], recv_mes[3])
        elif recv_mes[1] == '09':
            client_channels(r_addr)
        elif recv_mes[1] == '10':
            # [addr, parameters]
            client_join(r_addr, recv_mes[3])
        elif recv_mes[1] == '12':
            client_msg(recv_mes[0], recv_mes[2], recv_mes[3])
        elif recv_mes[1] == '13':
            client_leave(r_addr, recv_mes[0],recv_mes[2])
        elif recv_mes[1] == '15':
            message(recv_mes[0], recv_mes[3])
        elif recv_mes[1] == '20':
            update_users(recv_mes[3])
        elif recv_mes[1] == '22':
            sb_leave(recv_mes[3])


t = threading.Thread(target=rec)
t.start()


# 发送
# 当前不在任何一个聊天室内
def send(event=0):
    # 应用层协议格式
    # parameter_number
    # command type
    # sender_channel
    # parameters
    # msg(if any)
    if Channel == '0':
        tkinter.messagebox.showinfo(title="Reminder", message="Please join in any channel first")
    else:
        m = entry.get()
        m = 'server' + ' ' + UserId + ':08:' + Channel + ':' + m
        s.sendto(m.encode(), ServerAddr)
        msg.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(Root, text='发送', command=send)
button.place(x=370, y=310, width=60, height=50)
Root.bind('<Return>', send)  # 绑定回车发送信息
Root.mainloop()

# 结束，切断
s.close()
