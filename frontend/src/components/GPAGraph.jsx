import React from "react";
import { LineChart, YAxis, XAxis, Line, ResponsiveContainer } from "recharts";

const data = [
  {
    name: "A",
    grade: 13,
  },
  {
    name: "B",
    grade: 20,
  },
  {
    name: "C",
    grade: 17,
  },
  {
    name: "D",
    grade: 9,
  },
  {
    name: "F",
    grade: 2,
  },
];

const GPAGraph = () => {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart width={500} height={300} data={data}>
        <XAxis dataKey="name" />
        <YAxis dataKey="grade" />
        <Line type="monotone" dataKey="grade" stroke="#FF7787" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default GPAGraph;
