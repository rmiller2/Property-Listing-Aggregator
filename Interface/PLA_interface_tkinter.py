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

myclient = MongoClient("mongodb://localhost:27017/")
mydb = myclient["Property_aggregator"]
#mycol = mydb["Properties"]

country_list = ["Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Aruba", "Australia", "Austria", "Bahamas", "Barbados",
"Belgium", "Belize", "Bermuda", "Bonaire, Sint Eustatius and Saba", "Brazil", "Bulgaria", "Canada", "Cayman Islands", 
"Chile", "China", "Colombia", "Costa Rica", "Croatia", "Curaçao", "Cyprus", "Czech Republic", "Dominica", "Dominican Republic", "Estonia", "Fiji", "Finland",
 "France", "French Polynesia", "Germany", "Gibraltar", "Greece", "Grenada", "Honduras", "Hong Kong", "Hungary", "India", "Indonesia", "Ireland", "Italy",
 "Jamaica", "Japan", "Kazakhstan", "Latvia", "Lithuania", "Luxembourg", "Malaysia", "Maldives", "Mali", "Malta", "Mauritius", "Mexico", "Monaco", 
 "Montenegro", "Mococco", "Mozambique", "Netherlands", "New Zealand", "Norway", "Panama", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico",
 "Qatar", "Romania", "Russian Federation", "Saint Barthélemy", "Saint Lucia", "Saint Martin", "Sao Tome and Principe", "Serbia", "Seychelles", "Singapore",
 "Sint Maarten", "Slovakia", "Slovenia", "South Africa", "Spain", "Sri Lanka", "Sweden", "Switzerland", "Taiwan, Republic Of China", "Thailand", "Tunisia",
 "Turkey", "Turks and Caicos Islands", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uraquay", "Vanuatu", "Virgin Islands, British", "Virgin Islands, U.S."]

state_list = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", 
"IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM",
"NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

options_list = {"Sold", "Unsold", "All", "By Country", "By state(U.S.)"}



class mainwindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #window settings
        self.title('Listing Aggregator')    #set title
        self.geometry("1000x800")         #set the size
        self.resizable(0, 0)              #fix the size
        

        #retriever of webpage layout
        retrieve_frame = Frame(self)
        retrieve_frame.grid(row=0, column=0, sticky=W+N, pady=(0,20))

        Label(retrieve_frame, text='Enter URL to grab').grid(row=0, column=0, sticky=W) 

        url_input_string = Entry(retrieve_frame) 
        url_input_string.grid(row=0, column=1, sticky=W)

        launch_grab_script_button = tk.Button(retrieve_frame, text="Run",  command=lambda: launch_grab_script_button_action())
        launch_grab_script_button.grid(row=0, column=2, sticky=W)

        #general purpose listbox
        listbox_frame = Frame(self)
        listbox_frame.grid(row=2, column=0, sticky=W)
        
        listbox_label = Label(listbox_frame, text='Placeholder').grid(row=0, column=0, sticky=W) 

        button_frame = Frame(listbox_frame)
        button_frame.grid(row=0, column=1, sticky=W)

        back_button = tk.Button(button_frame, text="<-",  command=lambda: back_button_action())
        back_button.grid(row=0, column=1, sticky=W)

        select_button = tk.Button(button_frame, text="Select",  command=lambda: select_button_action())
        select_button.grid(row=0, column=2, sticky=W)

        check_sold_button = tk.Button(button_frame, text="Check Sold", state='disabled',  command=lambda: check_sold_button_action())
        check_sold_button.grid(row=0, column=3, sticky=W)
        #self.x['state'] = 'normal'

        display_box = Listbox(listbox_frame, height=20, width=40)
        default_col = mydb["Lists"]
        obj = default_col.find({"name": "master_list"})
        #for x in list(obj[0]['master_list']):
        #    print(x)
        blanklist = list(obj[0]['master_list'])

        #for x in blanklist:
        #    print(x)
        #for x in blanklist:
        display_box.insert(END, *blanklist)

        display_box.grid(row=1, column=0, columnspan=3, sticky=W)

        


        def check_sold_button_action():
            pass


        def select_button_action():
            test_var = display_box.get(ANCHOR)
            #url_input_string.insert(0, test_var)
            #pass


        def back_button_action():
            pass

    
        def launch_grab_script_button_action():

            url_check_string = url_input_string.get()#get the url that was entered

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

                    #retrieving pieces of the detail list
                    for li in soup.find('ul', {"class":"details-list"}).find_all("li"):
                        if (li.find('span', {"class":"name"}).getText(strip=True)) == "Location:": #gets the location with country,state(optional), city
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
                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Address:": #gets the listed address
                            listing_address_string = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_address = listing_address_string.split("(Show Map)",1)[0]
                            listing_dict["Address"] = listing_address
                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Property Type:": #gets the property type
                            listing_property_type = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Property Type"] = listing_property_type
                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Bedrooms:": #gets the bedroom quantity (if applicable)
                            listing_bedrooms = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Bedrooms"] = listing_bedrooms
                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Bathrooms:": #gets the bathroom quantity (if applicable)
                            listing_bathrooms = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Bathrooms"] = listing_bathrooms
                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Living area:": #gets the living area (if applicable)
                            listing_living_area = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Living Area"] = listing_living_area
                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Land area:": #gets the land area (if applicable)
                            listing_land_area = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Land Area"] = listing_land_area
                        
                    description_retriever = soup.find('div', attrs={"class":"JE-listing-info__description"})#this gets the listing description
                    for string in description_retriever.stripped_strings:
                        description_string = string
                        listing_dict["Listing Description"] = description_string
                        break

                    for x, y in listing_dict.items():
                        print(x, y)

                    

                    x = mycol.insert_one(listing_dict)
                    
                    

                    #subprocess.call(['./remove_website.sh'], shell=True) #not needed as wget -O will overwrite the file anyways and is not necessary for proper usage
  
                elif(return_val == 1):
                    #oops redirect
                    print("redirect 1")
                elif(return_val == 2):
                    #404 error
                    print("404 error 2")
            else:
                print("Not from approved website,error")#print off error
                #make this a display feature that shows if invalid
            

if __name__ == "__main__":
    app = mainwindow()
    app.mainloop()





#todo list

#add a check if sold button that activates when a property is selected
#figure out how to always get the usd instead of the native currency
#get it set up to be able to edit the lists of properties during insertion
#plan out how to do an update button so it updates everything including the lists
# 




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