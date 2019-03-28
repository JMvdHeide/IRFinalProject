# Elvira Slaghekke s3209695
# Myrthe Lammerse s2772841

import tkinter as tk
from tkinter import ttk
import re
import threading
from queue import Queue
from tkinter import filedialog
import ast
import tweepy
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# This code can be found at http://stackoverflow.com/a/13752628/6762004
# It is used to remove any emojis in the tweetsself.
RE_EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
def strip_emoji(text):
    return RE_EMOJI.sub(r'', text)

# Those variables contain the credentials to access the Twitter API
with open('credentials.txt') as credentials:
    tokens = [line.strip('\n') for line in credentials]

access_token = tokens[0]
access_token_secret = tokens[1]
oauth_token = tokens[2]
oauth_token_secret = tokens[3]

auth = tweepy.OAuthHandler(oauth_token, oauth_token_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit_notify=True)

# the frame classes
class Frame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)

        self.myqueue = Queue()

        # Menubar:
        self.menubar = tk.Menu(self.master)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.filemenu.add_command(label="Open", command=self.openfile)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.master.config(menu=self.menubar)

        self.content = tk.Frame(parent)
        self.filters = tk.Frame(parent)

        self.text=tk.Text(self.content,height=49)

        # the scrollbar code is reproduced from https://stackoverflow.com/questions/16188420/python-tkinter-scrollbar-for-frame/16198198#16198198
        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        self.label = tk.Label(self.filters, text="Min. number of participants:").grid(column=3, row=2, sticky='w')
        self.label = tk.Label(self.filters, text="Max. number of participants:").grid(column=3, row=3, sticky='w')
        self.label = tk.Label(self.filters, text="Min. length of conversation:").grid(column=3, row=5, sticky='w')
        self.label = tk.Label(self.filters, text="Max. length of conversation:").grid(column=3, row=6, sticky='w')
        self.label = tk.Label(self.filters, text="Sentiment:").grid(column=3, row=8, sticky='w')
        self.button = tk.Button(self.filters, text="Update",  command=self.start).grid(column=3,row=10)

        self.minlength = tk.Entry(self.filters, width=8)
        self.minlength.insert(0, "0")
        self.maxlength = tk.Entry(self.filters, width=8)
        self.maxlength.insert(10, "10")

        self.minuser = tk.StringVar(self.filters)
        self.minuser.set("2")
        self.options = tk.OptionMenu(self.filters, self.minuser, "2","3","4","5","6","7","8","9","10")
        self.maxuser = tk.StringVar(self.filters)
        self.maxuser.set("10")
        self.options2 = tk.OptionMenu(self.filters, self.maxuser, "2","3","4","5","6","7","8","9","10")
        self.sentiment = tk.StringVar(self.filters)
        self.sentiment.set("Undefined")
        self.options3 = tk.OptionMenu(self.filters, self.sentiment, "Undefined", "Positive", "Negative")

        self.content.grid(column=0, row=0)
        self.filters.grid(column=1, row=0, sticky='nesw')

        self.options.grid(column=4,row=2)
        self.options2.grid(column=4,row=3)
        self.options3.grid(column=4, row=8)

        self.minlength.grid(column=4,row=5)
        self.maxlength.grid(column=4,row=6)

        self.text.grid(column=0, row=0, columnspan=3, rowspan=2)

        self.tweets = []

        self.sid = SentimentIntensityAnalyzer()

        self.file = None

    def filterinput(self):
        try:
            if self.file == None:
                self.text.insert("end","Please open a working file via the open option in the filemenu.\n")
            else:
                minuser = self.minuser.get()
                maxuser = self.maxuser.get()
                minlength = self.minlength.get()
                maxlength = self.maxlength.get()
                sentiment = self.sentiment.get()

                conversation = 1
                for tweet_list in self.tweets:
                    if (len(tweet_list) - 1) >= int(minlength) and (len(tweet_list) - 1) <= int(maxlength) and tweet_list[-1] >= int(minuser) and tweet_list[-1] <= int(maxuser):
                        sentiment_of_list = self.sentimentfinder(tweet_list)
                        if sentiment_of_list == sentiment:
                            tweets.reverse()
                            self.filterdisplay(tweet_list[1:], conversationNo)
                            conversation +=1

                if conversationNo == 1:
                    self.text.insert("The filters do not return a conversation. Please try again.")

            self.filters.config(state='normal', text="Filter")
        except tk.TclError:
            pass



    def filterdisplay(self,tweet_list,conversation):
        self.text.insert("end","***CONVERSATION {0}***\n".format(conversation))
        count = 1
        for tweetID in tweet_list:
            try:
                tweetobj = api.get_status(tweetID)
                tweettext = strip_emoji(tweetobj.text)
                user = tweetobj.user.name
                try:
                    self.text.insert("end","*TWEET {0}* by {1}\n".format(count,user))
                except:
                    self.text.insert("end","*TWEET {0}* by undefined user\n".format(count))
                self.text.insert("end",tweettext)
                self.text.insert("end","\n")
                count += 1
            except:
                break
        self.text.insert("end","\n\n")


    def openfile(self):
        filepath = filedialog.askopenfilename(title="Choose a file.")

        self.file_handle = open(filepath, 'r')
        for line in self.file_handle:
            linelist = ast.literal_eval(line)
            self.tweets.append(linelist)

    def start(self):
        threading.Thread(target=self.filterinput, daemon=True).start()

    def quit(self):
        self.master.destroy()

    def sentimentfinder(self, list):
        oldsentiment = 0
        sentimentset = set()
        if len(lst) > 1:
            for tweetid in list:
                try:
                    tweetobject = api.get_status(tweetid)
                except:
                    break
                tweettext = tweetobject.text
                scores = self.sid.polarity_scores(tweettext)
                newsentiment = scores['compound']
                if oldsentiment > newsentiment:
                    sentimentset.add('Negative')
                elif newsentiment > oldsentiment:
                    sentimentset.add('Positive')
                else:
                    sentimentset.add('Undefined')
                oldsentiment = newsemtiment
            if len(sentimentset) == 1:
                return list(sentimentset)[0]

def main():
    root = tk.Tk()
    root.title('Coursework 3 - Part 2')
    root.geometry('1000x750')
    frame = Frame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
