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

# source for lines 17-26: https://github.com/shantnu/RedditBot/blob/master/Part2/reply_post.py
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
yosemite_shorthand_regex="1\d[abcdABCD](\/[abcdABCD])?[+-]?"


def comment(grade, submission, convertedGrade):
    if submission.id not in do_not_comment:
        # only comment if converted grade is not already in the title
        if not re.search(convertedGrade, submission.title):
            print("commenting: **" + grade + "** converts to **" + convertedGrade + "**")
            submission.reply("**" + grade + "** converts to **" + convertedGrade + "**")
        do_not_comment.append(submission.id)

# If u/MountainProjectBot already commented, ignore this post
def search_for_proj_bot(submission):
    submission.comments.replace_more(limit=0)
    for top_level_comment in submission.comments:
        if top_level_comment.author == "MountainProjectBot":
            print("found a comment by MountainProjectBot: " + top_level_comment.body)
            do_not_comment.append(submission.id)

def find_grade_in_title(submission, regex, conversion, prefix=""):
    title_found = re.search(regex, submission.title)
    if title_found:
        grade = prefix + title_found.group(0).lower()
        if grade in conversion:
            print("grade in title found: " + submission.title)
            search_for_proj_bot(submission)
            comment(grade, submission, conversion[grade])

subreddit = reddit.subreddit("climbing")
for submission in subreddit.new(limit=15):
    find_grade_in_title(submission, yosemite_shorthand_regex, NAtoEU, "5.")
    find_grade_in_title(submission, yosemite_grades_regex, NAtoEU)
    find_grade_in_title(submission, french_grades_regex, EUtoNA)

with open("do_not_comment.txt", "w") as f:
    for post_id in do_not_comment:
        f.write(post_id + "\n")
