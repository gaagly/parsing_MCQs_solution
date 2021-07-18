"""When there is an incorrect question. Software just writes location of answer as 0"""



from bs4 import BeautifulSoup
import requests
import csv

def check_QIDs(args):
    """In Old answer keys it generated extra QIDs. Thid code will return the location of the QID"""
    location_of_QIDs = []
    for i in range(len(args)):
        try:
            #print(args[i].text)
            if 'Question ID' in args[i].text:
                location_of_QIDs.append(i)

        except AttributeError :
            pass
    return location_of_QIDs

def answer_locator(args): # LIST CONTAINING TAGS as ELEMENTS
    """This function Locates index of the Answer and also index of correct option"""
    """Returns the index of correct answer"""
    n = len(args)

    for i in range(n):
        try:
            # Need for a try except statement arised because not every element in the
            # list is bs4.element.tag. Some are text and numbers
            if args[i].text == "Ans": #Locates Ans in cells. It helps us merge all the cells before it
                return i
        except AttributeError:
            pass

def ans_loc_text(args): #LIST CONTAINING STR as ELEMENTS
    """Locates Ans in a list containing str"""
    n = len(args)
    for i in range(n):
        if args[i] == ' <td align="center" class="bold">Ans</td>': #Locates Ans in cells. It helps us merge all the cells before it
            return i

def correct_answer_index(args):
    """This function returns index of correct answer in the given list args"""
    last_index = len(args)
    answer = answer_locator(args)
    for i in range(answer + 1,last_index):
        try:
            if args[i]['class'] == ['rightAns']:
                return (i - answer)
        except Exception as e:
            return "no_correct_answer"



    print("==========================================================================")
    return False #Returns false when no correct answer is found

def is_comprehension(args):
    """This function would return true if the given Question is of Comprehension type"""
    # otherwise it will return false
    #
    if args[0].text == "Comprehension:":
        return True
    else:
        return False

def remove_tag_comprehension(args):
    # THIS Function will remove TAG TD
    """["Comprehension:","Main_Text","SubQuestion","Qno","Select the Question",
    "Ans","Options1","Options2","Options3","Options4"""
    #I am inserting an empty element at location args[0]
    args.insert(0, args[3])
    del args[4]
    ans = answer_locator(args)-1 #locates answer in the list

    ### CLEANING INDEX 1 to 4 of its tags <td> ###
    ### After this elements in 1 to 4 will convert from tag to STR
    for i in range(1,5): #This will generate index 1 to 4
        temp = args[i].contents
        args[i]= ""
        for j in temp:
            args[i] = args[i] + str(j)

    # for i in range(1,ans+4):
    #     args[i] = str(args[i]) # This converts them from tag to string
    # args[1 : ans] = ['\n'.join(args[1 : ans])]
    return args
def clean_tags(args):
    """This option will remove tags from the element which is a BS4 element
    Here args = list[1].contents
    list[1].contents is a list, each element is the content inside the <td> tag"""
    ## args = [<1>, <2>, <3>, <4>, <5>]
    temp = ""
    for i in args:
        temp = temp+str(i)
    return temp

def tag_to_string(args):
    """This function will convert everything in the list to strings"""
    temp = []
    for i in range(len(args)):
        temp.append(str(args[i]))

    return temp

def option_cleaner_comprehension(op1,op4,args):
    """Function that cleans options in a comprehension"""
    for i in range(op1,op4+1):

        delimiter_ = str(i-(op1-1))+". "    # (i-1) is done here because it will result 1,2,3,4
        args[i] = str(args[i])
        temp = args[i].split(delimiter_)
        args[i]=temp[-1]
        temp.clear()
        temp = args[i].split("</td>") #this removes the garbage in the end
        args[i] = temp[0]
    return args

def option_cleaner(op1,op4,args):
    """This function clears Tick and cross.png from options"""
    """op1 is index of option 1 and same for op4/last option"""
    for i in range(op1,op4+1):
        delimiter_ = str(i-(op1-1))+". "    # (i-1) is done here because it will result 1,2,3,4
        args[i] = str(args[i])
        temp = args[i].split(delimiter_)
        args[i]=temp[-1]
        temp.clear()
        temp = args[i].split("</td>") #this removes the garbage in the end
        args[i] = temp[0]
    return args

#prompt for entering file name
filename = input("Please enter Name of TCS Ans key HTML file: ")
try:
    #This will open the TCS Answer Key File. It is necessary to open it as utf8 encoding
    with open(filename, encoding="utf8") as html_file:
        soup = BeautifulSoup(html_file, 'lxml')
        #This will parse all data from HTML using lxml parser which is being used by BeautifulSoup() method.
        #It assigns the parsed value to soup

    #Now all parsed data is in soup. No we are parsing section Name, all Question Panels(Questions, QuestionID)
    section_cntnr_list = soup.find_all('div', class_='section-cntnr')
    number_of_questions=0
    #section_cntne_list is a list
    #each element is in HTML containing Section Name and ALL Questions inside the section
    for section_cntnr in section_cntnr_list:
        question_pnl = section_cntnr.find_all('div', class_='question-pnl')
        #question_pnl is a list
        #it contains all questions given in the Question Paper and their ids together as one element
        # [<Question1, QID1> , <Question2, QID2>, ...]
        section_lbl_raw = section_cntnr.find('div', class_='section-lbl')
        #coding for getting section name and replacing whitespaces with underscore and passing is as the file name
        section_name = str(section_lbl_raw.text)
        section_name = section_name.replace(" ","_") #Replacing whitespaces

        section_name_file = section_name + ".csv"   #this will be passed as file name. Files will be created sectionwise
        section_name_file = section_name_file.replace("Section_: ","") #I had to remove all whitespaces and section as well


        with open(section_name_file,"a",encoding="utf8") as csv_sample: #utb8 encoding is producing unexpected A with signs in front of text
            csv_reader = csv.reader(csv_sample)
            csv_writer = csv.writer(csv_sample)
            print("File ",section_name_file," created")
            #The following for loop loops over question_pnl List
            table_comprehension = []
            for question_with_id in question_pnl:
                #now we have to read each element in the question_pnl list
                #question_with_id has first question and its QID

                # now the following code will separate Question and its ID
                question_with_options = question_with_id.find('table', class_ = "questionRowTbl")
                #the following code will assign menu-tbl data to question_id_table.
                #it will contain tags table. This is not a list as there is only one QuestionID table in Question PNL
                #and tags will be of data

                #===============MENU TABLE Extraction========================================
                question_menu_table = question_with_id.find('table', class_ = "menu-tbl")
                #============================================================================
                #question_with_options contains only html of question and options only
                #question_menu_table contains QID only
                question_menu_table_elt = question_menu_table.find_all('td')
                ##(question_menu_table_elt[1] is the Question Id of the Question
                ## it is in this form
                ## <td class="bold">98958015307</td>
                ## be carefull this is a tag not a string.

                #The following codes should separate questions and its options. Its options should contain tick/cross wala jugaad.
                #this code will also be used to extract data from Question_Menu_Table
                question = question_with_options.find_all('td')
                #the data in question is in the form of list. It contains a single question and its components as elements
                # for example [QNo,Question,Ans,Option1,Option2, optio3,option4]

                list = []
                for ques in question:
                    if str(ques) == "<td></td>": #Earlier I checker whether the ques.text is empty or not. And skipped empty ones
                        #But it skipped those cells which had questions as images. Now it skips EMpty cells
                        pass
                    else:
                        list.append(ques)


                list.append(correct_answer_index(list)) #This creates anothe column of the correct option
                #Now everything like merging and manipulating list will happen down this line
                #Till here list contains tags as elements and last element is an integer

                #check whether List contains comprehension or not
                if is_comprehension(list)==True:
                    #The elements in the LIST are tags. I am using a function to convert them into a string elements
                    list_comprehension = remove_tag_comprehension(list).copy() #This function will remove tags from indices 1 to 4
                    list_comprehension[0] = question_menu_table_elt[1].text
                    #list_comprehension will contain elements which are Qno, Comprehensio, text, sub, select, Qno

                    ans_loc = answer_locator(list_comprehension) #saves answer location in the list

                    del list_comprehension[ans_loc-1] ##delete cell preceding ans
                    del list_comprehension[ans_loc-1] ##delete ANs cell
                    del list_comprehension[1] ##delete text "Comprehension"

                    ##Ab comprehension mei options ki safai karni hai
                    ## seedhey bhi uda sktey hai aur nhi bhi
                    list_comprehension = option_cleaner_comprehension(ans_loc-2,ans_loc+1,list_comprehension).copy()

                    # the following code will be applicable on old TCS Answer Keys
                    # without this code two more cells with Question Ids are created
                    qid_list = check_QIDs(list_comprehension)
                    if len(qid_list):
                        temp = []
                        for i in range(len(list_comprehension)):
                            if i not in qid_list:
                                temp.append(list_comprehension[i])
                        list_comprehension = temp.copy()
                        temp = []

                    table_comprehension.append(list_comprehension)

                else:
                    #UPTO THIS INSTANCE ALL QUESTIONS are correctly aligned
                    #now we remove ANS Cell and its preceding cell too
                    ans_loc = answer_locator(list)

                    del list[ans_loc-1] #Deletes cell preceding Ans
                    del list[ans_loc-1] #Deletes Ans cell

                    #Now its time to Remove ticks and Crosses from in front of the options
                    #options start from index 2 to 5

                    ##option cleaner will remove unecessary <td> and cross tick.png
                    list = option_cleaner(ans_loc-1,ans_loc+2,list).copy()
                    list[0] = question_menu_table_elt[1].text
                    list[1] = clean_tags(list[1].contents)

                    # the following code will be applicable on old TCS Answer Keys
                    # without this code two more cells with Question Ids are created
                    qid_list = check_QIDs(list)
                    if len(qid_list):
                        temp = []
                        for i in range(len(list)):
                            if i not in qid_list:
                                temp.append(list[i])
                        list = temp.copy()
                        temp = []


                    csv_writer.writerow(list)
                    number_of_questions+=1
            ###### CHECK WHETHER OR NOT THERE IS ANY COMPREHENSION TABLE AVAILABLE IN THE SECTION
            ###### IT PRINTS IT IN ANOTHER FILE WITH COMPREHENSION APPENDED TO THE SECTION NAME
            if len(table_comprehension) != 0:
                comprehension_containing_filename = section_name+"_comprehension.csv"
                comprehension_containing_filename = comprehension_containing_filename.replace("Section_: ","")
                with open(comprehension_containing_filename,"a",encoding="utf8") as comp_csv:
                    comp_csv_reader = csv.reader(comp_csv)
                    comp_csv_writer = csv.writer(comp_csv)
                    print("File ",comprehension_containing_filename," created")
                    for com_ques_row in table_comprehension:
                        comp_csv_writer.writerow(com_ques_row)
                        number_of_questions+=1
                table_comprehension.clear() #CLEARING the comprehension table after writing all the comprehension questions
    print("Successful parsed {} questions".format(number_of_questions))

except FileNotFoundError:
    print("File does not exists!")





