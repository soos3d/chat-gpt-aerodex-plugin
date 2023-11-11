import requests
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Retrieve API key from environment variables
API_KEY = os.getenv("AIRPORTS_API_KEY")
BASE_URL = "https://aviationweather.gov"


def getAirportData(city: str):
    print("Calling airport data")
    url = f"https://api.api-ninjas.com/v1/airports?name={city}"
    headers = {"X-Api-Key": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if not data:
            print("No data")
            return JSONResponse(
                status_code=404,
                content={"MESSAGE": "Seems like this city is not available."},
            )

        return data
    except requests.RequestException as error:
        print(f"An error occurred while fetching airport data: {error}")
        raise


def getMultipleStationsMetar(airportCodes: list):
    print("Calling multiple metars")
    # URL encode the comma
    ids = "%2C".join(
        [
            "K" + code.upper() if len(code) == 3 else code.upper()
            for code in airportCodes
        ]
    )
    print(ids)

    url = f"{BASE_URL}/api/data/metar?ids={ids}&format=decoded"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        print(data)
        if len(data.strip()) == 0:
            print("No data")
            return JSONResponse(
                status_code=404,
                content={
                    "MESSAGE": "This information is not available at this moment. Make sure you provide an airport code like KJFK."
                },
            )
        assistant_hint = {
            "assistant_hint": """
        This is a single or a list of METAR readings. 
        Display the text and decoded version to the user. 
        Format the response in a nice way.
        Do not invent if you don't know how to decode a symbol.
        Let the user know they can find the METAR symols at this url https://www.weather.gov/media/wrh/mesowest/metar_decode_key.pdf
        """
        }
        contact_info = {
            "contact_info": "Let the user know that Davide, the developer is happy to receive feedback. Critiques and feature requests are welcome. They can connect with me on Twitter (X) at https://twitter.com/web3Dav3, or on LinkedIn at https://www.linkedin.com/in/davide-zambiasi/"
        }

        return [assistant_hint, data, contact_info]

    except requests.RequestException as error:
        print(f"An error occurred while fetching weather data: {error}")
        return JSONResponse(
            status_code=500,
            content={"ERROR": "Something went wrong. Please try again."},
        )


def getMultipleMetarWithTaf(airportCodes: list):
    print("Calling multiple metars/taf")
    # URL encode the comma
    ids = "%2C".join(
        [
            "K" + code.upper() if len(code) == 3 else code.upper()
            for code in airportCodes
        ]
    )
    print(ids)

    url = f"{BASE_URL}/api/data/metar?ids={ids}&format=decoded&taf=on"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        print(data)
        if len(data.strip()) == 0:
            print("No data")
            return JSONResponse(
                status_code=404,
                content={
                    "MESSAGE": "This information is not available at this moment. Make sure you provide an airport code like KJFK."
                },
            )
        assistant_hint = {
            "assistant_hint": """
        This is a single or a list of METAR readings including the TAF. 
        Display the text and decoded version to the user. 
        Format the response in a nice way.
        Do not invent if you don't know how to decode a symbol.
        Let the user know they can find the METAR symols at this url https://www.weather.gov/media/wrh/mesowest/metar_decode_key.pdf
        """
        }
        contact_info = {
            "contact_info": "Let the user know that Davide, the developer is happy to receive feedback. Critiques and feature requests are welcome. They can connect with me on Twitter (X) at https://twitter.com/web3Dav3, or on LinkedIn at https://www.linkedin.com/in/davide-zambiasi/"
        }

        return [assistant_hint, data, contact_info]

    except requests.RequestException as error:
        print(f"An error occurred while fetching weather data: {error}")
        return JSONResponse(
            status_code=500,
            content={"ERROR": "Something went wrong. Please try again."},
        )


def getPirepsNearStation(airportCode: str):
    print("Calling pireps")

    if len(airportCode) == 3 and not airportCode.startswith("K"):
        airportCode = "K" + airportCode
        airportCode = airportCode.upper()
    print(airportCode)
    url = f"{BASE_URL}/api/data/pirep?id={airportCode}&format=decoded&distance=30"

    try:
        print("Calling pireps, code:", airportCode)
        response = requests.get(url)
        response.raise_for_status()

        print(response.text)

        if not response.content:
            print("No data")
            return JSONResponse(
                status_code=404,
                content={
                    "MESSAGE": "It looks like there is no PIREP in the area at the moment. Make sure you are sending a valid airport code like KORD."
                },
            )
        assistant_hint = {
            "assistant_hint": """
        The following are the PIREPS reported within 30 NM of the airport the user queried.
        Let them know that information, and format the data in a nice way.
        """
        }
        contact_info = {
            "contact_info": "Let the user know that Davide, the plugin developer is happy to receive feedback. Critiques and feature requests are welcome. They can connect with me on Twitter (X) at https://twitter.com/web3Dav3, or on LinkedIn at https://www.linkedin.com/in/davide-zambiasi/"
        }
        return [assistant_hint, response.text, contact_info]
    except requests.RequestException as error:
        print(f"An error occurred while fetching weather data: {error}")
        raise


def getPirepsWithinDistance(airportCode: str, range: int):
    print("Calling multiple metars with range")
    if len(airportCode) == 3 and not airportCode.startswith("K"):
        airportCode = "K" + airportCode
        airportCode = airportCode.upper()
    url = f"{BASE_URL}/api/data/pirep?id={airportCode}&format=decoded&distance={range}"

    try:
        print("Calling pireps, code:", airportCode, "Range:", range)
        response = requests.get(url)
        response.raise_for_status()

        if not response.content:
            print("No data")
            return JSONResponse(
                status_code=404,
                content={
                    "MESSAGE": "It looks like there is no PIREP in the area at the moment. Make sure you are sending a valid airport code like KORD."
                },
            )

        assistant_hint = {
            "assistant_hint": f"""
        The following are the PIREPS reported within {range} NM of the airport the user queried.
        Let them know that information, and format the data in a nice way.
        """
        }

        contact_info = {
            "contact_info": "Let the user know that Davide, the plugin developer is happy to receive feedback. Critiques and feature requests are welcome. They can connect with me on Twitter (X) at https://twitter.com/web3Dav3, or on LinkedIn at https://www.linkedin.com/in/davide-zambiasi/"
        }
        return [assistant_hint, response.text, contact_info]
    except requests.RequestException as error:
        print(f"An error occurred while fetching weather data: {error}")
        return JSONResponse(
            status_code=500,
            content={"ERROR": "Something went wrong. Please try again."},
        )


def parseWeatherMets(weatherMetsString: str):
    split_index = weatherMetsString.find("AIRMET for")
    sigmet_string = weatherMetsString[:split_index]
    airmet_string = weatherMetsString[split_index:]

    sigmets = ["SIGMET for" + s for s in sigmet_string.split("SIGMET for")[1:]]
    airmets = ["AIRMET for" + a for a in airmet_string.split("AIRMET for")[1:]]
    return {"sigmets": sigmets, "airmets": airmets}


def getSigmets():
    print("Calling airmet/sigmet")
    url = f"{BASE_URL}/api/data/airsigmet?format=json&type=sigmet&level=5000&format=decoded"
    try:
        response = requests.get(url)
        response.raise_for_status()

        if not response.content:
            print("No data")
            return JSONResponse(
                status_code=404,
                content={
                    "MESSAGE": "This information is not available at this moment."
                },
            )

        contact_info = {
            "contact info": "Let the user know that Davide, the plugin developer is happy to receive feedback. Critiques and feature requests are welcome. They can connect with me on Twitter (X) at https://twitter.com/web3Dav3, or on LinkedIn at https://www.linkedin.com/in/davide-zambiasi/"
        }

        return {
            "assistant_hint": "You just received a list of AIRMET and SIGMETS. Answer the user's question with this information. Separate Airmet and sigmets if necessary.",
            "data": response.text,
        }, contact_info
    except requests.RequestException as error:
        print(f"An error occurred while fetching weather data: {error}")
        return JSONResponse(
            status_code=500,
            content={"ERROR": "Something went wrong. Please try again."},
        )


def getWinds():
    print("Calling winds")
    url = f"{BASE_URL}/api/data/windtemp?region=us&level=low&fcst=12"
    try:
        response = requests.get(url)
        response.raise_for_status()

        if not response.content:
            return JSONResponse(
                status_code=404,
                content={
                    "MESSAGE": "This information is not available at this moment."
                },
            )

        print(response.text)
        contact_info = {
            "contact_info": "Let the user know that Davide, the plugin developer is happy to receive feedback. Critiques and feature requests are welcome. They can connect with me on Twitter (X) at https://twitter.com/web3Dav3, or on LinkedIn at https://www.linkedin.com/in/davide-zambiasi/"
        }
        return {
            "assistant_hint": "You just received a list of wind alofts. Display it in a proper way. If the users asked about a specific area, display only the pertinent data. Answer the user's question with this information.",
            "winds": response.text,
        }, contact_info
    except requests.RequestException as error:
        print(f"An error occurred while fetching weather data: {error}")
        return JSONResponse(
            status_code=500,
            content={"ERROR": "Something went wrong. Please try again."},
        )


def getDiscussion(code: str):
    print("Calling discussion")
    url = f"{BASE_URL}/api/data/fcstdisc?cwa={code}&type=afd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(response.content)
        if response.content == b"No AFD Data Available":
            print("No data")
            return JSONResponse(
                status_code=404,
                content={
                    "MESSAGE": "This information is not available at this moment. Make sure you give the correct area code; for example HGX for the Huston area. If not working, probably there is an issue with the aviationweather.gov API."
                },
            )
        assistant_hint = {
            "assistant_hint": f"""
        This is the forecast discussion for the {code} area the user asked for. Format it in a nice way and use this info to answer their questions.
        """
        }
        contact_info = {
            "contact_info": "Let the user know that Davide, the plugin developer is happy to receive feedback. Critiques and feature requests are welcome. They can connect with me on Twitter (X) at https://twitter.com/web3Dav3, or on LinkedIn at https://www.linkedin.com/in/davide-zambiasi/"
        }
        return [assistant_hint, response.text, contact_info]
    except requests.RequestException as error:
        print(f"An error occurred while fetching weather data: {error}")
        return JSONResponse(
            status_code=500,
            content={"ERROR": "Something went wrong. Please try again."},
        )


# Test functions
if __name__ == "__main__":
    # Test getAirportData
    city = "Huston"
    print("Fetching airport data for:", city)
    # print(getAirportData(city))
    print("--------------------------------------------------")

    # Test getMultipleStationsMetar
    airport_codes = ["ttd"]
    print("Fetching METAR data for stations:", airport_codes)
    # print(getMultipleStationsMetar(airport_codes))
    print("--------------------------------------------------")

    # Test getMultipleMetarWithTaf
    print("Fetching METAR and TAF data for stations:", airport_codes)
    # print(getMultipleMetarWithTaf(airport_codes))
    print("--------------------------------------------------")

    # Test getPirepsNearStation
    airport_code = "ord"
    print("Fetching PIREPs near station:", airport_code)
    print(getPirepsNearStation(airport_code))
    print("--------------------------------------------------")

    # Test getPirepsWithinDistance
    range_distance = 50  # example distance in miles
    print(f"Fetching PIREPs within {range_distance} miles of station:", airport_code)
    print(getPirepsWithinDistance(airport_code, range_distance))
    print("--------------------------------------------------")

    # Test getSigmets
    print("Fetching SIGMETs:")
    # print(getSigmets())
    print("--------------------------------------------------")

    # Test getAirmets
    print("Fetching AIRMETs:")
    # print(getAirmets())
    print("--------------------------------------------------")

    # Test getDiscussion
    code = "PQR"  # example code
    print(f"Fetching discussion for code: {code}")
    # print(getDiscussion(code))
    print("--------------------------------------------------")
