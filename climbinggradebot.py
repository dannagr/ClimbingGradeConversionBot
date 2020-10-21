import csv
import os
import praw
import re

reddit = praw.Reddit('climbingbot')

NAtoEU = {}
EUtoNA= {}
with open('gradeconversions.csv', 'rt') as csvfile:
    grades = csv.reader(csvfile, delimiter=',')
    for row in grades:
        NAtoEU[row[0]] = row[1]
        EUtoNA[row[1]] = row[0]

# source: https://github.com/shantnu/RedditBot/blob/master/Part2/reply_post.py
if not os.path.isfile("do_not_comment.txt"):
    do_not_comment = []

# If we have run the code before, load the list of posts we have replied to
else:
    # Read the file into a list and remove any empty values
    with open("do_not_comment.txt", "r") as f:
        do_not_comment = f.read()
        do_not_comment = do_not_comment.split("\n")
        do_not_comment = list(filter(None, do_not_comment))

# ex: 7c+
french_grades_regex="[4-9][abcABC][+]?"
# ex: 5.9
yosemite_grades_regex="[5][.]\d\d?[abcdABCD]?[+-]?"
# ex: 10a/b
yosemite_shorthand_regex="1\d[abcdABCD]?[abcdABCD]?(\/[abcdABCD])?[+-]?"


def comment(grade, submission, conversion):
    if submission.id not in do_not_comment:
        # print("**" + grade + "** converts to **" + conversion[grade] + "**")
        submission.reply("**" + grade + "** converts to **" + conversion[grade] + "**")
        do_not_comment.append(submission.id)

def find_grade_in_title(submission, regex, conversion, prefix=""):
    title_found = re.search(regex, submission.title)
    if title_found:
        grade = prefix + title_found.group(0).lower()
        if grade in conversion:
            comment(grade, submission, conversion)


subreddit = reddit.subreddit("slabistheworst")
for submission in subreddit.hot(limit=5):
    find_grade_in_title(submission, yosemite_shorthand_regex, NAtoEU, "5.")
    find_grade_in_title(submission, yosemite_grades_regex, NAtoEU)
    find_grade_in_title(submission, french_grades_regex, EUtoNA)


with open("do_not_comment.txt", "w") as f:
    for post_id in do_not_comment:
        f.write(post_id + "\n")
        