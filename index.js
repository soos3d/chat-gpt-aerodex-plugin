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

async function logData(endpoint, requestBody, headers, response) {
  // Get the database and collection
  const db = mongoClient.db("AeroDex");
  const collection = db.collection("logs");

  // Define the document to insert
  const document = {
    endpoint: endpoint,
    requestBody: requestBody,
    headers: {
      host: headers.host,
      userAgent: headers["user-agent"],
      secChUaPlatform: headers["sec-ch-ua-platform"],
      openaiEphemeralUserId: headers["openai-ephemeral-user-id"],
      openaiConversationId: headers["openai-conversation-id"],
    },
    response: response,
    timestamp: new Date(),
  };

  // Insert the document into the collection
  try {
    await collection.insertOne(document);
    console.log(`Logged data for endpoint ${endpoint}`);
  } catch (error) {
    console.error(`Error logging data for endpoint ${endpoint}: ${error}`);
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
  console.log("Calling airport data");
  const city = req.body.city;
  try {
    const data = await getAirportData(city);
    console.log(data);
    await logData("/airport-data", req.body, data);

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

  // Get headers
  const headers = req.headers;

  try {
    const data = await getMultipleStationsMetar(stations);
    //console.log(data);
    await logData("/multiple-stations-metar", req.body, headers, data);
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

  // Get headers
  const headers = req.headers;

  try {
    const data = await getMultipleMetarWithTaf(stations);
    await logData("/metar-with-taf", req.body, headers, data);
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

  // Get headers
  const headers = req.headers;

  try {
    const data = await getPirepsNearStation(station);
    await logData("/pireps", req.body, headers, data);
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

  // Get headers
  const headers = req.headers;

  try {
    const data = await getPirepsWithinDistance(station, range);
    await logData("/pireps-range", req.body, headers, data);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching  data: ${error}`);
    res.status(500).send("Error occurred while fetching pireps");
  }
});

// Route to fetch sigmets
app.post("/get-sigmet", async (req, res) => {
  console.log("Calling sigmets");

  // Get headers
  const headers = req.headers;

  try {
    const data = await getSigmets();
    await logData("/sigmets", req.body, headers, data);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching  data: ${error}`);
    res.status(500).send("Error occurred while getting Sigmets");
  }
});

// Route to fetch airmets
app.post("/get-airmet", async (req, res) => {
  console.log("Calling airmet");

  // Get headers
  const headers = req.headers;
  try {
    const data = await getAirmets();
    await logData("/airmet", req.body, headers, data);
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
    await logData("/forecast-discussion", req.body, data);
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
app.listen(PORT, async () => {
  try {
    await mongoClient.connect();
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log("Connected to MongoDB");
  } catch (error) {
    console.error(`Failed to connect to MongoDB: ${error}`);
  }
});

// Event listeners for server shutdown
process.on("SIGINT", closeDatabaseConnection);
process.on("SIGTERM", closeDatabaseConnection);
process.on("SIGUSR2", closeDatabaseConnection); // For nodemon restarts

// Function to close the MongoDB connection
async function closeDatabaseConnection() {
  try {
    await mongoClient.close();
    console.log("MongoDB connection closed");
    process.exit(0);
  } catch (error) {
    console.error(`Error closing MongoDB connection: ${error}`);
    process.exit(1);
  }
}
