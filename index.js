// Import required modules
const express = require("express");
const path = require("path");
const cors = require("cors");
const fs = require("fs");
const bodyParser = require("body-parser");
require("dotenv").config();

// Import custom modules
const {
  getAirportData,
  getMultipleStationsMetar,
  getMultipleMetarWithTaf,
  getPirepsNearStation,
  getPirepsWithinDistance,
  getSigmets,
  getAirmets,
  getDiscussion,
} = require("./src/app");

const { MongoClient } = require("mongodb");

const mongoClient = new MongoClient(process.env.MONGO_CONNECTION);

async function connect() {
  await mongoClient.connect();
}

async function disconnect() {
  await mongoClient.close();
}

async function withDbConnection(fn) {
  try {
    await connect();
    return await fn();
  } catch (error) {
    console.error(`Error connecting to the database: ${error}`);
  } finally {
    await disconnect();
  }
}

// Initialize Express application
const app = express();

// Set the port number
const PORT = process.env.PORT || 3000;

// Configure Express to parse JSON
app.use(bodyParser.json());

// Configure CORS options
const corsOptions = {
  origin: "https://chat.openai.com",
  optionsSuccessStatus: 200, // For compatibility with legacy browsers (IE11, various SmartTVs)
};

// Use CORS middleware with the specified options
app.use(cors(corsOptions));

// Middleware to capture the response body
app.use((req, res, next) => {
  var oldWrite = res.write,
    oldEnd = res.end;

  var chunks = [];

  res.write = function (chunk) {
    chunks.push(chunk);

    oldWrite.apply(res, arguments);
  };

  res.end = function (chunk) {
    if (chunk) chunks.push(chunk);

    var body = Buffer.concat(chunks).toString("utf8");
    console.log(req.path, body);

    res.body = body; // Here's the body

    oldEnd.apply(res, arguments);
  };

  next();
});

// Middleware to log requests and responses
app.use(async (req, res, next) => {
  const start = Date.now();
  next();
  const ms = Date.now() - start;

  const log = {
    method: req.method,
    url: req.url,
    status: res.statusCode,
    length: res.get("Content-Length"),
    responseTime: ms,
    requestBody: req.body,
    responseBody: res.body,
    timestamp: new Date(),
  };

  await withDbConnection(async () => {
    const db = mongoClient.db("AeroDex_plugin"); // replace with your database name
    await db.collection("logs").insertOne(log);
  });
});

// Define content types for different file extensions
const contentTypes = {
  ".json": "application/json",
  ".yaml": "text/yaml",
};

// Function to read a file and send its contents as a response
const readFileAndSend = (filePath, res, contentType) => {
  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      console.error(`Error reading file: ${err}`);
      return res.status(500).send("An error occurred while reading the file.");
    }
    res.setHeader("Content-Type", contentType);
    res.send(data);
  });
};

// Route to serve the plugin manifest
app.get("/.well-known/ai-plugin.json", (req, res) => {
  readFileAndSend(
    path.join(__dirname, ".well-known/ai-plugin.json"),
    res,
    contentTypes[".json"]
  );
});

// Route to serve the OpenAPI schema
app.get("/openapi.yaml", (req, res) => {
  readFileAndSend(
    path.join(__dirname, "openapi.yaml"),
    res,
    contentTypes[".yaml"]
  );
});

// Route to serve the logo image
app.get("/logo.jpg", (req, res) => {
  res.sendFile(path.join(__dirname, "logo.png"));
});

// Route to fetch airport data
app.post("/airport-data", async (req, res) => {
  const city = req.body.city;
  try {
    const data = await getAirportData(city);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching  data: ${error}`);
    res.status(500).send("Error occurred while fetching  data");
  }
});

// Route to fetch multiple stations metar
app.post("/multiple-stations-metar", async (req, res) => {
  console.log("Calling metar only");
  const stations = req.body.stations;
  try {
    const data = await getMultipleStationsMetar(stations);
    //console.log(data);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching metar data: ${error}`);
    res.status(500).send("Error occurred while fetching metar data");
  }
});

// Route to fetch metar with taf
app.post("/metar-with-taf", async (req, res) => {
  console.log("Calling metar with taf");
  const stations = req.body.stations;
  try {
    const data = await getMultipleMetarWithTaf(stations);
    //console.log(data);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching metar data: ${error}`);
    res.status(500).send("Error occurred while fetching metar data");
  }
});

// Route to fetch pireps based on station
app.post("/get-pireps-standard", async (req, res) => {
  console.log("Calling pireps");
  const station = req.body.station;
  try {
    const data = await getPirepsNearStation(station);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching  data: ${error}`);
    res.status(500).send("Error occurred while fetching pireps");
  }
});

// Route to fetch pireps based on station and range
app.post("/get-pireps-within-range", async (req, res) => {
  console.log("Calling pireps with range");
  const station = req.body.station;
  const range = req.body.range;
  try {
    const data = await getPirepsWithinDistance(station, range);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching  data: ${error}`);
    res.status(500).send("Error occurred while fetching pireps");
  }
});

// Route to fetch sigmets
app.post("/get-sigmet", async (req, res) => {
  console.log("Calling sigmets");
  try {
    const data = await getSigmets();
    res.json(data);
  } catch (error) {
    console.error(`Error fetching  data: ${error}`);
    res.status(500).send("Error occurred while getting Sigmets");
  }
});

// Route to fetch airmets
app.post("/get-airmet", async (req, res) => {
  console.log("Calling airmet");
  try {
    const data = await getAirmets();
    res.json(data);
  } catch (error) {
    console.error(`Error fetching  data: ${error}`);
    res.status(500).send("Error occurred while getting Sigmets");
  }
});

// Route to fetch forecast discussion
app.post("/forecast-discussion", async (req, res) => {
  console.log("Calling discussion");
  const code = req.body.code;
  try {
    const data = await getDiscussion(code);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching  data: ${error}`);
    res.status(500).send("Error occurred while fetching  data");
  }
});

// Default route for unimplemented methods and paths
app.all("/*", (req, res) => {
  res
    .status(501)
    .send(`Method ${req.method} not implemented for path ${req.path}`);
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
