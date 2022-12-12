/**
 * Authors: Aidan Shine, Bryan Li, Jarvis Jia, Peter Bryant, Swathi Annamaneni, Tong Yang
 * Revision History: 11/01/2022:12/12/2022
 * Organization: Madgers
 * Version: 1.0.0
 */

import React, { useEffect, useState } from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Header from "./Header";
import { useParams } from "react-router-dom";
import GPAGraph from "./GPAGraph";
import Reddit from "./Reddit";
import ProfessorList from "./ProfessorList";

// Course: displays Header and all course info: basic course info,
//    cumulative GPA graph, list of reddit comments, and info on instructors
//    that teach that course.
const Course = () => {
  const courseID = useParams().id; // get the value of the id param

  const [courseInfo, setCourseInfo] = useState({}); // useState hook to store the courseInfo
  const [redditList, setRedditList] = useState([]); // useState hook to store the redditList
  const [graphInfo, setGraphInfo] = useState({}); // useState hook to store the graphInfo
  const [professorList, setProfessorList] = useState([]); // useState hook to store the professorList
  const [profGraphInfo, setProfGraphInfo] = useState([]); // useState hook to store the profGraphInfo

  // fetch course info for a particular courseID
  useEffect(() => {
    fetch("http://3.145.22.97/course-info/" + courseID).then((response) =>
      response.json().then((json) => {
        setCourseInfo(json);
      })
    );
  }, [courseID]);

  // fetch professor graph info for a particular courseInfo, courseID to be used in fetching from /course-profs
  useEffect(() => {
    fetch("http://3.145.22.97/grade-distribution/" + courseID)
      .then((response) =>
        response.json().then((json) => {
          if (json && json["professor_cumulative_grade_distribution"]) {
            // if the response is valid
            setProfGraphInfo(json["professor_cumulative_grade_distribution"]);
          } else setProfGraphInfo({});
        })
      )
      .catch((e) => console.log("error while calling grade-distribution API"));
  }, [courseInfo, courseID]);

  // fetch professor list and professor GPA info for a particular profGraphInfo, courseID to be used in ProfessorList component
  useEffect(() => {
    fetch("http://3.145.22.97/course-profs/" + courseID)
      .then((response) =>
        response.json().then((json) => {
          var professors = [];
          // for each professor in the json response, create a new object with the professor name, rate my professor rating, department, overall score (bad / good), and the graph properties
          for (var key in json) {
            const name = json[key].name;
            const RMPRating = json[key].RMPRating;
            const dept = json[key].dept;
            const RMPRatingClass = json[key].RMPRatingClass;
            const id = key;

            let graph = {};
            if (profGraphInfo.hasOwnProperty(id)) {
              const temp = profGraphInfo[id];
              // if the graph is empty
              if (
                temp.aCount === 0 &&
                temp.abCount === 0 &&
                temp.bCount === 0 &&
                temp.bcCount === 0 &&
                temp.cCount === 0 &&
                temp.dCount === 0 &&
                temp.fCount === 0
              )
                graph = [];
              else
                graph = [
                  { name: "A", grade: temp.aCount ?? 0 },
                  { name: "AB", grade: temp.abCount ?? 0 },
                  { name: "B", grade: temp.bCount ?? 0 },
                  { name: "BC", grade: temp.bcCount ?? 0 },
                  { name: "C", grade: temp.cCount ?? 0 },
                  { name: "D", grade: temp.dCount ?? 0 },
                  { name: "F", grade: temp.fCount ?? 0 },
                ];
            }
            professors.push({
              // push the new object to the professors list
              name,
              RMPRating,
              dept,
              RMPRatingClass,
              id,
              graph,
            });
          }
          setProfessorList(professors);
        })
      )
      .catch((e) => console.log("error while calling course-profs API", e));
  }, [profGraphInfo, courseID]);

  // fetch Reddit comments for a particular courseInfo, courseID to be used in Reddit component, sorting by popularity
  useEffect(() => {
    fetch("http://3.145.22.97/reddit-comments/" + courseID).then((response) =>
      response.json().then((json) => {
        var comments = [];
        // for each comment in the json response, create a new object with the comment body, comment link, and number of votes
        for (var key in json) {
          const id = key;
          const body = json[key].comBody;
          const link = json[key].comLink;
          const votes = json[key].comVotes;

          comments.push({ id, body, link, votes }); // push the new object to the comments list
        }
        comments.sort((a, b) => {
          // Sorting in descending order based on upvotes
          return b.votes - a.votes;
        });
        setRedditList(comments);
      })
    );
  }, [courseInfo, courseID]);

  // fetch overall gpa graph info for a particular courseInfo, courseID
  // The returned gpa graph distribution for this course is converted into the
  //    required format for our graph API
  useEffect(() => {
    fetch("http://3.145.22.97/grade-distribution/" + courseID).then(
      (response) =>
        response.json().then((json) => {
          if (json && json.cumulative) {
            // if the graph is empty
            if (
              json.cumulative.aCount === 0 &&
              json.cumulative.abCount === 0 &&
              json.cumulative.bCount === 0 &&
              json.cumulative.bcCount === 0 &&
              json.cumulative.cCount === 0 &&
              json.cumulative.dCount === 0 &&
              json.cumulative.fCount === 0
            )
              setGraphInfo([]);
            else
              setGraphInfo([
                { name: "A", grade: json.cumulative.aCount },
                { name: "AB", grade: json.cumulative.abCount },
                { name: "B", grade: json.cumulative.bCount },
                { name: "BC", grade: json.cumulative.bcCount },
                { name: "C", grade: json.cumulative.cCount },
                { name: "D", grade: json.cumulative.dCount },
                { name: "F", grade: json.cumulative.fCount },
              ]);
          } else setGraphInfo([]);
        })
    );
  }, [courseInfo, courseID]);

  return (
    <Container className="full">
      <Row>
        <Header />
      </Row>

      <Container className="grey-box full">
        {/* Course Name */}
        <Row>
          <h3 className="bold-heading-style">{courseInfo.cName}</h3>
        </Row>

        {/* Course Code */}
        <Row className="heading-style">
          <h3>{courseInfo.cCode}</h3>
        </Row>

        {/* Course Subject */}
        <Row>
          <Col>
            <Row>
              <h5 className="bold-heading-style">Subject</h5>
            </Row>
            <Row>
              <h5 className="heading-style">{courseInfo.cSubject}</h5>
            </Row>
          </Col>

          {/* Course Credits */}
          <Col>
            <Row>
              <h5 className="bold-heading-style">Credits</h5>
            </Row>
            <Row>
              <h5 className="heading-style">{courseInfo.cCredits}</h5>
            </Row>
          </Col>
        </Row>

        {/* Course Description */}
        <Row>
          <h5 className="bold-heading-style">Description</h5>
        </Row>
        <Row>
          <h5 className="heading-style">{courseInfo.cDescription}</h5>
        </Row>

        {/* Course Requisites */}
        <Row>
          <h5 className="heading-style">
            <b>Requisites</b>
            {": " + courseInfo.cReq}
          </h5>
        </Row>

        {/* Cumulative Course GPA Graph */}
        <Row>
          {graphInfo &&
          graphInfo.length > 0 &&
          redditList &&
          redditList.length > 0 ? (
            <Col>
              {graphInfo && graphInfo.length > 0 ? (
                <div xs={12} lg={6} className="graph-box">
                  <GPAGraph graphInfo={graphInfo} />
                </div>
              ) : (
                <></>
              )}

              {redditList && redditList.length > 0 ? (
                <Row xs={12} md={6} className="reddit-box">
                  <Reddit redditList={redditList} />
                </Row>
              ) : (
                <></>
              )}
            </Col>
          ) : (
            <></>
          )}

          {/* Professor List and Associating Professor GPA Graph(s) */}
          {professorList && professorList.length > 0 ? (
            <Col xs={12} lg={6}>
              <Row>
                <h5 className="bold-heading-style">Instructors</h5>
              </Row>
              <Row xs={12} lg={6} className="professor-list-container">
                {<ProfessorList professorList={professorList} />}
              </Row>
            </Col>
          ) : (
            <>
              <h5 className="heading-style">
                No Intructor Info found for this course
              </h5>
            </>
          )}
        </Row>
      </Container>
    </Container>
  );
};

export default Course;
