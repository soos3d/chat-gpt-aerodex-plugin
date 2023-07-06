// Import required modules
const dotenv = require("dotenv");
const axios = require("axios");

// Load environment variables from .env file
dotenv.config();

// Retrieve API key from environment variables
const API_KEY = process.env.AIRPORTS_API_KEY;

/**
 * Fetches airport data for a given city using the API Ninjas Airports API.
 *
 * @param {string} city - The city for which to fetch airport data.
 * @returns {Promise<Object>} The airport data for the specified city.
 * @throws {Error} If an error occurs during the API request.
 */
async function getAirportData(city) {
  const options = {
    method: "GET",
    url: `https://api.api-ninjas.com/v1/airports?name=${city}`,
    headers: {
      "X-Api-Key": API_KEY,
    },
  };

  try {
    const response = await axios.request(options);
    return response.data;
  } catch (error) {
    console.error(
      `An error occurred while fetching airport data: ${error.response.data}`
    );
    throw error;
  }
}

const BASE_URL = "https://beta.aviationweather.gov";

async function getMultipleStationsMetar(airportCodes) {
  try {
    const ids = airportCodes.join(",");
    const response = await axios.get(
      `${BASE_URL}/cgi-bin/data/metar.php?ids=${ids}&format=decoded`
    );

    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error(`An error occurred while fetching weather data: ${error}`);
    throw error;
  }
}

async function getMultipleMetarWithTaf(airportCodes) {
  try {
    const ids = airportCodes.join(",");
    const [metarResponse, tafResponse] = await Promise.all([
      axios.get(`${BASE_URL}/cgi-bin/data/metar.php?ids=${ids}&format=decoded`),
      axios.get(`${BASE_URL}/cgi-bin/data/metar.php?ids=${ids}&taf=on`),
    ]);

    // Split the taf response into an array at each newline, remove the first element, and join it back into a string
    const cleanedTaf = tafResponse.data.split("\n").slice(1).join("\n");

    // Combine the responses
    const combinedResponse = {
      metar: metarResponse.data,
      taf: cleanedTaf,
    };

    console.log(combinedResponse);
    return combinedResponse;
  } catch (error) {
    console.error(`An error occurred while fetching weather data: ${error}`);
    throw error;
  }
}

async function getPirepsNearStation(airportCode) {
  try {
    const response = await axios.get(
      `${BASE_URL}/cgi-bin/data/pirep.php?id=${airportCode}&format=decoded`
    );

    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error(`An error occurred while fetching weather data: ${error}`);
    throw error;
  }
}

async function getPirepsWithinDistance(airportCode, range) {
  try {
    const response = await axios.get(
      `${BASE_URL}/cgi-bin/data/pirep.php?id=${airportCode}&format=decoded&distance=${range}`
    );

    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error(`An error occurred while fetching weather data: ${error}`);
    throw error;
  }
}

function parseWeatherMets(weatherMetsString) {
  const splitIndex = weatherMetsString.indexOf("AIRMET for");

  const sigmetString = weatherMetsString.slice(0, splitIndex);
  const airmetString = weatherMetsString.slice(splitIndex);

  const sigmets = sigmetString
    ? sigmetString
        .trim()
        .split("SIGMET for")
        .slice(1)
        .map((s) => "SIGMET for" + s)
    : [];
  const airmets = airmetString
    ? airmetString
        .trim()
        .split("AIRMET for")
        .slice(1)
        .map((a) => "AIRMET for" + a)
    : [];

  return { sigmets, airmets };
}

async function getSigmets() {
  try {
    const response = await axios.get(
      `${BASE_URL}/cgi-bin/data/airsigmet.php?format=decoded`
    );

    const { sigmets, airmets } = parseWeatherMets(response.data);
    console.log("SIGMETs:", sigmets);
    const result = { sigmets: sigmets };
    console.log(result);
    return result;
  } catch (error) {
    console.error(`An error occurred while fetching weather data: ${error}`);
    throw error;
  }
}

async function getAirmets() {
  try {
    const response = await axios.get(
      `${BASE_URL}/cgi-bin/data/airsigmet.php?format=decoded`
    );

    const { sigmets, airmets } = parseWeatherMets(response.data);
    console.log("AIRMETSs:", airmets);
    const result = { airmets: airmets };
    console.log(result);
    return result;
  } catch (error) {
    console.error(`An error occurred while fetching weather data: ${error}`);
    throw error;
  }
}

async function getDiscussion(code) {
  try {
    console.log(code);
    const response = await axios.get(
      `${BASE_URL}/cgi-bin/data/fcstdisc.php?cwa=k${code}`
    );

    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error(`An error occurred while fetching weather data: ${error}`);
    throw error;
  }
}

module.exports = {
  getAirportData,
  getMultipleStationsMetar,
  getMultipleMetarWithTaf,
  getPirepsNearStation,
  getPirepsWithinDistance,
  getSigmets,
  getAirmets,
  getDiscussion,
};
