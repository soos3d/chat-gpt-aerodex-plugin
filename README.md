# AeroDex ChatGPT Plugin

This is the code powering the AeroDex ChatGPT plugin. This app fetches different kind of aviation weather informaion from the [aviationweather.gov API](https://beta.aviationweather.gov/data/example/). It also uses the [airport API](https://api-ninjas.com/api/airports) from API-Ninjas to get airport information.

> Check out the website and try it on ChatGPT.
> ... coming soon...

## Project details

This is a JavaScript project using `axios` to send `GET` requests to the aviationweather.gov API. The server for ChatGPT is an Express.js server running various `POST` endpoints.

This ChatGPT plugin can get the following data:

- **Latest METAR Data**: The `multipleStationsMetar` function returns the latest METAR (Meteorological Aerodrome Report) data for a single or multiple weather stations specified by the user. METAR data includes information about temperature, dew point, wind speed and direction, precipitation, cloud cover, visibility, and barometric pressure.

- **METAR and TAF Data**: The `metarWithTaf` function returns both METAR and TAF (Terminal Aerodrome Forecast) data for the specified weather stations. TAFs are weather forecasts that are issued four times daily for airports around the world.

- **PIREPs within 200 sm**: The `getPireps` function returns PIREPs (Pilot Reports) reported within 200 sm (statute miles) from the specified station. PIREPs are reports of actual weather conditions encountered by pilots.

- **PIREPs within Specified Range**: The `getPirepsWithRange` function returns PIREPs reported within a user-specified range from the station.

- **Airport Data**: The `airportData` function returns details of airports present in the city specified by the user.

- **Active SIGMETs**: The `getSigmets` function returns the decoded active SIGMETs (Significant Meteorological Information). SIGMETs are weather advisories issued for significant weather events that are potentially hazardous to all aircraft.

- **Active AIRMETs**: The `getAirmets` function returns the decoded active AIRMETs (Aeronautical Information Reports). AIRMETs are weather advisories that cover smaller areas than SIGMETs and are typically issued for weather conditions like turbulence, icing, and low visibility.

- **Forecast Discussion**: The `forecastDiscussion` function returns the forecast discussion for an area specified by the user. Forecast discussions provide a narrative from a meteorologist about the current weather situation and the reasoning behind the issued forecasts.

> ⚠️
> Please be aware that while the data provided by the AeroDex plugin is sourced from the aviationweather.gov API, it should not be used as the sole resource for flight planning and decision-making. Always consult official and certified weather briefings from trusted sources before making any aviation-related decisions.

## Quickstart

1. Clone the repository:

```sh
git clone https://github.com/soos3d/chat-gpt-aerodex-plugin.git
```

2. Install dependencies:

```sh
npm install
```

3. Edit `.env.sample` file:

Edit the `.env.sample` file to add your API Ninjas API key, then rename it to `.env`.

Get your API key on the [API Ninjas website](https://api-ninjas.com/api).

4. Serve the plugin:

```sh
node index
```

The plugin is now running on `http://localhost:3333`

- Optional: I recommend utilizing Nodemon for your server applications for a smoother development process. This tool offers the convenience of automatic server restarts whenever changes are saved, enhancing your efficiency and productivity.

```sh
npm install -g nodemon # or using yarn: yarn global add nodemon
```

- Serve the plugin with

```sh
nodemon index
```

5. Install the plugin in ChatGPT:

Navigate to the **Plugin Store** and select the **Develop your own plugin** option. In the provided field, enter `localhost:3333`. The system will then locate the manifest and the OpenAPI schema, installing the plugin for you.

## How Does a ChatGPT Plugin Work?

The operation of a ChatGPT plugin is straightforward and can be broken down into four key components:

1. **An application**: There is an application that performs a specific function. This could range from executing an API call to retrieve data or interact with other services to implementing various types of logic, such as performing arithmetic operations or even handling more complex tasks.

2. **A server**: There is a server with endpoints that facilitate communication with your application and invoke its functions. ChatGPT interacts with the plugin through this server.

3. **OpenAPI Schema**: This is a comprehensive documentation of the available server endpoints. ChatGPT uses this schema to understand the plugin's capabilities and determine when to call a specific endpoint.

4. **Plugin manifest**: A JSON file that contains detailed information about the plugin. It provides ChatGPT with a clear understanding of the plugin's purpose and functionality and the URLs needed to locate the server and the logo.

Upon installing a plugin via the ChatGPT user interface, the system establishes a connection to the server, locates the manifest and the OpenAPI schema, and subsequently prepares the plugin for use.

## The ChatGPT plugin structure

The fundamental structure of this plugin is outlined below. Please note that it can be tailored to meet your specific requirements.

```sh
root-directory
│
├── .well-known
│   └── ai-plugin.json
│
├── src
│   └── app.js
│
├── .env
│
├── index.js
│
├── openapi.yaml
│
└── logo.png

```

In this structure:

- .well-known/ai-plugin.json is the plugin manifest.
- src/app.js is the main application file.
- .env is the environment variables file.
- index.js is the main server file.
- openapi.yaml is the OpenAPI schema.
- logo.png is the logo of the plugin.

## The server

The server is the `index.js` file.

This code sets up a simple Express.js server with various endpoints to serve a ChatGPT plugin. Here's a step-by-step breakdown:

1. The code begins by importing the necessary modules, including Express, path, cors (for handling Cross-Origin Resource Sharing neessery for ChatGPT to find the plugin), fs (for file system operations), and body-parser (for parsing incoming request bodies). It also imports a custom module, `getAirportData`, from `./src/app`.

2. The Express application is initialized, and the port number is set based on the environment variable `PORT` or defaults to 3000 if `PORT` is not set.

3. The application is configured to parse JSON in the body of incoming requests using `bodyParser.json()`.

4. CORS is configured to allow requests from `https://chat.openai.com` and to send a 200 status code for successful preflight requests for compatibility with some older browsers.

5. A helper function, `readFileAndSend`, is defined. This function reads a file and sends its contents as a response with the appropriate content type.

6. Several routes are set up:

   - The `/.well-known/ai-plugin.json` route serves the plugin manifest.
   - The `/openapi.yaml` route serves the OpenAPI schema.
   - The `/logo.jpg` route serves the plugin's logo image.
   - The various endpoints to interact with the APIs.

7. A catch-all route is set up to handle any other requests. This route sends a 501 status code and a message indicating that the requested method and path are not implemented.

8. Finally, the server is started and listens for requests on the specified port. A message is logged to the console indicating that the server is running and on which port.

This serves as the heart of the plugin, enabling ChatGPT to establish a connection, locate the manifest and OpenAPI schema to comprehend its functionality, and ultimately access the endpoints that interact with the application.

## The OpenAPI schema

The OpenAPI schema, also known as an OpenAPI specification, is a powerful tool for describing and documenting APIs. It's a standard, language-agnostic specification for RESTful APIs, which allows both humans and computers to understand the capabilities of a service without needing to access the source code, additional documentation, or network traffic inspection.

In an OpenAPI schema, you define all the aspects of your API. This includes:

1. **Endpoints (Paths)**: These are the routes or URLs where your API can be accessed. For example, in a weather API, you might have an endpoint like `/weather` to get the current weather.

2. **Operations**: These are the actions that can be performed on each endpoint, such as GET, POST, PUT, DELETE, etc. Each operation will have its parameters, request body, and responses defined.

3. **Parameters and Request Body**: These define what data can be passed to the API, either as part of the URL, as query parameters, or in the body of a POST or PUT request.

4. **Response**: This defines what the API returns after an operation, including various status codes, headers, and the body of the response.

5. **Models (Schemas)**: These are definitions of the data structures that the API uses. For example, a User model might include fields for the user's name, email, and password.

By using an OpenAPI schema, developers can understand how to use your API without having to read through all your code or rely on extensive external documentation. It also enables the use of automated tools for tasks like generating code, testing, or creating interactive API documentation.

> The 'description' field of the endpoint serves as a prompt for ChatGPT, providing an area where you can include additional details. Please be aware that this field has a character limit of 300.

## The plugin manifest

The manifest file is a JSON file that provides essential information about the plugin to ChatGPT. Here's a breakdown of what each field represents:

- `schema_version`: This field indicates the version of the schema that the plugin is using.

- `name_for_human`: This is the name of the plugin as it should be displayed to humans.

- `name_for_model`: This is the name of the plugin as it should be referred to by the model.

- `description_for_human`: This is a description of the plugin for humans. It should provide a clear explanation of what the plugin does.

- `description_for_model`: This is a description of the plugin for the model. It should provide a clear explanation of what the plugin does.

- `auth`: This field describes the type of authentication required by the plugin. In this case, it's "none", meaning no authentication is required.

- `api`: This field provides information about the API used by the plugin. It includes the type of API (in this case, "openapi"), the URL where the OpenAPI schema can be found, and a boolean indicating whether user authentication is required.

- `logo_url`: This is the URL where the logo for the plugin can be found.

- `contact_email`: This is the contact email for the developer or team responsible for the plugin.

- `legal_info_url`: This is the URL where legal information about the plugin can be found. In this case, it's empty.

> Find more information on the [OpenAI docs](https://platform.openai.com/docs/plugins/introduction).
