# Needed Python Libraries
import requests
import json
import mysql.connector
# Custom MadGrades Script for Grade Distributions
import madgrades as mg
# PRAW: Python Reddit API Wrapper
import praw
from praw.models import MoreComments
# Public & Modified RMP API for Professor Data
from RMP.ratemyprof_api import RateMyProfApi
# Application Configuration (Private) Information
import config

# Documentation Reference: README Subsection 1.1

# Establish connection to MySQL DB
conn = mysql.connector.connect(
   user = config.user,
   password = config.password, 
   host = config.host,
   database = config.database
)

# Instantiate an instance of PRAW's Reddit object
reddit = praw.Reddit(client_id = config.PRAW_client_id, 
                    client_secret = config.PRAW_client_secret,
                    username = config.r_username, 
                    password = config.r_password,
                    user_agent = config.PRAW_user_agent)

# Instantiate PRAW Subreddit Object for r/UWMadison
uwmadison_subreddit = reddit.subreddit('UWMadison')

# Instantiate UW-Madison RateMyProfessor Object (DOCS: 1.1.2.1)
uwm_rmp_sid_1 = "1256"  # RMP School ID #1
uwm_rmp_sid_2 = "18418" # RMP School ID #2

api_1 = RateMyProfApi(uwm_rmp_sid_1, testing = True) # (DOCS: 1.1.2.2)
api_2 = RateMyProfApi(uwm_rmp_sid_2, testing = True)

# TODO: PopCourses() is finished!
# (DOCS: 1.1.1.1)
def PopCourses():
    """
    Function to populate the courses table with all courses at UW-Madison.
    Entries contain a cUID, the course's name, the course's subject, the course's code, the course's credits, and the course's description.
    """

    file = open('sample.json', 'r') # Open the JSON file containing all UW-Madison courses (pre-scraped)
    data = json.load(file)          # Load the JSON file into a dictionary
    cursor = conn.cursor()          # Create a cursor object to execute SQL queries

    # For each course at UW-Madison, try inserting its course data into the DB
    for key in data.keys():
        cName = data[key]['name']
        cSubject =  data[key]['subject']
        cCode = data[key]['code']
        cCredits = data[key]['credits']
        cDescription = data[key]['description'] 
        cReq = data[key]['requisite']

        try:
            cursor.execute("INSERT INTO courses (cName, cSubject, cCode, cCredits, cDescription, cReq) VALUES (%s, %s, %s, %s, %s, %s)", (cName, cSubject, cCode, cCredits, cDescription, cReq,))
            conn.commit()
        except Exception as e:
            print(e)
            #print("Error inserting course into database")
            
    cursor.close()
    pass

def PopProfessorsHelper(professor_data):
    """
    Helper function to populate the professors table with all professors at UW-Madison.

    """
    cursor = conn.cursor() 

    # Iterating through every UW professor on RMP, and store the information in a String
    for professor in professor_data:
        prof_json = {}                                          
        professor = professor_data[professor]                               
        prof_json['name'] = professor.first_name + " " + professor.last_name 
        prof_json['dept'] = professor.department              
        prof_json['RMPID'] = professor.ratemyprof_id          
        prof_json['RMPRating'] = professor.overall_rating        
        prof_json['RMPTotalRatings'] = professor.num_of_ratings 
        prof_json['RMPRatingClass'] = professor.rating_class
        pData = json.dumps(prof_json)  # Convert the JSON object to a string

        try:
            # Insert course into the database's professors table
            cursor.execute("INSERT INTO professors (pName, pData) VALUES (%s, %s)", (prof_json['name'], pData))
            conn.commit()
        except Exception as e:
            print(e)
            # print("Error inserting professor into database")
      
    cursor.close()
    pass

# TODO: PopProfessors() is finished!
# (DOCS: 1.1.1.2)
def PopProfessors():
    """
    Function to populate the professors table with all professors at UW-Madison. Iterates over the two RMP school IDs and calls the helper function to populate the table.
    Entries contain a pUID, the professor's first name, last name, and pData (where pData is a dictionary of all RateMyProfessor data).

    Sample pData : {'Fname': 'Peter', 'Lname': 'Adamczyk', 'dept': 'Mechanical Engineering', 'RMPID': 2215832, 'RMPRating': 4.9, 'RMPTotalRatings': 12, 'RMPRatingClass': 'good'}
    """
    professors_data = []

    professors_data.append(api_1.scrape_professors()) # (DOCS: 1.1.2.3)
    professors_data.append(api_2.scrape_professors())

    for data in professors_data:
        PopProfessorsHelper(data)
    pass

 # TODO: PopRedditComments() is unfinished. We will need to continually refine how we choose comments to populate the DB with!
# (DOCS: 1.1.1.3)
def PopRedditComments():
    """
    Function to populate the rc (reddit comments) table with all comments that are relevant to a certain course that were posted to r/UWMadison. 
    Entries contain a comment ID, the comment's text, a link to the comment, the comment's upvotes, and the cUID of the course the comment is about.
    """
    cursor = conn.cursor() 

    cursor.execute("SELECT cUID, cName, cCode FROM courses WHERE cName Like 'Introduction to Algorithms'") # Get the cUID, cName, and cCode of all courses
    # cursor.execute("SELECT cUID, cName, cCode FROM courses WHERE cName Like 'PRINCIPLES OF BIOLOGICAL ANTHROPOLOGY'") # Get the cUID, cName, and cCode of all courses
    courses = cursor.fetchall() # Store all course data

    # TODO: FIGURE OUT WHAT SEARCHES TO DO

    # Create a course acronym (DOCS: 1.1.2.4)
    for course in courses:
        cNum = ''.join(filter(str.isdigit, course[2]))  # Extract all numeric characters from the course's code
        search = course[2]
        # Extract the first letter of all alphabetical characters in the course's code
        acronym = ''
        for word in course[2].split():
            if word[0].isalpha():
                acronym += word[0]

        # print(acronym)
        # print(search)
        # search = cNum

        # NEW METHOD: Searching for posts that have either the full course code, or the courses acronym + course number (e.g. CS506 or CS 506)
       
        # Search for submissions that contain the course's code
        for submission in uwmadison_subreddit.search(search, limit=50):
            if search.lower() in submission.title.lower() or acronym + cNum in submission.title or acronym + ' ' + cNum in submission.title: # If the course's code is in the submission's title
                # print(submission.title) # Print the submission's title
                submission.comments.replace_more(limit=5) # Return only the top three comments from the comment tree
                for comment in submission.comments.list():
                    if (comment.score > 2 or cNum in comment.body) and len(comment.body) < 1000:
                        try:
                            # Insert reddit comment into the database's rc table
                            cursor.execute("INSERT INTO rc (cUID, comBody, comLink, comVotes) VALUES (%s, %s, %s, %s)", (course[0], comment.body, reddit_url+comment.permalink, comment.score,))
                            conn.commit()
                        except Exception as e:
                            print(e)
                            print("Error inserting reddit comment into database")

        # OLD METHOD: Our old plan was to search for comments that mentioned the course code/number. This is ineffective because a lot of posts have the course code 
        # in the title but not in the course comment body.

        # Search for comments that mention the substring provided by the user in r/UWMadison
        # for submission in uwmadison_subreddit.search(search, limit=25):
        #     for comment in submission.comments:
        #         if search in comment.body and comment.score > 5 and len(comment.body) < 1000:

        #             try:
        #                 # Insert reddit comment into the database's rc table
        #                 cursor.execute("INSERT INTO rc (cUID, comBody, comLink, comVotes) VALUES (%s, %s, %s, %s)", (course[0], comment.body, reddit_url+comment.permalink, comment.score,))
        #                 conn.commit()
        #             except Exception as e:
        #                 print(e)
        #                 print("Error inserting reddit comment into database")
            
    cursor.close()

    pass

# TODO: PopTeaches() is unfinished. All we have to do it remove "WHERE cName Like 'Introduction to Algorithms'" from first query to populate teaches with all courses!
# (DOCS: 1.1.1.4)
def PopTeaches():
    """
    Function to populate the teaches table with cUIDs and pUIDs for each course. Defining what courses each professor teaches.
    Entries contain a cUID and a pUID.
    """

    cursor = conn.cursor() # Create a cursor object to execute SQL queries

    cursor.execute("SELECT cUID, cCode FROM courses WHERE cName Like 'Introduction to Algorithms'") # Get the cUID, and cCode of all courses
    # cursor.execute("SELECT cUID, cCode FROM courses") # Get the cUID, and cCode of all courses

    courses = cursor.fetchall() 
    
    for course in courses:
        # print(course)
        cUID = course[0]
        cCode = course[1]
        search = cCode
        grade_distributions = mg.MadGrades(search)
        course_professors = []
        all_term_data = []

        # Iterate over all terms in the grade distribution data
        for i in range(len(grade_distributions["courseOfferings"])):
            single_term_data = grade_distributions["courseOfferings"][i]["sections"]
            all_term_data.append(single_term_data)

        # Iterate over all terms in the grade distribution data, and create a list of all professors that teach the course
        num_terms = len(all_term_data)
        for j in range(num_terms):
            for k in range(len(all_term_data[j])):
                course_professors.append(all_term_data[j][k]["instructors"])

        # print(course_professors)

        for professor in course_professors:
            prof_name = professor[0]['name']
            cursor.execute("SELECT pUID from professors where pName Like %s", (prof_name,))
            pUID = cursor.fetchone()
            if pUID is not None:
                try:
                    cursor.execute("INSERT INTO teaches (cUID, pUID) VALUES (%s, %s)", (cUID, pUID[0],))
                    conn.commit()
                except Exception as e:
                    print(e)
                    print("Error inserting into teaches table")
            else:
                print("Professor not found")

    cursor.close()
    pass

def PopDB():
    """
    Function that populated the entire database by calling all Pop Functions.
    """
    PopCourses()
    PopProfessors()
    PopRedditComments()
    PopTeaches()
    return

if __name__ == '__main__':
    # PopDB() # Run all Pop Functions
    # For Testing
    PopCourses()