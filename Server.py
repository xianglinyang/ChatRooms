import socket
import threading
import tkinter

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
Root['height'] = 330
Root['width'] = 450

# 创建多行文本框
ListBox = tkinter.Listbox(Root, width=300)
ListBox.place(x=5, y=0, width=440, height=280)

# 滚动条
scrollbar = tkinter.Scrollbar(ListBox, command=ListBox.yview)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
ListBox.config(yscrollcommand=scrollbar.set)

# 创建输入文本框和关联变量
msg = tkinter.StringVar()
msg.set('')
entry = tkinter.Entry(Root, width=120, textvariable=msg)
entry.place(x=5, y=285, width=300, height=30)


# 接收
def rec():
    def server_open_channel(name):
        room = [name]
        Rooms.append(room)
        m = 'You have successfully created chat room: '+name
        ListBox.insert(tkinter.END, m)

    def server_channels():
        if len(Rooms) == 0:
            ListBox.insert(tkinter.END, "There are no rooms right now!")
        else:
            ListBox.insert(tkinter.END, "Now You have the following rooms:")
            for i in range(len(Rooms)):
                ListBox.insert(tkinter.END, Rooms[i][0])

    def server_enter_channel(channel_name):
        global Channel, UserName, UserId
        if Channel == '0':
            Channel = channel_name
            for i in range(len(Rooms)):
                if Rooms[i][0] == channel_name:
                    user_id = UserName+'-'+str(len(Rooms[i]))
                    UserId = user_id
                    Rooms[i].append(['server', user_id, ServerAddr])
                    ListBox.insert(tkinter.END, "You now in room: " + channel_name)
                    break
        else:
            ListBox.insert(tkinter.END, "You have to leave this room first!")

    def server_list():
        global Channel
        if Channel == '0':
            ListBox.insert(tkinter.END, "You are not in room !")
        else:
            for i in range(len(Rooms)):
                if Rooms[i][0] == Channel:
                    for j in range(1, len(Rooms[i])):
                        ListBox.insert(tkinter.END,
                                       Rooms[i][j][1] + " " + Rooms[i][j][2][0] + ' ' + str(Rooms[i][j][2][1]))
                    break

# 只能踢出user，不能踢出自己
    def server_kick_out(user_id):
        for i in range(len(Rooms)):
            if Rooms[i][0] == Channel:
                for j in range(1, len(Rooms[i])):
                    if Rooms[i][j][1] == user_id:
                        server_data = 'server 0:16:' + Channel + ':' + "You have been kick out from this room!"
                        s.sendto(server_data.encode(), Rooms[i][j][2])
                        del(Rooms[i][j])
                        server_data = 'server 0:15:' + Channel + ':' + user_id + " has been kick out!"
                        for k in range(1, len(Rooms[i])):
                            s.sendto(server_data.encode(), Rooms[i][k][2])
                        break
                break

# 这里要注意server发送出去的如果又被发回给server怎么办？
# 让server和client收到message的命令相同

    def server_leave():
        global Channel, UserId
        for i in range(len(Rooms)):
            if Rooms[i][0] == Channel:
                for j in range(1, len(Rooms[i])):
                    if Rooms[i][j][2] == ServerAddr:
                        del(Rooms[i][j])
                        m = "You leave the room : " + Channel
                        ListBox.insert(tkinter.END, m)
                        break
                server_data = 'server 0:15:' + Channel + ':' + UserId + " has left the room !"
                for k in range(1, len(Rooms[i])):
                    s.sendto(server_data.encode(), Rooms[i][k][2])
                break
        Channel = '0'
        UserId = '0'


# 前提是自己不在这个聊天室内
    def server_close_channel(channel_name):
        for i in range(len(Rooms)):
            if Rooms[i][0] == channel_name:
                m = "server 0:16:0:This channel has been closed by server !"
                for j in range(1, len(Rooms[i])):
                    s.sendto(m.encode(), Rooms[i][j][2])
                del(Rooms[i])
                break
        ListBox.insert(tkinter.END, "You closed room: "+channel_name)

# server 处理转发message
    def server_message(user, channel, sender_data):
        user_info = user.split(' ', 1)
        user_id = user_info[1]
        user_name = user_info[0]
        m = user_name + ' ' + user_id + ':15:' + channel + ':' + sender_data
        for i in range(len(Rooms)):
            if Rooms[i][0] == channel:
                for j in range(1, len(Rooms[i])):
                    s.sendto(m.encode(), Rooms[i][j][2])

# 表示要显示在屏幕上的
    def client_message(user, recv_data):
        user_info = user.split(' ', 1)
        user_id = user_info[1]
        m = 'From ' + user_id + ' :' + recv_data
        ListBox.insert(tkinter.END, m)

# channel分隔符 /
    def client_channels(recv_data):
        if len(Rooms) == 0:
            m = "server 0:15:0:There are no rooms right now!"
        else:
            m = "server 0:15:0:Rooms: "
            for i in range(len(Rooms)):
                m = m + Rooms[i][0] + ' '
        s.sendto(m.encode(), recv_data)

    def client_join(addr, parameters):
        user_info = parameters.split(' ', 1)
        user_name = user_info[1]
        channel_name = user_info[0]
        for i in range(len(Rooms)):
            if Rooms[i][0] == channel_name:
                user_id = user_name+'-'+str(len(Rooms[i]))
                Rooms[i].append([user_name, user_id, addr])
                m = "server 0:17:0:"+user_name+' '+user_id+' '+channel_name
                s.sendto(m.encode(), addr)
                break

# 分隔符 /
    def client_list(addr, channel_name):
        m = 'server 0:15:0:'
        for i in range(len(Rooms)):
            if Rooms[i][0] == channel_name:
                for j in range(1, len(Rooms[i])):
                    m = m + Rooms[i][j][1] + " "
                break
        s.sendto(m.encode(), addr)

    def client_msg(sender_info, channel_name, parameters):
        para = parameters.split(' ', 1)
        recv_id = para[0]
        m = para[1]
        for i in range(len(Rooms)):
            if Rooms[i][0] == channel_name:
                for j in range(1, len(Rooms[i])):
                    if Rooms[i][j][1] == recv_id:
                        recv_addr = Rooms[i][j][2]
                        break
                break
        message = sender_info + ':18:' + channel_name + ":(private) " + m
        s.sendto(message.encode(), recv_addr)

    def client_leave(addr, user, channel_name):
        client = user.split(' ', 1)
        user_id = client[1]
        for i in range(len(Rooms)):
            if Rooms[i][0] == channel_name:
                for j in range(1, len(Rooms[i])):
                    if Rooms[i][j][1] == user_id:
                        del (Rooms[i][j])
                        m = 'server 0:16:0:You left room:'+channel_name
                        s.sendto(m.encode(), addr)
                        break
                server_data = 'server 0:15:' + Channel + ':' + user_id + " has left the room !"
                for k in range(1, len(Rooms[i])):
                    s.sendto(server_data.encode(), Rooms[i][k][2])
                break

# 解析协议
    while True:
        data, r_addr = s.recvfrom(512)
        data = data.decode()
        recv_mes = data.split(':', 3)
        if recv_mes[1] == '01':
            server_open_channel(recv_mes[3])
        elif recv_mes[1] == '02':
            server_channels()
        elif recv_mes[1] == '03':
            server_enter_channel(recv_mes[3])
        elif recv_mes[1] == '04':
            server_list()
        elif recv_mes[1] == '05':
            server_kick_out(recv_mes[3])
        elif recv_mes[1] == '06':
            server_leave()
        elif recv_mes[1] == '07':
            server_close_channel(recv_mes[3])
        elif recv_mes[1] == '08':
            # [addr, username user_id, channel, parameters]
            server_message(recv_mes[0], recv_mes[2], recv_mes[3])
        elif recv_mes[1] == '09':
            client_channels(r_addr)
        elif recv_mes[1] == '10':
            # [addr, parameters]
            client_join(r_addr, recv_mes[3])
        elif recv_mes[1] == '11':
            # [user,command,channel,parameters]
            client_list(r_addr, recv_mes[2])
        elif recv_mes[1] == '12':
            client_msg(recv_mes[0], recv_mes[2], recv_mes[3])
        elif recv_mes[1] == '13':
            client_leave(r_addr, recv_mes[0],recv_mes[2])
        elif recv_mes[1] == '15':
            client_message(recv_mes[0], recv_mes[3])


t = threading.Thread(target=rec)
t.start()


# 发送
def send(event=0):
    m = entry.get()
    # 应用层协议格式
    # parameter_number
    # command type
    # sender_channel
    # parameters
    # msg(if any)

    mes = m.split(' ', 1)
    if mes[0] == '/openchannel':
        message = 'server' + ' ' + UserId + ':01:' + Channel + ':' + mes[1]
    elif mes[0] == '/channels':
        message = 'server' + ' ' + UserId + ':02:' + Channel
    elif mes[0] == '/enterchannel':
        message = 'server' + ' ' + UserId + ':03:' + Channel + ':' + mes[1]
    elif mes[0] == '/list':
        message = 'server' + ' ' + UserId + ':04:' + Channel
    elif mes[0] == '/kickout':
        message = 'server' + ' ' + UserId + ':05:' + Channel + ':' + mes[1]
    elif mes[0] == '/leave':
        message = 'server' + ' ' + UserId + ':06:' + Channel
    elif mes[0] == '/closechannel':
        message = 'server' + ' ' + UserId + ':07:' + Channel + ':' + mes[1]
    else:
        if len(mes) == 1:
            message = 'server' + ' ' + UserId + ':08:' + Channel + ':' + mes[0]
        else:
            message = 'server' + ' ' + UserId + ':08:' + Channel + ':' + mes[0] + ' ' + mes[1]
    s.sendto(message.encode(), ServerAddr)
    msg.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(Root, text='发送', command=send)
button.place(x=310, y=285, width=60, height=30)
Root.bind('<Return>', send)  # 绑定回车发送信息
Root.mainloop()

# 结束，切断
s.close()
