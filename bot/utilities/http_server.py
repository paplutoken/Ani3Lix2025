import asyncio
import logging
import json
from urllib.parse import urlparse, parse_qs

class HTTPServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.links = [
            {"name": "Ani3Lix Chat", "url": "https://t.me/Anim3chat"},
            {"name": "Join My Telegram", "url": "https://t.me/Ani3lix_clan"},
            {"name": "Ongoing Anime Episodes", "url": "https://t.me/Ongoing_Anime_Episodes"},
            {"name": "MyAnimeList", "url": "https://myanimelist.net"},
            {"name": "AniList", "url": "https://anilist.co"},
            {"name": "Crunchyroll", "url": "https://www.crunchyroll.com"},
            {"name": "Funimation", "url": "https://www.funimation.com"},
            {"name": "Netflix Anime", "url": "https://www.netflix.com/browse/genre/7424"}
        ]

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            request = await reader.read(1024)
            if not request:
                return

            request_line = request.decode().splitlines()[0]
            self.logger.info("Received request: %s", request_line)

            method, full_path, _ = request_line.split(" ")

            parsed_url = urlparse(full_path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            if path == "/":
                response = self.render_index()
            elif path == "/api/links":
                response = self.get_links_json()
            elif path == "/api/search":
                search_query = query_params.get("q", [""])[0].lower()
                response = self.search_links(search_query)
            else:
                response = self.render_404()

            writer.write(response.encode())
            await writer.drain()
        except ConnectionResetError:
            self.logger.info("Connection lost")
        finally:
            writer.close()
            await writer.wait_closed()

    def render_index(self) -> str:
        """Returns the main page with search and scrolling functionality."""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ani3Lix</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center; background-color: #f0f0f0; }
                .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); }
                h1 { color: #333; }
                a { display: block; margin: 10px 0; padding: 10px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-size: 1.2em; }
                a:hover { background-color: #0056b3; }
                input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; }
                #links { margin-top: 20px; }
            </style>
            <script>
                async function searchLinks() {
                    let query = document.getElementById('search').value;
                    let response = await fetch('/api/search?q=' + encodeURIComponent(query));
                    let data = await response.json();
                    displayLinks(data.links);
                }

                function displayLinks(links) {
                    let container = document.getElementById('links');
                    container.innerHTML = "";
                    links.forEach(link => {
                        let a = document.createElement('a');
                        a.href = link.url;
                        a.textContent = link.name;
                        a.target = "_blank";
                        container.appendChild(a);
                    });
                }

                async function loadMoreLinks() {
                    let response = await fetch('/api/links');
                    let data = await response.json();
                    displayLinks(data.links);
                }

                window.onload = loadMoreLinks;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Ani3Lix</h1>
                <p>Welcome To Ani3Lix</p>

                <input type="text" id="search" onkeyup="searchLinks()" placeholder="Search links...">

                <h2>🔗 Links</h2>
                <div id="links"></div>
            </div>
        </body>
        </html>
        """
        return "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html_content

    def get_links_json(self) -> str:
        """ Returns JSON response dynamically """
        json_response = json.dumps({"links": self.links}, indent=4)
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{json_response}"

    def search_links(self, query: str) -> str:
        """ Filters links based on the search query """
        filtered_links = [link for link in self.links if query in link["name"].lower()]
        json_response = json.dumps({"links": filtered_links}, indent=4)
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{json_response}"

    def render_404(self) -> str:
        """ Returns 404 error page dynamically """
        return "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>"

    async def run_server(self) -> None:
        server = await asyncio.start_server(self.handle_request, self.host, self.port)
        self.logger.info("Serving on %s:%d", self.host, self.port)
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = HTTPServer("0.0.0.0", 8080)  # 0.0.0.0 allows external access
    asyncio.run(server.run_server())
