#!/usr/bin/python

import sys
import requests
import json



def cmpDict(a_dict, a_key, a_val):
    return a_key in a_dict.keys() and a_dict[a_key] == a_val

def chkKey(a_dict, a_key):
    return a_key in a_dict.keys() and a_dict[a_key] != None



if len(sys.argv) != 2:
    if len(sys.argv) > 0: pname = sys.argv[0]
    else: pname = "itmoapi-calculateplace.py"
    print("usage: python " + pname + " \"snils\"")
    print("example: python " + pname + " \"12345678910\"")
    exit(1)



apiURL = "https://abitlk.itmo.ru/api/v1/9e2eee80b266b31c8d65f1dd3992fa26eb8b4c118ca9633550889a8ff2cac429/rating/bachelor/budget?program_id=16002&manager_key="

print("Sending API request... ", end="")
apiAnswer = requests.get(apiURL)
print("done!")

apiAnswerText = apiAnswer.content
apiAnswerParsedData = json.loads(apiAnswerText)

rating = []
unknownList = []

tmpdata = apiAnswerParsedData
if cmpDict(tmpdata, "ok", True) and cmpDict(tmpdata, "message", "ok") and chkKey(tmpdata, "result"):
    tmpdata = tmpdata["result"]
    if chkKey(tmpdata, "without_entry_tests"):
        tmpdata = tmpdata["without_entry_tests"]
        for i in range(len(tmpdata)):
            e = tmpdata[i]
            if chkKey(e, "olympiad") and chkKey(e, "ia_scores") and chkKey(e, "is_have_advantages"):
                if "победитель" in e["olympiad"].lower() or "призер" in e["olympiad"].lower() or "призёр" in e["olympiad"].lower(): # I don't think that the third one has ever used but let it be here
                    levelOfOlymp = int("III" in e["olympiad"]) + int("II" in e["olympiad"]) + int("I" in e["olympiad"])
                    if levelOfOlymp > 0:
                        place = int(e["is_have_advantages"])*10000 + int("победитель" in e["olympiad"].lower())*1000 + (3 - levelOfOlymp)*100 + e["ia_scores"]
                        rating.append([20000 - place, i]) # (20000-place) for reversed sorting
                        continue
            unknownList.append(i)
        noCriticalApiErrors = True

if not noCriticalApiErrors:
    print("An error in API answer detected")
    exit(2)

rating.sort()

print("Total count: " + str(len(rating) + len(unknownList)))
print("Failed to check due to API errors: " + str(len(unknownList)))
print("="*10)

userplace = 0
for i in range(len(rating)):
    if cmpDict(tmpdata[rating[i][1]], "snils", sys.argv[1]):
        userplace = i+1
        break
if userplace == 0:
    for i in range(len(unknownList)):
        if cmpDict(tmpdata[unknownList[i]], "snils", sys.argv[1]):
            userplace = -(i+1)
            break
if userplace == 0:
    print("You are not in the list. It can be an error (less-likely) so you better check at abit.itmo.ru.")
elif userplace < 0:
    print("An error ocurred during calculating place for you (some data has not provided by API), check youself at abit.itmo.ru.")
    if chkKey(tmpdata[unknownList[-userplace-1]], "position"):
        print("By the way, your position at abit.itmo.ru is " + str(tmpdata[unknownList[-userplace-1]]["position"]) + ".")
else:
    sameCnt = -1
    for e in rating:
        if e[0] == rating[userplace-1][0]:
            sameCnt += 1
    print("=== Now your place in sorted list is ", end="")
    if sameCnt > 0:
        print("in range [" + str(userplace) + ";" + str(userplace+sameCnt) + "]", end="")
    else:
        print(str(userplace), end="")
    print(" of " + str(len(rating)) + " (not including " + str(len(unknownList)) + " entries with errors).")
    print("Your data:")
    checklist = ["snils", "case_number", "is_have_advantages", "olympiad", "ia_scores", "is_send_original", "send_agreement", "position", "priority"]
    for e in checklist:
        print(e + ": ", end="")
        if chkKey(tmpdata[rating[userplace-1][1]], e):
            print(tmpdata[rating[userplace-1][1]][e])
        else:
            print("(an error ocurred)")
