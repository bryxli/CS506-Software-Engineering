import requests
import json
import math
import os
from .professor import Professor

class RateMyProfApi:
    """
    RateMyProfAPI class contains functions to scrape professor data from RateMyProfessors.com
    """
    def __init__(self, school_id):
        """
        Constructor for RateMyProfApi class.
        Args: school_id (int): ID of the UID that RateMyProfessor assigns to identify schools.
        """
        self.UniversityId = school_id
        

    def ScrapeProfessors(self, testing = False):  # creates List object that include basic information on all Professors from the IDed University
        """
        Scrapes all professors from the school with the given school_id. 
        Return: a list of Professor objects, defined in professor.py.
        """
        if testing:
            print("-------ScrapeProfessors--------")
            print("Scraping professors from RateMyProfessors.com...")
            print("University ID: ", self.UniversityId)
        
        professors = dict() 
        num_of_prof = self.NumProfessors() # The number of professors with RMP records associated with this university school_id.
        
        if testing:
            print("Number of Professors Total: ", num_of_prof)

        num_of_pages = math.ceil(num_of_prof/20)   # The API returns 20 professors per page.
        for i in range(1, num_of_pages + 1):  # the loop insert all professor into list
            
            # print("Scraping page ", i, " of ", num_of_pages, "...")
            request = "http://www.ratemyprofessors.com/filter/professor/?&page=" + str(i) + "&queryoption=TEACHER&query=*&sid=" + str(self.UniversityId)
            page = requests.get(request)

            json_response = json.loads(page.content)

            if json_response['professors'] == []:
                continue

            for json_professor in json_response["professors"]:
    
                # print(json_professor)
                professor = Professor(
                    json_professor["tid"],
                    json_professor["tFname"],
                    json_professor["tLname"],
                    json_professor["tNumRatings"],
                    json_professor["overall_rating"],
                    json_professor["rating_class"],
                    json_professor["tDept"]
                    )

                professors[professor.ratemyprof_id] = professor

        if testing:
            print("Professors actually added: ", str(len(professors)))

        return professors

    def NumProfessors(self):
        """
        Helper function to get the number of professors in the school with the given school_id.
        """
        page = requests.get(
            "http://www.ratemyprofessors.com/filter/professor/?&page=1&queryoption=TEACHER&queryBy=schoolId&sid="
            + str(self.UniversityId)
        )

        temp_jsonpage = json.loads(page.content)
        num_of_prof = (temp_jsonpage["searchResultsTotal"]) 
        return num_of_prof