#!/usr/bin/python3

from tkinter import *
from tkinter import simpledialog
from tkinter import Frame
from twython import Twython
from twython import Twython, TwythonError
import threading
import time
import datetime
import json



class Window(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self):

        self.master = Tk()
        self.master.geometry("500x500")
        self.language = StringVar()
        self.language.set("en")
        self.number = 20
        self.hashtag = '#python'
        self.radio_button = True
        self.conv_dic = {}
        self.result = []

        # parameters that you want to send through the Frame class. 
        Frame.__init__(self, self.master)   


        #with that, we want to then run init_window, which doesn't yet exist
        self.init_window()


        #Creates text in the window with a scrollbar wich can be edited .
        self.S = Scrollbar(self.master)
        self.T = Text(self.master, height=20)
        self.S.pack(side=RIGHT,fill=Y)
        self.T.pack(side=LEFT, fill=Y)
        self.S.config(command=self.T.yview)
        self.T.config(yscrollcommand=self.S.set)


    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget      
        self.master.title("GUI")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a menu instance
        menu = Menu(self.master)
        self.master.config(menu=menu)

        # create the file object)

        menu_file = Menu(menu)
        menu.add_cascade(menu=menu_file, label='File')



        menu_widgets = Menu(menu)
        menu.add_cascade(menu=menu_widgets, label='widgets')
        menu_widgets.add_command(label='Language',command=self.change_lang)
        menu_widgets.add_command(label='Hash tag',command=self.change_hashtag)
        menu_widgets.add_command(label='Count',command=self.change_count)

        menu_edit = Menu(menu)
        menu.add_cascade(menu=menu_edit, label='credentials')
        menu_edit.add_command(label='Reset', command=self.reset)
        menu_edit.add_command(label='Change', command=self.newcredentials)
        #Adds command buttons to the File button.
        #menu_file.add_command(label='New submission', command=newsub)
        Button(self.master, text="Load tweets", width=20, command=self.tplay).pack()
        menu_file.add_command(label='Exit', command=self.master.quit)

#        menu_widgets.add_command(label='Load comments', command=load_comments)

                #Adds a seperator between menufiles.
        menu_file.add_separator()


    def newcredentials(self):
        x = []
        x.append(simpledialog.askstring("Input","What is the consumerkey"))
        x.append(simpledialog.askstring("Input","What is the consumersecret"))
        x.append(simpledialog.askstring("Input","What is the authkey"))
        x.append(simpledialog.askstring("Input","What is the authsecret"))
        y = open('credentials.txt', 'w')
        for i in x:
            y.write(i + '\n')


    def reset(self):
        x = open('backup.txt', 'r')
        y = open('credentials.txt', 'w')
        for line in x:
            print(line)
            y.write(line)

    def run(self):
        self.master.mainloop()

    def change_lang(self):
        if self.radio_button:
            languages = [("English", "en"),
            			("Deutsch", "de"),
            			("Nederlands", "nl")]

            for text,mode in languages:
                b = Radiobutton(self.master, text=text,
                    value=mode, variable=self.language)
                b.pack()
                self.language.set(mode)
            self.radio_button = False


            
    def change_hashtag(self):
        self.hashtag= str(simpledialog.askstring("Input","With what hash tag do you want to search"))


    def change_count(self):
        try:
            self.number= simpledialog.askinteger("Input","How many tweets?")
        except:
            print("Please fill in an integer. Not a string.")


    def stream_twitter(self):

        count = 0
        count2 = 0
        conversation = []

        credentials = open("credentials.txt", "r")
        for line in credentials:
            line = line.strip()

            if count == 0:
                consumer_key = line

            elif count == 1:
                consumer_secret = line

            elif count == 2:
                acces_token = line

            else:
                token_secret = line
            
            count += 1
        credentials.close()


        try:
            twitter = Twython(consumer_key, consumer_secret)

            results = twitter.search(count=self.number,lang=self.language.get(),q=self.hashtag)
            all_tweets = results['statuses']

            for tweet in all_tweets:
                replies = self.get_replies(tweet, twitter, conversation)
                count2 += 1
                self.conv_dic[count2] = list(set(replies))
                replies[:] = []
        except TwythonError as e:
            if e.error_code == 401:
                print("Please check your credentials. The program was unable to authenticate you.")

    def get_replies(self, tweet, twitter, lst):
        parent_id = tweet['in_reply_to_status_id']

        if parent_id:
            child_user = tweet['user']
            child_name = child_user['screen_name']
            child_message = tweet['text'].strip("\n")
            child_time = tweet['created_at']
            child = (child_time, child_name, child_message)


            try:
                parent_tweet = twitter.show_status(id=parent_id)
                parent_message = parent_tweet['text'].strip("\n")

                parent_user = parent_tweet['user']
                parent_name = parent_user['screen_name']
                parent_time = parent_tweet['created_at']
                parent = (parent_time, parent_name, parent_message)

                lst.append((parent, child))
                self.get_replies(parent_tweet, twitter, lst)
                


            except TwythonError as e:
                if e.error_code == 403:
                    print("You are not allowed to see these tweets.\n")
                elif e.error_code == 404:
                    print("This tweet does not longer exsist.\n")
                elif e.error_code == 429:
                    print("Your request limit has exceeded.")
                else:
                    print(e)
        return lst

    def print_result(self):

        for tweet_conv in self.result:
            
            tweet_conv.sort(key=lambda x:x["Timestamp"])
                

            prev_message = ""            

            #if len(tweet_conv) > 2 and len(tweet_conv) < 11:
            self.T.insert(END, "{0} {1}". format(42*"-", "Beginning of conversation\n"))
            conv_file = open(str(self.hashtag) + '.txt','w')
            

            for tweet_dic in tweet_conv:

                
                tup = tweet_dic["Message_tup"]

                
                self.T.insert(END, "{0}\n{1}: {2:20} \n\n".format(tup[0], tup[1], tup[2]))
            self.T.insert(END, "{0} {1}". format(47*"-", "End of conversation\n"))

            conv_file.write(json.dumps(tweet_conv))
            conv_file.close()
    print("done")

    def tplay(self):
        self.T.delete(1.0,END)
        self.result.clear()
        
        repl_lst =[]
        conversations = ""

        self.stream_twitter()

        try:
            for val in self.conv_dic.values():

                for pc_tup in val:

                    p_tup = pc_tup[0]
                    c_tup = pc_tup[1]

                    time_parent = p_tup[0]
                    time_child = c_tup[0]

                    timestamp_p = datetime.datetime.strptime(time_parent, '%a %b %d %H:%M:%S +0000 %Y').timestamp()
                    timestamp_c = datetime.datetime.strptime(time_child, '%a %b %d %H:%M:%S +0000 %Y').timestamp()

                    repl_lst.append({"Timestamp" : timestamp_p, "Message_tup" : p_tup})
                    repl_lst.append({"Timestamp" : timestamp_c, "Message_tup" : c_tup})
            
                #result = repl_lst
                repl_lst =   [dict(tupleized) for tupleized in set(tuple(item.items()) for item in repl_lst)]
                if repl_lst != []:
                    self.result.append(list(repl_lst))
                repl_lst[:] = []


        except:
            print("No conversations were found.")

        self.print_result()



#creation of an instance
app = Window()
app.run()