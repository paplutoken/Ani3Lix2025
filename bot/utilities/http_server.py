import asyncio
import logging


class HTTPServer:
    """
    A simple HTTP server class.

    Parameters:
    host (str): The host to bind the server to.
    port (int): The port to bind the server to.
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handle an incoming HTTP request.

        Parameters:
        reader (asyncio.StreamReader): The reader object to read the request from.
        writer (asyncio.StreamWriter): The writer object to write the response to.
        """
        try:
            request = await reader.read(1024)
            if not request:
                return

            self.logger.info("Received request: %s", request.decode().splitlines()[0])

            path = request.decode().split(" ")[1]
            if path == "/":
                response_body = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teleshare</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            text-align: center;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
        }
        a {
            display: block;
            margin: 10px 0;
            padding: 10px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 1.2em;
        }
        a:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Teleshare</h1>
        <p>Your hub for sharing links and anime updates!</p>
        
        <h2>🔗 Links</h2>
        <a href="https://t.me/Anim3chat" target="_blank">Ani3Lix Chat</a>
        <a href="https://t.me/Ani3lix_clan" target="_blank">Join My Telegram</a>
        <a href="https://t.me/Ongoing_Anime_Episodes" target="_blank">Visit Ani3Lix (Ongoing Anime Episodes)</a>
        
        <h2>🔥 Latest Anime Updates</h2>
        <p>Check out the latest episodes and news!</p>
        <a href="https://myanimelist.net" target="_blank">MyAnimeList</a>
        <a href="https://anilist.co" target="_blank">AniList</a>
        
        <footer>
            <p>&copy; 2025 Ani3Lix | Created by The Fool</p>
        </footer>
    </div>
</body>
</html>
"""
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{response_body}"
            else:
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>"

            writer.write(response.encode())
            await writer.drain()
        except ConnectionResetError:
            self.logger.info("Connection lost")
        finally:
            writer.close()
            await writer.wait_closed()

    async def run_server(self) -> None:
        """
        Run the HTTP server.
        """
        server = await asyncio.start_server(self.handle_request, self.host, self.port)
        self.logger.info("Serving on %s:%d", self.host, self.port)
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = HTTPServer("127.0.0.1", 8080)
    asyncio.run(server.run_server())
