import PIL
import subprocess
import urllib.request
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt 

from PIL import Image
from PIL import ImageTk
from pexpect import pxssh
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
from pymongo import MongoClient
from bs4 import BeautifulSoup

client = MongoClient(port=27017)
db = client.Property_aggregator

country_list = ["Greece", "Italy", "United States"]
state_list = ["CA", "WA"]

class mainwindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #window settings
        self.title('Listing Aggregator')    #set title
        self.geometry("1000x800")         #set the size
        self.resizable(0, 0)              #fix the size

    

        #initial window setup
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for frame_option in (StatsFrame, RangeFrame):
            frame_name = frame_option.__name__
            
            frame = frame_option(parent=container, controller=self)
            
            self.frames[frame_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.display_frame("StatsFrame")

    def display_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()


class StatsFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config(background='grey')

        #frame label
        stats_frame_label = tk.Label(self,background='grey', text="Statistics")
        stats_frame_label.place(x=700, y=5)
        stats_frame_label.config(font=("Courier", 30))

        #tab buttons
        StatsButton1 = tk.Button(self, text="Stats",highlightbackground='grey', command=lambda: controller.display_frame("StatsFrame"))
        StatsButton1.config(height = 1, width = 8)
        StatsButton1.place(x = 1, y = 1)
        
        RangeButton1 = tk.Button(self, text="Range",highlightbackground='grey', command=lambda: controller.display_frame("RangeFrame"))
        RangeButton1.config(height = 1, width = 8)
        RangeButton1.place(x = 100, y = 1)



        def category_plot_button_action():

            url_check_string = range_query_input_1.get()#get the url that was entered



            #check it against the recognized urls 
            if url_check_string.startswith(("https://www.jamesedition.com/real_estate", "https://www.zillow.com/")) == True:
                return_val = subprocess.call(['./test_status.sh ' + url_check_string], shell=True)
                print(return_val)

                if (return_val == 0):
                    #success
                    #retrieving the listing from the web
                    subprocess.call(['./get_website.sh ' + url_check_string], shell=True)
                    soup = BeautifulSoup(open("/Users/richardmiller/Documents/website_file_storage/test_file.html"), "html.parser")

                    listing_dict = {}   #create the dictionary to hold all of the relevant info from the web page to push to the database

                    #retrieve name of listing
                    headline_retriever = soup.find('h1', attrs={"class":"headline"})#this tests and gets the headline name of the listing 
                    for string in headline_retriever.stripped_strings:
                        listing_name = string
                        listing_dict["Title"] = listing_name
                        #print(listing_name)
                        break

                    #retrieve price of listing
                    price_retriever = soup.find("div", attrs={"class":"price"})#this tests and gets the price of the listing 
                    for string in price_retriever.stripped_strings:
                        listing_price = string
                        listing_dict["Price"] = listing_price
                        #print(listing_price)
                        #break

                    #retrieving piece of the detail list
                    for li in soup.find('ul', {"class":"details-list"}).find_all("li"):
                        if (li.find('span', {"class":"name"}).getText(strip=True)) == "Location:":
                            listing_location_string = li.find('span', {"class":"value"}).getText(strip=True)
                            list_of_location_strings = listing_location_string.split(", ")
                            for location in list_of_location_strings:
                                if (location not in country_list and location not in state_list):
                                    location_city = location
                                    listing_dict["City"] = location_city
                                elif (location in state_list):
                                    location_state = location
                                    listing_dict["State"] = location_state
                                elif (location in country_list):
                                    location_country = location
                                    listing_dict["Country"] = location_country
                    
                    for x, y in listing_dict.items():
                        print(x, y)

                    subprocess.call(['./remove_website.sh'], shell=True)
  
                elif(return_val == 1):
                    #oops redirect
                    print("redirect 1")
                elif(return_val == 2):
                    #404 error
                    print("404 error 2")
            else:
                print("Not from approved website,error")#print off error
                #make this a display feature that shows if invalid
            
        range_query_input_1 = tk.Entry(self, width = 20)
        range_query_input_1.place(x = 300, y = 100)

        #Launch category plot label
        launch_category_plot_label = tk.Label(self, text="Run Script   ->")
        launch_category_plot_label.place(x = 575, y = 115)

        #category plot button
        category_plot_button = tk.Button(self, text="Script",  command=lambda: category_plot_button_action())    
        category_plot_button.config(height = 1, width = 8)
        category_plot_button.place(x = 750, y = 115)



class RangeFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config(background='grey')

        #frame label
        Range_frame_label = tk.Label(self,background='grey', text="Range Search")
        Range_frame_label.place(x=700, y=5)
        Range_frame_label.config(font=("Courier", 30))



        #tab buttons
        StatsButton2 = tk.Button(self, text="Stats",highlightbackground='grey', command=lambda: controller.display_frame("StatsFrame"))
        StatsButton2.config(height = 1, width = 8)
        StatsButton2.place(x = 1, y = 1)
        
        RangeButton2 = tk.Button(self, text="Range",highlightbackground='grey', command=lambda: controller.display_frame("RangeFrame"))
        RangeButton2.config(height = 1, width = 8)
        RangeButton2.place(x = 100, y = 1)



       
  

if __name__ == "__main__":
    app = mainwindow()
    app.mainloop()

#how im thinking of connecting to the databases.
#hopefully if we get neo4j up and running on aws and is available to ssh into 
#using pexpect to ssh into
#send the commands from this app -> pexpect -> aws neo4j instance

#pxssh link https://www.pythonforbeginners.com/code-snippets-source-code/ssh-connection-with-python
#pexpect link from stackoverflow https://stackoverflow.com/questions/15096667/ssh-and-send-commands-in-tkinter
#github pexpect https://github.com/pexpect/pexpect






#********code for image gallery***********

#image_list = ['cat1.jpg', 'cat2.jpg', 'cat3.jpg']
#text_list = ['cat1', 'cat2', 'cat3']
#current = 0

#def move(delta):
#    global current, image_list
#    if not (0 <= current + delta < len(image_list)):
#        tkMessageBox.showinfo('End', 'No more image.')
#        return
#    current += delta
#    image = Image.open(image_list[current])
#    photo = ImageTk.PhotoImage(image)
#    label['text'] = text_list[current]
#    label['image'] = photo
#    label.photo = photo


#root = Tkinter.Tk()

#label = Tkinter.Label(root, compound=Tkinter.TOP)
#label.pack()

#frame = Tkinter.Frame(root)
#frame.pack()

#Tkinter.Button(frame, text='Previous picture', command=lambda: move(-1)).pack(side=Tkinter.LEFT)
#Tkinter.Button(frame, text='Next picture', command=lambda: move(+1)).pack(side=Tkinter.LEFT)
#Tkinter.Button(frame, text='Quit', command=root.quit).pack(side=Tkinter.LEFT)

#move(0)

#root.mainloop()