import asyncio
import logging
import socket
from typing import Optional

class HTTPServer:
    """
    An asynchronous HTTP server.
    """

    def __init__(self, host: str, port: int, max_request_size: int = 1024) -> None:
        """
        Initializes the HTTPServer with a host, port, maximum request size, and logger.

        Args:
            host (str): The hostname or IP address to bind to.
            port (int): The port number to listen on.
            max_request_size (int): The maximum size of the request to read (in bytes).  Defaults to 1024.
        """
        self.host = host
        self.port = port
        self.max_request_size = max_request_size
        self.logger = logging.getLogger(__name__)

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handles an incoming HTTP request.  Reads the request, parses the path,
        and sends an appropriate HTTP response.  Includes robust error handling
        and logging.

        Args:
            reader (asyncio.StreamReader): The stream reader for reading data from the client.
            writer (asyncio.StreamWriter): The stream writer for sending data to the client.
        """
        addr = writer.get_extra_info('peername')
        self.logger.info(f"Connection from {addr}")

        try:
            request = await self._read_request(reader)
            if not request:
                return  # Connection closed prematurely

            request_str = request.decode()
            self.logger.info("Received request: %s", request_str.splitlines()[0])

            try:
                path = self._parse_path(request_str)
            except ValueError as e:
                self.logger.warning(f"Malformed request from {addr}: {e}")
                await self._send_error_response(writer, 400, "Bad Request")
                return

            if path == "/":
                response = self._get_homepage_response()
            else:
                response = self._get_not_found_response()

            await self._send_response(writer, response)

        except ConnectionResetError:
            self.logger.info(f"Connection reset by peer: {addr}")
        except Exception as e:
            self.logger.exception(f"Error handling request from {addr}: {e}")
            await self._send_error_response(writer, 500, "Internal Server Error")
        finally:
            await self._close_connection(writer, addr)

    async def _read_request(self, reader: asyncio.StreamReader) -> Optional[bytes]:
        """
        Reads the HTTP request from the stream reader, up to the maximum request size.

        Args:
            reader (asyncio.StreamReader): The stream reader.

        Returns:
            Optional[bytes]: The request data as bytes, or None if the connection was closed.
        """
        try:
            request = await reader.read(self.max_request_size)
            return request
        except asyncio.exceptions.IncompleteReadError as e:
            self.logger.warning(f"Incomplete read: {e}")
            return e.partial  # Return the partial data, if any
        except Exception as e:
            self.logger.error(f"Error reading request: {e}")
            return None

    def _parse_path(self, request_str: str) -> str:
        """
        Parses the path from the HTTP request string.

        Args:
            request_str (str): The HTTP request string.

        Returns:
            str: The requested path.

        Raises:
            ValueError: If the request is malformed and the path cannot be parsed.
        """
        try:
            return request_str.split(" ")[1]
        except IndexError:
            raise ValueError("Malformed request: missing path")
        except Exception as e:
            raise ValueError(f"Error parsing path: {e}")


    async def _send_response(self, writer: asyncio.StreamWriter, response: str) -> None:
        """
        Sends the HTTP response to the client.

        Args:
            writer (asyncio.StreamWriter): The stream writer.
            response (str): The HTTP response string.
        """
        try:
            writer.write(response.encode())
            await writer.drain()
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")

    async def _send_error_response(self, writer: asyncio.StreamWriter, status_code: int, message: str) -> None:
        """
        Sends an HTTP error response to the client.

        Args:
            writer (asyncio.StreamWriter): The stream writer.
            status_code (int): The HTTP status code.
            message (str): The error message.
        """
        response = f"HTTP/1.1 {status_code} {message}\r\nContent-Type: text/plain\r\n\r\n{message}"
        await self._send_response(writer, response)

    async def _close_connection(self, writer: asyncio.StreamWriter, addr: tuple) -> None:
        """
        Closes the connection with the client.

        Args:
            writer (asyncio.StreamWriter): The stream writer.
            addr (tuple): The client's address.
        """
        try:
            writer.close()
            await writer.wait_closed()
            self.logger.info(f"Connection closed with {addr}")
        except Exception as e:
            self.logger.error(f"Error closing connection with {addr}: {e}")


    def _get_homepage_response(self) -> str:
        """
        Returns the HTTP response for the homepage ("/").  This includes the
        HTML content for the Ani3Lix website.

        Returns:
            str: The HTTP response string.
        """
        html_content = (
            "<!DOCTYPE html>"
            "<html lang='en'>"
            "<head>"
            "<meta charset='UTF-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            "<title>Ani3Lix</title>"
            "<style>"
            "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center; background-color: #f0f0f0; }"
            ".container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); }"
            "h1 { color: #333; }"
            "a { display: block; margin: 10px 0; padding: 10px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-size: 1.2em; }"
            "a:hover { background-color: #0056b3; }"
            "</style>"
            "</head>"
            "<body>"
            "<div class='container'>"
            "<h1>Ani3Lix</h1>"
            "<p>Your hub for sharing links and anime updates!</p>"
            "<h2>🔗 Links</h2>"
            "<a href='https://t.me/Anim3chat' target='_blank'>Ani3Lix Chat</a>"
            "<a href='https://t.me/Ani3lix_clan' target='_blank'>Join My Telegram</a>"
            "<a href='https://t.me/Ongoing_Anime_Episodes' target='_blank'>Ongoing Anime Episodes</a>"
            "<h2>🔥 Latest Anime Updates</h2>"
            "<a href='https://myanimelist.net' target='_blank'>MyAnimeList</a>"
            "<a href='https://anilist.co' target='_blank'>AniList</a>"
            "<footer>"
            "<p>&copy; 2025 Ani3Lix | Created by The Fool</p>"
            "</footer>"
            "</div>"
            "<script src='https://inapp.telega.io/sdk/v1/sdk.js'></script>"
            "<script>"
            "const ads = window.TelegaIn.AdsController.create_miniapp({ token: '170a3bc1-4cb3-4c99-8a30-58c7c44117f0' });"
            "ads.ad_show({ adBlockUuid: '6b346b7a-ff49-43fb-8c23-cbb3e008f836' });"
            "</script>"
            "</body>"
            "</html>"
        )
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            f"{html_content}"
        )
        return response

    def _get_not_found_response(self) -> str:
        """
        Returns the HTTP response for a "404 Not Found" error.

        Returns:
            str: The HTTP response string.
        """
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>"
        return response

    async def run_server(self) -> None:
        """
        Starts the asyncio server and listens for incoming connections.
        """
        try:
            server = await asyncio.start_server(self.handle_request, self.host, self.port)
            addr = server.sockets[0].getsockname()
            self.logger.info(f"Serving on {addr}")

            async with server:
                await server.serve_forever()
        except OSError as e:
            self.logger.error(f"Could not start server: {e}")
        except Exception as e:
            self.logger.critical(f"Unexpected error during server startup: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    server = HTTPServer("127.0.0.1", 8080)
    try:
        asyncio.run(server.run_server())
    except KeyboardInterrupt:
        logging.info("Server shutting down.")
