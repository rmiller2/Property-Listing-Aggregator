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



#database connection
myclient = MongoClient("mongodb://localhost:27017/")
mydb = myclient["Property_aggregator"]



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

options_list = ["Sold", "Unsold", "All", "By Country", "By state(U.S.)"]


current_menu_state = "master_list"
previous_menu_state = "none"

menu_stack = ["master_list"]
property_id = 0

master_ref = "temp"
gallery_max = 0
gallery_place = 0

class mainwindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #window settings
        self.title('Listing Aggregator')    #set title
        self.geometry("1000x800")           #set the size
        self.resizable(0, 0)                #fix the size
        
        

        #retriever of webpage layout
        retrieve_frame = Frame(self)
        retrieve_frame.grid(row=0, column=0, sticky=W+N)

        Label(retrieve_frame, text='Enter URL to grab').grid(row=0, column=0, sticky=W) 

        url_input_string = Entry(retrieve_frame) 
        url_input_string.grid(row=0, column=1, sticky=W)

        launch_grab_script_button = tk.Button(retrieve_frame, text="Run",  command=lambda: launch_grab_script_button_action())
        launch_grab_script_button.grid(row=0, column=2, sticky=W)

        #general purpose listbox
        listbox_frame = Frame(self)
        listbox_frame.grid(row=1, column=0, sticky=W+N)
        
        listbox_label = Label(listbox_frame, text='Placeholder').grid(row=0, column=0,  sticky=W) 

        button_frame = Frame(listbox_frame)
        button_frame.grid(row=0, column=1, sticky=W)

        back_button = tk.Button(button_frame, text="<-", state='disabled',  command=lambda: back_button_action())
        back_button.grid(row=0, column=1, sticky=W)

        select_button = tk.Button(button_frame, text="Select",  command=lambda: select_button_action())
        select_button.grid(row=0, column=2, sticky=W)

        check_sold_button = tk.Button(button_frame, text="Check Sold",  command=lambda: check_sold_button_action())
        check_sold_button.grid(row=0, column=3, sticky=W)

        display_box = Listbox(listbox_frame, height=20, width=40)
        default_col = mydb["Lists"]
        obj = default_col.find({"name": "master_list"})

        blanklist = list(obj[0]['master_list'])

        display_box.insert(END, *blanklist)

        display_box.grid(row=1, column=0, columnspan=3, padx=5, sticky=W)


        #listing frame
        #listing_frame = Frame(self, highlightbackground="black", highlightthickness=1)
        listing_frame = Frame(self)
        listing_frame.grid(row=1, column=1, rowspan=20, sticky=W+N, padx=(30,0))


        #listing photo gallery
        gallery_button = tk.Button(listing_frame, text="Launch Photo Gallery",state='disabled', command=lambda: launch_gallery_button_action())
        gallery_button.grid(row=0, column=1, sticky=W)

        #listing name 
        Label(listing_frame, text='Property Name:', font=("", 16)).grid(row=1, column=0, sticky=N+W) 
        name_box = Listbox(listing_frame, height=1, width=30)
        name_box.grid(row=1, column=1, sticky=W)

        #listing price 
        Label(listing_frame, text='Price:', font=("", 16)).grid(row=2, column=0, sticky=N+W) 
        price_box = Listbox(listing_frame, height=1, width=15)
        price_box.grid(row=2, column=1, sticky=W)

        #listing city 
        Label(listing_frame, text='City:', font=("", 16)).grid(row=3, column=0, sticky=N+W) 
        city_box = Listbox(listing_frame, height=1, width=15)
        city_box.grid(row=3, column=1, sticky=W)

        #listing state(if applicable) 
        Label(listing_frame, text='State:', font=("", 16)).grid(row=4, column=0, sticky=N+W) 
        state_box = Listbox(listing_frame, height=1, width=15)
        state_box.grid(row=4, column=1, sticky=W)

        #listing country 
        Label(listing_frame, text='Country:', font=("", 16)).grid(row=5, column=0, sticky=N+W) 
        country_box = Listbox(listing_frame, height=1, width=15)
        country_box.grid(row=5, column=1, sticky=W)

        #listing address 
        Label(listing_frame, text='Address:', font=("", 16)).grid(row=6, column=0, sticky=N+W) 
        address_box = Listbox(listing_frame, height=1, width=15)
        address_box.grid(row=6, column=1, sticky=W)

        #listing property type 
        Label(listing_frame, text='Type:', font=("", 16)).grid(row=7, column=0, sticky=N+W) 
        type_box = Listbox(listing_frame, height=1, width=15)
        type_box.grid(row=7, column=1, sticky=W)

        #listing bedrooms 
        Label(listing_frame, text='Bedrooms:', font=("", 16)).grid(row=8, column=0, sticky=N+W) 
        bedrooms_box = Listbox(listing_frame, height=1, width=15)
        bedrooms_box.grid(row=8, column=1, sticky=W)

        #listing bathrooms 
        Label(listing_frame, text='Bathrooms:', font=("", 16)).grid(row=9, column=0, sticky=N+W) 
        bathrooms_box = Listbox(listing_frame, height=1, width=15)
        bathrooms_box.grid(row=9, column=1, sticky=W)

        #listing land area
        Label(listing_frame, text='Land Area:', font=("", 16)).grid(row=10, column=0, sticky=N+W) 
        land_area_box = Listbox(listing_frame, height=1, width=15)
        land_area_box.grid(row=10, column=1, sticky=W)

        #listing living area 
        Label(listing_frame, text='Living Area:', font=("", 16)).grid(row=11, column=0, sticky=N+W) 
        living_area_box = Listbox(listing_frame, height=1, width=15)
        living_area_box.grid(row=11, column=1, sticky=W)

        #listing internal ref 
        Label(listing_frame, text='Internal Ref:', font=("", 16)).grid(row=12, column=0, sticky=N+W) 
        internal_ref_box = Listbox(listing_frame, height=1, width=15)
        internal_ref_box.grid(row=12, column=1, sticky=W)

        #listing property description 
        Label(listing_frame, text='Description:', font=("", 16)).grid(row=13, column=0, sticky=N+W) 
        description_box = Text(listing_frame, height=20, width=50, highlightbackground="black", highlightthickness=1)
        description_box.grid(row=13, column=1, sticky=W)
       

        

        def launch_gallery_button_action():
            global master_ref
            global gallery_max
            global gallery_place
            test_width = 750

            if (master_ref != "temp"):
                gallery_ref = master_ref    #internal ref for lookup

                temp_col = mydb["Properties"]
                item1 = temp_col.find({"Internal Reference": gallery_ref})
    
                image_count = item1[0]["image count"]

                gallery_max = image_count - 1

                gallery_place = 0

                path = "/Users/richardmiller/Documents/website_file_storage/" + gallery_ref + "/" + gallery_ref + "_0.jpg"  
                sub_path = "/Users/richardmiller/Documents/website_file_storage/" + gallery_ref + "/" + gallery_ref
                print(path)


                gallery_window = tk.Toplevel()
                gallery_window.geometry("%dx%d%+d%+d" % (925, 525, 250, 125))  #define the window
                gallery_window.columnconfigure(0, weight=1)
                

                main_frame = Frame(gallery_window)                              #main frame for window
                main_frame.grid(row=0,column=0, sticky=NSEW)


                myimage = PIL.Image.open(path)

                wpercent = (test_width/float(myimage.size[0]))
                hsize = int((float(myimage.size[1])*float(wpercent)))
                myimage = myimage.resize((test_width,hsize),PIL.Image.ANTIALIAS)

                render = ImageTk.PhotoImage(myimage)
                img = Label(main_frame, image=render)
                img.image = render
                img.grid(row=0,column=1, sticky=NSEW)

                photo_back_button = tk.Button(main_frame, text="back", state='disabled',  command=lambda: photo_back_button_action(img, photo_next_button, photo_back_button, sub_path))
                photo_back_button.grid(row=0, column=0, sticky=N+S+E)

                photo_next_button = tk.Button(main_frame, text="next",  command=lambda: photo_next_button_action(img, photo_next_button, photo_back_button, sub_path))
                photo_next_button.grid(row=0, column=2, sticky=N+S+W)

                main_frame.columnconfigure(0, weight=1)
                main_frame.columnconfigure(1, weight=1)
                main_frame.columnconfigure(2, weight=1)


        def photo_back_button_action(image1, button1, button2, sub_path1):
            global gallery_max
            global gallery_place
            global master_ref
            test_width = 750

            gallery_place = gallery_place - 1

            path = sub_path1 + "_" + str(gallery_place) + ".jpg"

            myimage = PIL.Image.open(path)

            wpercent = (test_width/float(myimage.size[0]))
            hsize = int((float(myimage.size[1])*float(wpercent)))
            myimage = myimage.resize((test_width,hsize),PIL.Image.ANTIALIAS)

            render = ImageTk.PhotoImage(myimage)
            image1.config(image=render)
            image1.image = render
 
            if(gallery_place < gallery_max):
                button1['state'] = NORMAL

            if(gallery_place == 0):
                button2['state'] = DISABLED

        def photo_next_button_action(image1, button1, button2, sub_path1):
            global gallery_max
            global gallery_place
            global master_ref
            test_width = 750

            gallery_place = gallery_place + 1

            path = sub_path1 + "_" + str(gallery_place) + ".jpg"

            myimage = PIL.Image.open(path)

            wpercent = (test_width/float(myimage.size[0]))
            hsize = int((float(myimage.size[1])*float(wpercent)))
            myimage = myimage.resize((test_width,hsize),PIL.Image.ANTIALIAS)

            render = ImageTk.PhotoImage(myimage)
            image1.config(image=render)
            image1.image = render
 
            if(gallery_place > 0):
                button2['state'] = NORMAL

            if(gallery_place == gallery_max):
                button1['state'] = DISABLED


        def check_sold_button_action():
            pass

        def select_button_action():
            selected_value = display_box.get(ANCHOR)                    #gets the selected value 

            if(menu_stack[-1] in country_list):
                global property_id
                property_id = 1
                temp_col = mydb["Countries"]
                temp_string = "properties." + selected_value
                item = temp_col.find({'country':menu_stack[-1]},{temp_string})
                temp_ref = item[0]['properties'][selected_value]
                print("temp ref = " + temp_ref)

                temp_col = mydb["Properties"]
                item1 = temp_col.find({"Internal Reference": temp_ref})
                
                temp_usage_list = item1[0]["usage list"]

                for x in range(len(temp_usage_list)):
                    print(temp_usage_list[x])

                if(temp_usage_list[0] == 1):
                    name_box.delete('0', 'end')
                    name_box.insert(END, item1[0]["Title"])
                if(temp_usage_list[1] == 1):
                    price_box.delete('0', 'end')
                    price_box.insert(END, item1[0]["Price"])
                if(temp_usage_list[2] == 1):
                    city_box.delete('0', 'end')
                    city_box.insert(END, item1[0]["City"])
                if(temp_usage_list[3] == 1):
                    state_box.delete('0', 'end')
                    state_box.insert(END, item1[0]["State"])
                if(temp_usage_list[4] == 1):
                    country_box.delete('0', 'end')
                    country_box.insert(END, item1[0]["Country"])
                if(temp_usage_list[5] == 1):
                    address_box.delete('0', 'end')
                    address_box.insert(END, item1[0]["Address"])
                if(temp_usage_list[6] == 1):
                    type_box.delete('0', 'end')
                    type_box.insert(END, item1[0]["Property Type"])
                if(temp_usage_list[7] == 1):
                    bedrooms_box.delete('0', 'end')
                    bedrooms_box.insert(END, item1[0]["Bedrooms"])
                if(temp_usage_list[8] == 1):
                    bathrooms_box.delete('0', 'end')
                    bathrooms_box.insert(END, item1[0]["Bathrooms"])
                if(temp_usage_list[9] == 1):
                    living_area_box.delete('0', 'end')
                    living_area_box.insert(END, item1[0]["Living Area"])
                if(temp_usage_list[10] == 1):
                    land_area_box.delete('0', 'end')
                    land_area_box.insert(END, item1[0]["Land Area"])
                if(temp_usage_list[11] == 1):
                    internal_ref_box.delete('0', 'end')
                    internal_ref_box.insert(END, item1[0]["Internal Reference"])
                    global master_ref
                    master_ref = item1[0]["Internal Reference"]
                    print("master ref = ")
                    print(master_ref)
                if(temp_usage_list[13] == 1):
                    description_box.delete('1.0', END)
                    description_box.insert(INSERT, item1[0]["Listing Description"])
                
                gallery_button['state'] = NORMAL

                print("number of images = ")
                print(item1[0]["image count"])

            elif(selected_value in country_list):
                menu_stack.append(selected_value)                           #pushes the current menu item to top of stack
                temp_col = mydb["Countries"]
                obj = temp_col.find({"country": selected_value})
                templist = list(obj[0]['properties'])
                display_box.delete('0','end')
                display_box.insert(END, *templist)
                back_button['state'] = NORMAL

            else:
                menu_stack.append(selected_value)                           #pushes the current menu item to top of stack
                temp_col = mydb["Lists"]
                obj = temp_col.find({"name": selected_value})
                templist = list(obj[0]['list'])
                display_box.delete('0','end')
                display_box.insert(END, *templist)
                back_button['state'] = NORMAL




        def back_button_action():
            #current_menu_state = previous_menu_state                    #change the menu state back to the previous
            global property_id

            if (property_id == 1):
                name_box.delete('0', 'end')
                price_box.delete('0', 'end')
                city_box.delete('0', 'end')
                state_box.delete('0', 'end')
                country_box.delete('0', 'end')
                address_box.delete('0', 'end')
                type_box.delete('0', 'end')
                bedrooms_box.delete('0', 'end')
                bathrooms_box.delete('0', 'end')
                living_area_box.delete('0', 'end')
                land_area_box.delete('0', 'end')
                internal_ref_box.delete('0', 'end')
                description_box.delete('1.0', END)
                property_id = 0
                gallery_button['state'] = DISABLED

            menu_stack.pop()
            current_top_stack = menu_stack[-1]

            temp_col = mydb["Lists"]
            obj = temp_col.find({"name": current_top_stack})

            if(current_top_stack == "master_list"):
                templist = list(obj[0]['master_list'])
                back_button['state'] = DISABLED
            else:
                templist = list(obj[0]['list'])

            display_box.delete('0','end')
            display_box.insert(END, *templist)
            
            
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
                    listing_images_list = [] 
                    condensed_dict = {}

                    usage_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]

                    ref_id_found = False

                    #retrieve name of listing
                    headline_retriever = soup.find('h1', attrs={"class":"headline"})#this tests and gets the headline name of the listing 
                    for string in headline_retriever.stripped_strings:
                        listing_name = string
                        listing_dict["Title"] = listing_name
                        
                        usage_list[0] = 1
                        #print(listing_name)
                        break

                    #retrieve price of listing
                    price_retriever = soup.find("div", attrs={"class":"price"})#this tests and gets the price of the listing 
                    for string in price_retriever.stripped_strings:
                        listing_price = string
                        listing_dict["Price"] = listing_price
                        usage_list[1] = 1
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
                                    usage_list[2] = 1

                                elif (location in state_list):
                                    location_state = location
                                    listing_dict["State"] = location_state
                                    usage_list[3] = 1

                                elif (location in country_list):
                                    location_country = location
                                    listing_dict["Country"] = location_country
                                    usage_list[4] = 1

                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Address:":                 #gets the listed address
                            listing_address_string = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_address = listing_address_string.split("(Show Map)",1)[0]
                            listing_dict["Address"] = listing_address
                            usage_list[5] = 1

                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Property type:":           #gets the property type
                            listing_property_type = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Property Type"] = listing_property_type
                            usage_list[6] = 1

                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Bedrooms:":                #gets the bedroom quantity (if applicable)
                            listing_bedrooms = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Bedrooms"] = listing_bedrooms
                            usage_list[7] = 1

                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Bathrooms:":               #gets the bathroom quantity (if applicable)
                            listing_bathrooms = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Bathrooms"] = listing_bathrooms
                            usage_list[8] = 1

                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Living area:":             #gets the living area (if applicable)
                            listing_living_area = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Living Area"] = listing_living_area
                            usage_list[9] = 1

                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Land area:":               #gets the land area (if applicable)
                            listing_land_area = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Land Area"] = listing_land_area
                            usage_list[10] = 1

                        elif (li.find('span', {"class":"name"}).getText(strip=True)) == "Internal Reference:":      #gets the jamesedition internal reference id
                            listing_internal_ref = li.find('span', {"class":"value"}).getText(strip=True)
                            listing_dict["Internal Reference"] = listing_internal_ref
                            usage_list[11] = 1
                            ref_id_found = True
                            image_link_file = open("image_links.txt", "w")

                            
                            for link in soup.find_all('a', href=True):                                               #retrieves all the image names
                                if link['href'].startswith("https://img.jamesedition.com/listing_images"):
                                    listing_images_list.append(link['href'])
                                    image_link_file.write(link['href']+"\n")
                            image_link_file.close()


                            #adds the list of image names to the dict
                            listing_dict["images"] = listing_images_list
                            listing_dict["image count"] = len(listing_images_list)
                            usage_list[12] = 1
                            subprocess.call(['./get_images.sh ' + "image_links.txt " + listing_internal_ref], shell=True) #uncomment to actually run, commented for testing to save bandwidth
                            

                    #retrieves listing description   
                    description_retriever = soup.find('div', attrs={"class":"JE-listing-info__description"})
                    for string in description_retriever.stripped_strings:
                        description_string = string
                        listing_dict["Listing Description"] = description_string
                        usage_list[13] = 1
                        break

                    
                    listing_dict["usage list"] = usage_list
                    

                    #print out the listing dict before pushing to DB
                    for x, y in listing_dict.items():
                        print(x, y)

                    

                    #push to DB
                    mycol = mydb["Properties"]
                    x = mycol.insert_one(listing_dict) #inserting into the main properties holder


                    #adding the country if it doesnt exist in db yet
                    mycol = mydb["Countries"]

                    if(mycol.count_documents({"country": location_country}, limit = 1) != 0):                   #updates the country with the new listing
                        temp_string = "properties." + listing_name 
                        mycol.update({"country": location_country},{'$set':{temp_string:listing_internal_ref}})

                    else:
                        condensed_dict["country"] = location_country
                        mycol.insert_one(condensed_dict)                #adds the country to the countries list

                        temp_string = "properties." + listing_name 
                        test_list = {}
                        test_list[listing_name] = listing_internal_ref

                        mycol.update({"country": location_country},{'$set':{temp_string:listing_internal_ref}})

                        mycol = mydb["Lists"]

                        mycol.update({'name':'By Country'},{'$push':{'list':location_country}})     #push the new country to the updated list
                        mycol.update({'name':'By Country'},{'$push':{'list':{'$each':[], '$sort': 1}}}) 


                    

            







                    #pseudocode for adding to all the different lists
                    
                
                    #normal full entry will be entered into the properties collection
                    #everywhere else will have the form of
                        # name,city,country -> key=internal ref 


                    #add to unsold
                    
                    #check if country exists in db
                        #if yes, add to country
                            # if country is usa, check state
                                # if exists, add to state
                        #if no, create country and add

                       

                    #start adding code for insterting into the different list types
                    #***********************************************************************


                    #call remove temp text file
                    subprocess.call(['./remove_text_file.sh'], shell=True)
                    

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