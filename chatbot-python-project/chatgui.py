import nltk
from nltk.stem import WordNetLemmatizer
import pandas as pd
import pickle
import numpy as np
import json
import random
from scipy.spatial import distance
from keras.models import load_model

model = load_model('chatbot_model.h5')

lemmatizer = WordNetLemmatizer()

# load intents ,words and classes
intents = json.loads(open('intent.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    # get response according to intent
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['intent'] == tag:
            # get a random response according to intent
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(msg):
    # predict the intent
    ints = predict_class(msg, model)
    # get response according to intent
    res = getResponse(ints, intents)
    return res


# Creating GUI with tkinter
import tkinter
from tkinter import *


def send():
    # get the entry text from user
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)

    # check if the message is not empty
    if msg != '':
        ChatLog.config(state=NORMAL)
        # insert user message in the chat log
        ChatLog.insert(END, "You: " + msg + '\n\n')

        if msg == 'recommendation':
            # if the question is recommendation call recommendation function
            recommend()
        if msg == 'recommend':
            # if the question is recommend call recommendation function
            recommend()

        ChatLog.config(foreground="#442265", font=("Verdana", 12))
        # get bot response
        res = chatbot_response(msg)
        ChatLog.insert(END, "Bot: " + res + '\n\n')
        # insert bot response in the chat log

        # update yview
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)


from tkinter import messagebox


def recommend():
    # var for the choice selected
    selected_text = ""
    # indx represent the index of the question
    indx = 0

    # choices values

    values = [
        ['communication', 'drawing', 'creativity', 'enthusiasm',
         'confidence'],
        ['persuasion ', 'negotiation', 'ethics', 'reading', 'accuracy',
         'psychology', 'research', 'patience', 'coding', 'strategy',
         'confidence', 'creativity', 'flexibility', 'empathy', 'biology',
         'critical-thinking', 'leadership', 'analytics'],
        ['writing', 'maths', 'patience', 'compassion', 'animation',
         'designing', 'determination', 'accuracy', 'discipline',
         'enthusiasm', 'problem-solving', 'flexibility', 'creativity',
         'analytics', 'psychology'],
        ['leadership', 'flexibility', 'social', 'time management',
         'discipline', 'history', 'observation', 'critical-thinking',
         'ethics', 'designing ', 'accuracy', 'photography', 'communication',
         'problem-solving', 'teamwork', 'creativity', 'sensitivity',
         'analytical', 'supportive', 'dance'],
        ['analytics', 'adaptability', 'law', 'painting', 'drawing',
         'creativity', 'writing', 'leadership', 'animals', 'persuasion',
         'maths', 'surveillance', 'technical', 'enthusiastic'],
        ['mentoring', 'patience', 'problem-solving', 'social media',
         'critical-thinking', 'editing', 'research', 'open-minded',
         'creativity', 'flexibility', 'organisational', 'discipline',
         'accuracy', 'fitness']
    ]
    # contain the selected choices
    attributes = []

    # question values
    questions = [

        "choose skill1",
        "choose skill2",
        "choose skill3",
        "choose skill4",
        "choose skill5",
        "choose skill6",
    ]
    # for styling (position)
    idx2 = 0

    def send1():
        # function send1 to send question with choices for user
        nonlocal indx, selected_text, attributes, questions, idx2
        global recommendation_distance_thresh

        if indx < 6:
            # we still have questions

            if indx > 0:
                # save the precedent choice
                attributes.append(str(selected_text + '.')[:-1])
                print(attributes, indx)

            # get the selected choice
            def sel():
                nonlocal selected_text
                selected_text = v.get()

            # question label

            label = Label(canvas)
            label.config(text="Bot: " + questions[indx])

            canvas.create_window(160, idx2 * 20, anchor='nw', window=label, height=20)
            idx2 += 1

            # var for radio button
            v = StringVar(canvas, "1")
            # get the possible choice
            valu = values[indx]
            for text in valu:
                # create radio button with the choice
                r1 = Radiobutton(canvas, text=text, variable=v,
                                 value=text,
                                 background="white", command=sel)

                # add the button to the window
                canvas.create_window(160, idx2 * 20, anchor='nw', window=r1, height=20)
                idx2 += 1

            canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scrollbar1.set)

            idx2 += 1

            indx += 1
        elif indx == 6:
            # indx==7 mean last question

            # save the selected choice
            attributes.append(str(selected_text + '.')[:-1])
            print(attributes, indx)

            indx += 1
            # read the course excel file
            df = pd.read_excel('Courses.xlsx')

            # get the indexes of recommended courses with the score (percentage of fitting)
            dic_rec_index = {}

            # get skills for all courses
            skilsss = df[['Attribute2(skill1)', 'Attribute3(skill2)', 'Attribute4(skill3)',
                          'Attribute5(skill4)', 'Attribute6(skill5)', 'Attribute7(skill6)']].values
            # get details of courses
            info = df[['category', 'title', 'overview', 'degree', 'tariff_points', 'ucas_code',
                       'location', 'duration_full_time', 'duration_part_time', 'tuition_fee']].values

            # for each course count its distance compared to user skills
            # small distance mean fit user requirements
            for j in range(len(skilsss)):
                ds = distance.hamming(attributes, skilsss[j])
                if ds <= recommendation_distance_thresh:
                    # get only courses that fit user skills according to recommendation_distance_thresh
                    # recommendation_distance_thresh by default is 0.5 mean 50%
                    dic_rec_index[j] = ds
            print(dic_rec_index)

            i = 1
            # details buttons
            btns = []
            # information of courses
            infoo = []

            # create label for text Recommended Courses
            label = Label(canvas)

            label.config(text="Recommended Courses", bg="white")
            canvas.create_window(160, idx2 * 20, anchor='nw', window=label, height=20)

            # add each course to the window with details button
            for key in dic_rec_index.keys():
                print('***title : ', info[key][1], '\n***overview : ', info[key][2], '\n***fit your skills : ',
                      (1 - dic_rec_index[key]) * 100, '%\n\n')

                # label for courses title and fitting percentage
                label = Label(canvas)
                course_gnr = str(i) + '-' + info[key][1] + '\nfit your skills ' + str(
                    int((1 - dic_rec_index[key]) * 100)) + '%'
                # configure font and background color
                label.config(text=course_gnr, bg="white", foreground="black", font=("Verdana", 9))
                idx2 += 2
                # add label to window
                canvas.create_window(160, idx2 * 20, anchor='nw', window=label, height=40)
                idx2 += 2
                infoo.append(info[key])
                # create details button with details function as command when the user press it
                btns.append(Button(canvas, text='Details', command=lambda c=i: details(infoo[c - 1])))
                i += 1
                canvas.create_window(160, idx2 * 20, anchor='nw', window=btns[-1], height=20)
            # configure scroll bar to fit window size
            canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scrollbar1.set)

    def details(det):
        # take as argument course info
        base2 = Tk()
        # course title as window title
        base2.title(det[1])
        base2.geometry("400x500")
        base2.resizable(width=FALSE, height=FALSE)

        ChatLog2 = Text(base2, bd=0, bg="white", height="8", width=50, font="Arial", )
        ChatLog2.config(state=NORMAL)
        ChatLog2.config(foreground="#442265", font=("Verdana", 12))
        # Category
        ChatLog2.insert(END, "1 - Category\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, det[0] + "\n\n")

        # Overview
        ChatLog2.insert(END, "2 - Overview\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, det[2] + "\n\n")

        # Degree
        ChatLog2.insert(END, "3 - Degree\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, det[3] + "\n\n")

        # tarif_points
        ChatLog2.insert(END, "4 - Tarif points\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, str(det[4]) + "\n\n")

        # ucas_code
        ChatLog2.insert(END, "5 - Ucas code\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, det[5] + "\n\n")

        # location
        ChatLog2.insert(END, "6 - Location\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, det[6] + "\n\n")
        # duration full time
        ChatLog2.insert(END, "7 - Duration full time\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, det[7] + "\n\n")

        # duration part time
        ChatLog2.insert(END, "8 - Duration part time\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, det[8] + "\n\n")
        # tuition fees
        ChatLog2.insert(END, "9 - Tuition fees\n")

        ChatLog2.config(foreground="#440065", font=("Verdana", 9))
        ChatLog2.insert(END, det[9] + "\n\n")

        ChatLog2.config(state=DISABLED)

        # Bind scrollbar to Chat window
        scrollbar2 = Scrollbar(base2, command=ChatLog2.yview, cursor="heart")
        ChatLog2['yscrollcommand'] = scrollbar2.set

        scrollbar2.place(x=376, y=6, height=486)
        ChatLog2.place(x=6, y=6, height=486, width=370)

        # ChatLog2.config(state=DISABLED)
        ChatLog2.yview(END)

        base2.mainloop()

    # recommendation window
    base1 = Tk()
    # title
    base1.title("Recommendation")
    base1.geometry("400x500")
    base1.resizable(width=FALSE, height=FALSE)

    # Create canvas window that will contain questions,choices,recommended courses
    canvas = Canvas(base1, bg="white", height="8", width="50")
    # scrollbar
    scrollbar1 = Scrollbar(base1, orient='vertical', command=canvas.yview)

    # Bind scrollbar to Chat window

    canvas['yscrollcommand'] = scrollbar1.set

    # Create Button to send message
    send_button1 = Button(base1, font=("Verdana", 12, 'bold'), text="Send", width="12", height=5,
                          bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                          command=send1)

    # Create the box to enter message

    # Place all components on the screen
    scrollbar1.place(x=376, y=6, height=386)
    canvas.place(x=6, y=6, height=386, width=370)
    send_button1.place(x=6, y=401, height=90, width=388)
    send1()
    base1.mainloop()


# distance threshold (use while recommendation) 0.7 mean the course should fit 30% of user skills
recommendation_distance_thresh = 0.7

# main window
base = Tk()
base.title("Chatbot")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

# Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width=50, font="Arial", )

ChatLog.config(state=DISABLED)

# Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

# Create Button to send message
SendButton = Button(base, font=("Verdana", 12, 'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                    command=send)

# Create the box to enter message
EntryBox = Text(base, bd=0, bg="white", width=29, height="5", font="Arial")
EntryBox.bind("<Return>", send)

# Place all components on the screen
scrollbar.place(x=376, y=6, height=386)
ChatLog.place(x=6, y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

base.mainloop()
