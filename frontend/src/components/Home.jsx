import React from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Header from "./Header";
import Search from "./Search";

// Home: This component is the homepage for Madger Course, with a large title
//    and search bar where users can search by course or instructor. It also
//    uses the Header component at the top.
const Home = () => {
  return (
    <Container className="full">
      <Row>
        <Header />
      </Row>
      <Container className="pink-box">
        <Row>
          <h1>Madger Courses</h1>
        </Row>
        <Row>
          <h4>Detailed Course information at your fingertips</h4>
        </Row>
        <Row>
          <div class="rbt-home">
            <Search />
          </div>
        </Row>
      </Container>
    </Container>
  );
};

export default Home;
