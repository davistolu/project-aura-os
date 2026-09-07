import urllib.request
import urllib.parse
import json
import re
import math

class ExternalServices:
    """
    Live External API Connectors for Weather, Currency, Web Search, Science, and Music.
    All connectors use free, high-availability public APIs with zero API keys required.
    """

    @staticmethod
    def get_weather(location="auto") -> dict:
        """Fetch live real-time weather forecast"""
        try:
            loc = location.strip() if location and location != "auto" else ""
            url = f"https://wttr.in/{urllib.parse.quote(loc)}?format=j1" if loc else "https://wttr.in/?format=j1"
            
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                current = data.get("current_condition", [{}])[0]
                area = data.get("nearest_area", [{}])[0]
                city = area.get("areaName", [{}])[0].get("value", "your area")
                country = area.get("country", [{}])[0].get("value", "")

                temp_c = current.get("temp_C", "N/A")
                temp_f = current.get("temp_F", "N/A")
                desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
                humidity = current.get("humidity", "N/A")
                wind = current.get("windspeedKmph", "N/A")

                return {
                    "success": True,
                    "city": city,
                    "country": country,
                    "temp_c": temp_c,
                    "temp_f": temp_f,
                    "description": desc,
                    "humidity": humidity,
                    "wind_kmh": wind,
                    "text": f"The weather in {city} is currently {desc} with a temperature of {temp_c}°C ({temp_f}°F), {humidity}% humidity, and wind at {wind} km/h."
                }
        except Exception as e:
            return {
                "success": False,
                "text": "I was unable to retrieve live weather data at this moment. Please check your internet connection."
            }

    @staticmethod
    def convert_currency(amount: float, from_curr: str, to_curr: str) -> dict:
        """Fetch live forex exchange rates and perform conversion"""
        try:
            from_c = from_curr.upper().strip()
            to_c = to_curr.upper().strip()
            url = f"https://open.er-api.com/v6/latest/{from_c}"

            req = urllib.request.Request(url, headers={"User-Agent": "ProjectAura/1.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("result") == "success":
                    rates = data.get("rates", {})
                    rate = rates.get(to_c)
                    if rate:
                        converted = round(amount * rate, 2)
                        return {
                            "success": True,
                            "amount": amount,
                            "from": from_c,
                            "to": to_c,
                            "converted": converted,
                            "rate": rate,
                            "text": f"{amount:,.2f} {from_c} is currently equal to {converted:,.2f} {to_c} (Exchange rate: 1 {from_c} = {rate:.4f} {to_c})."
                        }
                    else:
                        return {"success": False, "text": f"Currency code '{to_c}' not found in exchange database."}
        except Exception as e:
            pass

        return {"success": False, "text": "Unable to fetch live currency exchange rates right now."}

    @staticmethod
    def web_search_knowledge(query: str) -> dict:
        """Live search via Wikipedia API and DuckDuckGo Instant Knowledge API"""
        # 1. Try Wikipedia summary API first for comprehensive definitions
        try:
            wiki_query = re.sub(r'^(who is|what is|tell me about|define|search for)\s*', '', query, flags=re.I).strip()
            encoded = urllib.parse.quote(wiki_query)
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "ProjectAura/1.0 (aura@personal-os.internal)"})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                if "extract" in data and data["extract"]:
                    title = data.get("title", wiki_query)
                    extract = data["extract"]
                    # Shorten extract to 2-3 concise sentences for vocal speech
                    sentences = extract.split(". ")
                    concise = ". ".join(sentences[:3]) + ("." if not sentences[0].endswith(".") else "")
                    return {
                        "success": True,
                        "title": title,
                        "summary": concise,
                        "text": f"{title}: {concise}"
                    }
        except Exception:
            pass

        # 2. Fallback to DuckDuckGo Instant API
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
            req = urllib.request.Request(url, headers={"User-Agent": "ProjectAura/1.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                abstract = data.get("AbstractText")
                if abstract:
                    return {
                        "success": True,
                        "title": data.get("Heading", query),
                        "summary": abstract,
                        "text": abstract
                    }
        except Exception:
            pass

        return {
            "success": False,
            "text": f"I couldn't locate specific live encyclopedic records for '{query}'."
        }

    @staticmethod
    def solve_math_science(expression: str) -> dict:
        """Scientific calculator, unit converter, and physics constants"""
        expr = expression.lower().strip()

        # Scientific Constants
        constants = {
            "speed of light": ("299,792,458 meters per second", "c ≈ 3.00 × 10⁸ m/s"),
            "gravitational constant": ("6.674 × 10⁻¹¹ N·m²/kg²", "G"),
            "planck's constant": ("6.626 × 10⁻³⁴ J·s", "h"),
            "electron mass": ("9.109 × 10⁻³¹ kg", "m_e"),
            "avogadro's number": ("6.022 × 10²³ particles per mole", "N_A"),
            "pi": ("3.141592653589793", "π"),
        }

        for k, (val, symb) in constants.items():
            if k in expr:
                return {
                    "success": True,
                    "text": f"The {k} ({symb}) is {val}."
                }

        # Unit Conversions
        # e.g., "convert 100 miles to km", "50 kg to pounds", "32 celsius to fahrenheit"
        m_c2f = re.search(r'(\d+(?:\.\d+)?)\s*(?:degrees?\s*)?(?:c|celsius)\s*to\s*(?:f|fahrenheit)', expr)
        if m_c2f:
            c = float(m_c2f.group(1))
            f = round((c * 9/5) + 32, 2)
            return {"success": True, "text": f"{c}°C is equal to {f}°F."}

        m_f2c = re.search(r'(\d+(?:\.\d+)?)\s*(?:degrees?\s*)?(?:f|fahrenheit)\s*to\s*(?:c|celsius)', expr)
        if m_f2c:
            f = float(m_f2c.group(1))
            c = round((f - 32) * 5/9, 2)
            return {"success": True, "text": f"{f}°F is equal to {c}°C."}

        m_m2k = re.search(r'(\d+(?:\.\d+)?)\s*(?:miles?)\s*to\s*(?:km|kilometers?)', expr)
        if m_m2k:
            mi = float(m_m2k.group(1))
            km = round(mi * 1.60934, 2)
            return {"success": True, "text": f"{mi} miles is equal to {km} kilometers."}

        m_kg2lb = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)\s*to\s*(?:lbs?|pounds?)', expr)
        if m_kg2lb:
            kg = float(m_kg2lb.group(1))
            lbs = round(kg * 2.20462, 2)
            return {"success": True, "text": f"{kg} kg is equal to {lbs} pounds."}

        # Advanced Math Evaluator
        cleaned = re.sub(r'^(calculate|what is|compute|solve)\s*', '', expr).strip()
        cleaned = cleaned.rstrip("?.,! ").replace("^", "**").replace("×", "*").replace("÷", "/")
        try:
            # Safe math environment
            safe_dict = {
                "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "log": math.log, "log10": math.log10, "exp": math.exp, "pi": math.pi, "e": math.e,
                "pow": math.pow, "abs": abs, "round": round
            }
            if re.match(r'^[\d\.\s\+\-\*\/\(\)\,\w]+$', cleaned):
                result = eval(cleaned, {"__builtins__": None}, safe_dict)
                return {"success": True, "result": result, "text": f"{expression} equals {result}."}
        except Exception:
            pass

        return {"success": False, "text": "Unable to compute mathematical expression."}

    @staticmethod
    def search_song(query: str) -> dict:
        """Search song information, artists, and album via iTunes Search API"""
        try:
            song_term = re.sub(r'^(who sings|play song|song|music|who wrote)\s*', '', query, flags=re.I).strip()
            encoded = urllib.parse.quote(song_term)
            url = f"https://itunes.apple.com/search?term={encoded}&entity=song&limit=1"
            req = urllib.request.Request(url, headers={"User-Agent": "ProjectAura/1.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("resultCount", 0) > 0:
                    track = data["results"][0]
                    name = track.get("trackName")
                    artist = track.get("artistName")
                    album = track.get("collectionName")
                    year = track.get("releaseDate", "")[:4]
                    return {
                        "success": True,
                        "track": name,
                        "artist": artist,
                        "album": album,
                        "year": year,
                        "text": f"Found '{name}' by {artist} from the album '{album}' ({year})."
                    }
        except Exception:
            pass

        return {"success": False, "text": f"No song information found matching '{query}'."}
