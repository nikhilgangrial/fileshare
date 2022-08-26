import kivy
import socket, os, sys
from threading import Thread, Timer
from time import sleep
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import ObjectProperty, StringProperty


PORT = 5080
BUFFER_SIZE = 4096
SEPARATOR = ">SEPARATOR<"
_popup = clent = client_soc = None
filenames = []

if sys.platform == 'win32':
    drives = [ chr(x) + ":" for x in range(65,90) if os.path.exists(chr(x) + ":") ]
    

def convert(size):
    unit = 'B'
    if size >= 1024:
        size = round(size/1024, 2)
        unit = ' KB'
    if size >= 1024:
        size = round(size/1024, 2)
        unit = ' MB'
    if size >= 1024:
        size = round(size/1024, 2)
        unit = ' GB'
    if size >= 1024:
        size = round(size/1024, 2)
        unit = ' TB'
    return str(size) + unit

def convert_time(time_left):
    try:
        if time_left[0] >= 60:
            time_left = [time_left[0]//60, str(time_left[0]%60)+'sec']
        else:
            time_left[0] = str(time_left[0]) + 'sec'
    except:
        pass
    
    try:   
        if time_left[0] >= 60:
            time_left = [time_left[0]//60, str(time_left[0]%60)+'min']
        else:
            time_left[0] = str(time_left[0]) + 'min'
    except:
        pass

    try:
        if time_left[0] >= 24:
            time_left = [str(time_left[0]//24)+'days', str(time_left[0]%24)+'hrs']
        else:
            time_left[0] = str(time_left[0]) + 'hrs'
    except:
        pass

    return ' '.join(time_left)


class FILECHOOSER(FloatLayout):

    
    path_ = StringProperty()
    fc = ObjectProperty()
    parent_ = ObjectProperty()
    dirs = ObjectProperty()



    def add_labels(self):
        
        def update_path(x):
            path = x.text
            self.fc.path = f"{path}\\"
            
            
        for i in drives:
            self.dirs.add_widget(Button(text=f"{i}\\", on_press=lambda x: update_path(x)))

            

    def load(self, path, filename):
        global filenames

        filenames = []
        for i in filename:
            filenames.append(os.path.join(path, i))
        
        if len(filenames)>1:
            del filenames[0]

        _popup.dismiss()
        main_back.remove_widget(self.parent_)
        temp = SENDER()
        main_back.add_widget(temp)


    def cancel(self):
        global drives

        if sys.platform == 'win32':
            drives = [ chr(x) + ":" for x in range(65,90) if os.path.exists(chr(x) + ":") ]
        
        _popup.dismiss()

    
class HOME(FloatLayout):

    def clicked_rec(self):
        main_back.remove_widget(self)
        temp = RECEIVER(ip=socket.gethostbyname(socket.gethostname()))
        temp.runserver()
        main_back.add_widget(temp)

    def clicked_sen(self):
        global _popup
        
        content = FILECHOOSER(parent_=self, path_=f"{drives[0]}\\")
        content.add_labels()
        _popup = Popup(title="Load files", content=content,
                            size_hint=(0.9, 0.9))
        _popup.open()



class RECEIVER(FloatLayout):

    ip = StringProperty()
    lab = ObjectProperty()
    wait = ObjectProperty()
    
    def runserver(self):

        self.iscancel = False

        self.server = socket.socket()
        self.server.bind((self.ip, PORT))
        self.server.listen(5)
        self.server.settimeout(60)

        waiter=Thread(target=self.wait_for_con)
        waiter.start()
        
        def change():
            while waiter.is_alive():
                sleep(0.3)
                self.wait.text = "Waiting for Sender.."
                sleep(0.3)
                self.wait.text = "Waiting for Sender..."
        Thread(target=change).start()

    def wait_for_con(self):

        #try:
        global client_soc
        
        client_soc, ip = self.server.accept()
        main_back.remove_widget(self)
        content = RECEIVING()
        main_back.add_widget(content)
        content.main_run()
        """  
        except:
            if not self.iscancel:
                self.lab.text = '\nRetry'

                def but_press(touch):
                    main_back.remove_widget(self)
                    self.server.close()
                    temp = RECEIVER(ip=socket.gethostbyname(socket.gethostname()))
                    temp.runserver()
                    main_back.add_widget(temp)

                butt = Button(background_normal='bck_n.png', on_press=but_press, size_hint=(0.1,0.1), pos_hint={'x':0.45, 'y':0.55})
                #retry button
                #cancel color
                #send
                #receive
                self.add_widget(butt)
                              
            else:
                self.iscancel = False
            return
    """
    def pressed_cancel(self):
        self.cancel = True
        self.server.close()
        main_back.remove_widget(self)
        main_back.add_widget(HOME())
        


class RECEIVING(FloatLayout):
    table = ObjectProperty()
    rec = ObjectProperty()
    rate = ObjectProperty()
    recei = ObjectProperty()
    pb = ObjectProperty()
    time = ObjectProperty()

    
    def setup_rec(self):
        global filenames
        
        size = int((client_soc.recv(BUFFER_SIZE).decode()).split(SEPARATOR)[0])
        
        received = client_soc.recv(size).decode()
        filenames, filesizes, paths  = received.split(SEPARATOR)

        print(filesizes)
        filenames = eval(filenames)
        self.filesizes = eval(filesizes)
        paths = eval(paths)

        def arr_path(main, prev_m='', prev='received\\', level = None):
            paths = {}
            for j in main:
                i = j
                    
                if not level:
                    i = os.path.basename(j)

                if not os.path.isdir(prev):
                    os.mkdir(prev)
                    
                if main[j] == {}:
                    if not os.path.isdir(prev+i):
                        os.mkdir(prev + i)
                    
                elif main[j] == None:
                    paths.update({prev_m + j: prev})

                else:
                    paths.update(arr_path(main[j], prev_m=prev_m+j+'\\', prev=prev+i+'\\', level=1))
                    

            return paths

        self.paths = arr_path(paths)
        
        self.sum_total = sum(self.filesizes)
        self.totaldata = convert(self.sum_total)

        rows = len(filenames)
        self.table.size_hint_y =  0.1*rows
        self.table.rows = rows+1
        self.table.cols = 4

        self.table.add_widget(Button(text='File Name'))
        self.table.add_widget(Button(text='Received'))
        self.table.add_widget(Button(text='Total'))
        self.table.add_widget(Button(text='Status'))

        self.status = []
        self.file_rec = []
        for i in range(rows):
            name = Label(text=os.path.basename(filenames[i]))
            self.table.add_widget(name)
            
            rec_ = Label(text='0b')
            self.table.add_widget(rec_)
            self.file_rec.append(rec_)

            size_ = Label(text=convert(self.filesizes[i]))
            self.table.add_widget(size_)

            prog_ = ProgressBar(max=100, value=0)
            self.table.add_widget(prog_)
            self.status.append(prog_)
        
        

    def main_rec(self):

        for i in range(len(filenames)):

            self.index = i
            path = self.paths[filenames[i]]
            filename = os.path.basename(filenames[i])
            self.filesize = self.filesizes[i]

            carry = b''
            with open(f"{path}{filename}", "wb") as f:
                
                self.cur_f=0
                f.write(carry)
                self.cur_f=len(carry)
                carry = b''
                while 1:
                       
                    bytes_read = client_soc.recv(BUFFER_SIZE)
                    count = len(bytes_read)
                    
                    if not bytes_read:
                        break
                    
                    self.cur_f += count

                    if self.cur_f >= self.filesize or self.cur_f/self.filesize >= 1:
                        extra = self.cur_f - self.filesize
                        f.write(bytes_read[:len(bytes_read)-extra])
                        carry = bytes_read[len(bytes_read)-extra:]
                        break

                    f.write(bytes_read)
   
            
            self.total_rec += self.cur_f
            self.file_rec[i].text = convert(self.filesize)
            self.status[i].value = 100
        

    def rec_updater(self):

        if self.total_rec/self.sum_total == 1:
            return

        received_till = self.cur_f + self.total_rec
        self.turn += 1

        self.pb.value = (received_till*100)//self.sum_total
        
        change = -(self.prev_red + self.curp_red - self.total_rec - self.cur_f)
                
        rate = change/0.5
        data_rate = convert(rate)#data
        self.rate.text = f"{data_rate}ps"
        
        
        overall_rate = (received_till)/(0.5*self.turn)
        if overall_rate >0:
            time_left = convert_time([int((self.sum_total-received_till) / overall_rate)])#time
        
            self.time.text = time_left
            self.recei.text = f"{convert(received_till)}/ {self.totaldata}"

        if self.turn%2 == 0:
            self.rec.text = "Sending Data .."
        else:
            self.rec.text = "Sending Data ..."

        self.file_rec[self.index].text = convert(self.cur_f)
        
        cur_percent = self.cur_f*100 //self.filesize
        self.status[self.index].value = cur_percent
        
        self.prev_red, self.curp_red  = self.total_rec, self.cur_f
        

    def main_run(self):
        
        self.setup_rec()

        main = Thread(target=self.main_rec)
        main.start()

        def updater():
            self.prev_red = self.curp_red = self.turn = self.total_rec = self.cur_f = self.index = 0
            self.filesize=self.filesizes[0]
            
            while main.is_alive():
                sleep(0.5)
                Thread(target=self.rec_updater).start()

        Thread(target=updater).start()
    

    
class SENDER(FloatLayout):

    ip = ObjectProperty()

    def pressed_cancel(self):
        main_back.remove_widget(self)
        main_back.add_widget(HOME())
        

    def pressed_connect(self):
        global client
        
        client = socket.socket()
        HOST = self.ip.text


        try:
            client.connect((HOST, PORT))
           
        except:
            client.close()
            self.ip.text = ''
            return

        main_back.remove_widget(self)
        content = SENDING()
        main_back.add_widget(content)
        content.main_run()
        

class SENDING(FloatLayout):

    table = ObjectProperty()
    sen = ObjectProperty()
    rate = ObjectProperty()
    sent = ObjectProperty()
    pb = ObjectProperty()
    

    def mk_zip(self, file):


        if os.path.isdir(file):
            global filenames
            
            files = os.listdir(file)
            
            pattern = {}
            for file_ in files:
                if os.path.isdir(file + '\\' + file_):
                    pattern[file_] = self.mk_zip(file + '\\' + file_) 
                else:
                    filenames.append(file + '\\' + file_)
                    pattern[file_] = None

            return pattern
        
        return
            
                        
        
    def setup_sen(self):
        global filenames
        
        self.dirs = []
        filenames_ = filenames
        filenames = []
        self.pattern = {}
        for file in filenames_:
            self.pattern[file] = self.mk_zip(file)

        self.filesizes = list(map(os.path.getsize, filenames))
        
        rows = len(filenames)
        self.table.size_hint_y =  0.1*rows
        self.table.rows = rows+1
        self.table.cols = 4

        self.table.add_widget(Button(text='File Name'))
        self.table.add_widget(Button(text='Sent'))
        self.table.add_widget(Button(text='Total'))
        self.table.add_widget(Button(text='Status'))

        self.status = []
        self.total_sent = []
        for i in range(rows):
            name = Label(text=os.path.basename(filenames[i]))
            self.table.add_widget(name)
            
            sent_ = Label(text='0b')
            self.table.add_widget(sent_)
            self.total_sent.append(sent_)

            size_ = Label(text=convert(self.filesizes[i]))
            self.table.add_widget(size_)

            prog_ = ProgressBar(max=100, value=0)
            self.table.add_widget(prog_)
            self.status.append(prog_)
        
        

    def main_sen(self):
        
        size = str(len(f"{filenames}{SEPARATOR}{self.filesizes}{SEPARATOR}{self.pattern}".encode()))
        size = (f"{size}{SEPARATOR}" + "5"*(4096 - len(f"{size}{SEPARATOR}"))).encode()
        client.send(size)
        client.send(f"{filenames}{SEPARATOR}{self.filesizes}{SEPARATOR}{self.pattern}".encode())
        
        self.sum_total = sum(self.filesizes)
        self.totaldata = convert(self.sum_total)
            

        for i in range(len(filenames)):

            self.index = i
            filename = filenames[i]
            self.filesize = self.filesizes[i]
            
            with open(filename, "rb") as f:
                
                self.cur_f=0
                while 1:

                    bytes_read = f.read(BUFFER_SIZE)
                    count = len(bytes_read)
                    
                    if not bytes_read:
                        break
                    
                    self.cur_f += count
                    client.sendall(bytes_read)
   

            self.total_sen += self.cur_f
            self.total_sent[i].text = convert(self.filesize)
            self.status[i].value = 100
        

    def sen_updater(self):

        if self.total_sen/self.sum_total == 1:
            return

        received_till = self.total_sen + self.cur_f
        self.turn += 1

        self.pb.value = (received_till*100)//self.sum_total
        
        change = -(self.prev_red + self.curp_red - self.total_sen - self.cur_f)
                
        rate = change/0.5
        data_rate = convert(rate)#data
        self.rate.text = f"{data_rate}ps"
        
        
        overall_rate = (received_till)/(0.5*self.turn)
        if overall_rate >0:
            time_left = convert_time([int((self.sum_total-received_till) / overall_rate)])#time
        
            self.time.text = time_left
            self.sent.text = f"{convert(received_till)}/ {self.totaldata}"

        if self.turn%2 == 0:
            self.sen.text = "Sending Data .."
        else:
            self.sen.text = "Sending Data ..."

        self.total_sent[self.index].text = convert(self.cur_f)
        
        cur_percent = self.cur_f*100 //self.filesize
        self.status[self.index].value = cur_percent
        
        self.prev_red, self.curp_red  = self.total_sen, self.cur_f
        

    def main_run(self):
        
        self.setup_sen()

        main = Thread(target=self.main_sen)
        main.start()

        def updater():
            self.prev_red = self.curp_red = self.turn = self.total_sen = self.cur_f = self.index = 0
            self.filesize=self.filesizes[0]
            self.sum_total = 1
            
            while main.is_alive():
                sleep(0.5)
                Thread(target=self.sen_updater).start()

        Thread(target=updater).start()

                    

            


def main():
    global main_back
    
    main_back = BoxLayout()
    main_back.add_widget(HOME())
    return main_back



class FileShareApp(App):
    use_kivy_settings = False

    def build(self):
        self.title = 'FileShare'
        return main()


if __name__ == '__main__':
    FileShareApp().run()
    
