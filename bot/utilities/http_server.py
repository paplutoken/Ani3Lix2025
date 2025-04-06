import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class AnimeUpdate:
    def __init__(self, title: str, episode: int, date: str, link: str):
        self.title = title
        self.episode = episode
        self.date = date
        self.link = link

class HTTPServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.routes = {
            "/": self.handle_home,
            "/anime": self.handle_anime,
            "/about": self.handle_about,
            "/favicon.ico": self.handle_favicon
        }
        
        # Sample anime updates - in a real app these would come from a database
        self.anime_updates = [
            AnimeUpdate("One Piece", 1114, "April 5, 2025", "https://myanimelist.net/anime/21/One_Piece"),
            AnimeUpdate("Jujutsu Kaisen", 45, "April 4, 2025", "https://myanimelist.net/anime/40748/Jujutsu_Kaisen"),
            AnimeUpdate("Demon Slayer", 32, "April 3, 2025", "https://myanimelist.net/anime/38000/Kimetsu_no_Yaiba"),
            AnimeUpdate("My Hero Academia", 126, "April 2, 2025", "https://myanimelist.net/anime/31964/Boku_no_Hero_Academia"),
            AnimeUpdate("Bleach: Thousand-Year Blood War", 18, "April 1, 2025", "https://myanimelist.net/anime/41467/Bleach__Sennen_Kessen-hen")
        ]

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            request_data = await reader.read(1024)
            if not request_data:
                return

            request = request_data.decode()
            request_line = request.splitlines()[0]
            self.logger.info("Received request: %s", request_line)
            
            # Parse request method and path
            parts = request_line.split(" ")
            if len(parts) < 2:
                response = self.create_error_response(400, "Bad Request")
            else:
                method, path = parts[0], parts[1]
                
                # Extract query parameters if any
                query_params = {}
                if "?" in path:
                    path_parts = path.split("?", 1)
                    path = path_parts[0]
                    query_string = path_parts[1]
                    for param in query_string.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            query_params[key] = value

                # Route the request
                handler = self.routes.get(path)
                if handler:
                    response = await handler(method, query_params)
                else:
                    response = self.create_error_response(404, "Not Found")

            writer.write(response.encode())
            await writer.drain()
        except Exception as e:
            self.logger.error("Error handling request: %s", str(e))
        finally:
            writer.close()
            await writer.wait_closed()

    async def handle_home(self, method: str, params: Dict) -> str:
        if method != "GET":
            return self.create_error_response(405, "Method Not Allowed")
        
        updates_html = ""
        for update in self.anime_updates:
            updates_html += f'''
            <div class="anime-card">
                <div class="anime-info">
                    <h3>{update.title}</h3>
                    <p>Episode {update.episode} • {update.date}</p>
                </div>
                <a href="{update.link}" target="_blank" class="watch-btn">Watch</a>
            </div>
            '''
            
        return self.render_template("Ani3Lix - Your Anime Hub", f'''
            <header>
                <div class="logo">
                    <h1>Ani3Lix</h1>
                </div>
                <nav>
                    <a href="/" class="active">Home</a>
                    <a href="/anime">Anime List</a>
                    <a href="/about">About</a>
                </nav>
            </header>
            
            <main>
                <section class="hero">
                    <div class="hero-content">
                        <h2>Your Ultimate Anime Companion</h2>
                        <p>Stay updated with the latest episodes, join discussions, and discover new series!</p>
                    </div>
                </section>
                
                <section class="section">
                    <h2>🔴 Community Links</h2>
                    <div class="links-container">
                        <a href="https://t.me/Anim3chat" target="_blank" class="community-link telegram">
                            <span class="icon">💬</span>
                            <span class="text">Ani3Lix Chat</span>
                        </a>
                        <a href="https://t.me/Ani3lix_clan" target="_blank" class="community-link telegram">
                            <span class="icon">👥</span>
                            <span class="text">Join My Telegram</span>
                        </a>
                        <a href="https://t.me/Ongoing_Anime_Episodes" target="_blank" class="community-link telegram">
                            <span class="icon">📺</span>
                            <span class="text">Ongoing Anime Episodes</span>
                        </a>
                    </div>
                </section>
                
                <section class="section">
                    <h2>🔥 Latest Updates</h2>
                    <div class="updates-container">
                        {updates_html}
                    </div>
                </section>
                
                <section class="section">
                    <h2>📊 Anime Trackers</h2>
                    <div class="trackers-container">
                        <a href="https://myanimelist.net" target="_blank" class="tracker mal">
                            <span class="tracker-name">MyAnimeList</span>
                            <span class="tracker-desc">Track your anime progress</span>
                        </a>
                        <a href="https://anilist.co" target="_blank" class="tracker anilist">
                            <span class="tracker-name">AniList</span>
                            <span class="tracker-desc">Discover seasonal anime</span>
                        </a>
                    </div>
                </section>
            </main>
        ''')

    async def handle_anime(self, method: str, params: Dict) -> str:
        if method != "GET":
            return self.create_error_response(405, "Method Not Allowed")
        
        return self.render_template("Anime List - Ani3Lix", '''
            <header>
                <div class="logo">
                    <h1>Ani3Lix</h1>
                </div>
                <nav>
                    <a href="/">Home</a>
                    <a href="/anime" class="active">Anime List</a>
                    <a href="/about">About</a>
                </nav>
            </header>
            
            <main>
                <section class="section">
                    <h2>Popular Anime</h2>
                    <p>This page is under construction. Check back soon for a complete anime directory!</p>
                    
                    <div class="coming-soon">
                        <img src="https://myanimelist.net/images/anime/1123/120922l.jpg" alt="Coming Soon">
                        <h3>More Content Coming Soon</h3>
                    </div>
                </section>
            </main>
        ''')

    async def handle_about(self, method: str, params: Dict) -> str:
        if method != "GET":
            return self.create_error_response(405, "Method Not Allowed")
        
        return self.render_template("About - Ani3Lix", '''
            <header>
                <div class="logo">
                    <h1>Ani3Lix</h1>
                </div>
                <nav>
                    <a href="/">Home</a>
                    <a href="/anime">Anime List</a>
                    <a href="/about" class="active">About</a>
                </nav>
            </header>
            
            <main>
                <section class="section about-section">
                    <h2>About Ani3Lix</h2>
                    <p>Ani3Lix is a passion project created by anime enthusiasts for anime enthusiasts. Our mission is to build a community where fans can discover, discuss, and enjoy their favorite anime series.</p>
                    
                    <h3>Our Story</h3>
                    <p>Founded in 2025 by "The Fool", Ani3Lix started as a small Telegram channel and has grown into a hub for anime updates and discussions.</p>
                    
                    <h3>Contact</h3>
                    <p>Join our Telegram groups to connect with the community and the creators!</p>
                    
                    <div class="contact-links">
                        <a href="https://t.me/Anim3chat" target="_blank">Telegram Chat</a>
                        <a href="https://t.me/Ani3lix_clan" target="_blank">Join Our Community</a>
                    </div>
                </section>
            </main>
        ''')

    async def handle_favicon(self, method: str, params: Dict) -> str:
        return "HTTP/1.1 204 No Content\r\n\r\n"

    def create_error_response(self, status_code: int, message: str) -> str:
        status_messages = {
            400: "Bad Request",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error"
        }
        status_text = status_messages.get(status_code, "Unknown Error")
        
        return f"HTTP/1.1 {status_code} {status_text}\r\nContent-Type: text/html\r\n\r\n" + self.render_error_page(status_code, message)

    def render_error_page(self, status_code: int, message: str) -> str:
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error {status_code} - Ani3Lix</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f5f5f5;
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .error-container {{
                    text-align: center;
                    background-color: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    max-width: 500px;
                }}
                h1 {{
                    font-size: 3rem;
                    margin-bottom: 0.5rem;
                    color: #ff6b6b;
                }}
                p {{
                    font-size: 1.2rem;
                    margin-bottom: 2rem;
                }}
                a {{
                    display: inline-block;
                    padding: 0.8rem 1.5rem;
                    background-color: #7159c1;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s;
                }}
                a:hover {{
                    background-color: #5f46af;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Error {status_code}</h1>
                <p>{message}</p>
                <a href="/">Return to Home</a>
            </div>
        </body>
        </html>
        '''

    def render_template(self, title: str, content: str) -> str:
        current_year = datetime.now().year
        
        return f'''HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary: #7159c1;
                    --primary-dark: #5f46af;
                    --secondary: #ff6b6b;
                    --text: #333;
                    --text-light: #777;
                    --bg: #f8f8f8;
                    --bg-card: #fff;
                    --border: #e0e0e0;
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Poppins', sans-serif;
                    background-color: var(--bg);
                    color: var(--text);
                    line-height: 1.6;
                }}
                
                /* Header & Navigation */
                header {{
                    background-color: var(--bg-card);
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem 5%;
                    position: sticky;
                    top: 0;
                    z-index: 100;
                }}
                
                .logo h1 {{
                    color: var(--primary);
                    font-size: 1.8rem;
                    font-weight: 700;
                }}
                
                nav {{
                    display: flex;
                    gap: 1.5rem;
                }}
                
                nav a {{
                    color: var(--text);
                    text-decoration: none;
                    font-weight: 500;
                    padding: 0.5rem 1rem;
                    border-radius: 5px;
                    transition: all 0.3s;
                }}
                
                nav a:hover, nav a.active {{
                    background-color: var(--primary);
                    color: white;
                }}
                
                /* Main Content */
                main {{
                    max-width: 1200px;
                    margin: 2rem auto;
                    padding: 0 1rem;
                }}
                
                .section {{
                    margin-bottom: 3rem;
                }}
                
                h2 {{
                    font-size: 1.8rem;
                    margin-bottom: 1.5rem;
                    color: var(--primary-dark);
                    position: relative;
                    padding-bottom: 0.5rem;
                }}
                
                h2::after {{
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 60px;
                    height: 4px;
                    background-color: var(--secondary);
                    border-radius: 2px;
                }}
                
                /* Hero Section */
                .hero {{
                    background-image: linear-gradient(to right, rgba(113, 89, 193, 0.9), rgba(113, 89, 193, 0.7)),
                                      url('https://wallpaperaccess.com/full/4498209.jpg');
                    background-size: cover;
                    background-position: center;
                    color: white;
                    border-radius: 15px;
                    padding: 4rem 2rem;
                    margin-bottom: 3rem;
                    text-align: center;
                }}
                
                .hero h2 {{
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                    color: white;
                }}
                
                .hero h2::after {{
                    display: none;
                }}
                
                .hero p {{
                    font-size: 1.2rem;
                    max-width: 700px;
                    margin: 0 auto;
                }}
                
                /* Links Section */
                .links-container {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 1rem;
                }}
                
                .community-link {{
                    display: flex;
                    align-items: center;
                    padding: 1.2rem;
                    background-color: var(--bg-card);
                    border-radius: 10px;
                    text-decoration: none;
                    color: var(--text);
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    transition: transform 0.3s, box-shadow 0.3s;
                }}
                
                .community-link:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                
                .community-link.telegram {{
                    border-left: 4px solid #0088cc;
                }}
                
                .community-link .icon {{
                    font-size: 1.5rem;
                    margin-right: 1rem;
                }}
                
                .community-link .text {{
                    font-weight: 500;
                }}
                
                /* Updates Section */
                .updates-container {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 1.5rem;
                }}
                
                .anime-card {{
                    background-color: var(--bg-card);
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    padding: 1.5rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .anime-info h3 {{
                    margin-bottom: 0.3rem;
                    color: var(--text);
                }}
                
                .anime-info p {{
                    color: var(--text-light);
                    font-size: 0.9rem;
                }}
                
                .watch-btn {{
                    padding: 0.5rem 1rem;
                    background-color: var(--primary);
                    color: white;
                    border-radius: 5px;
                    text-decoration: none;
                    font-weight: 500;
                    transition: background-color 0.3s;
                }}
                
                .watch-btn:hover {{
                    background-color: var(--primary-dark);
                }}
                
                /* Trackers Section */
                .trackers-container {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                }}
                
                .tracker {{
                    background-color: var(--bg-card);
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    padding: 1.5rem;
                    text-decoration: none;
                    color: var(--text);
                    transition: transform 0.3s, box-shadow 0.3s;
                }}
                
                .tracker:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                
                .tracker-name {{
                    display: block;
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                }}
                
                .tracker-desc {{
                    display: block;
                    font-size: 0.9rem;
                    color: var(--text-light);
                }}
                
                .tracker.mal {{
                    border-top: 4px solid #2e51a2;
                }}
                
                .tracker.anilist {{
                    border-top: 4px solid #02a9ff;
                }}
                
                /* About Page */
                .about-section {{
                    background-color: var(--bg-card);
                    border-radius: 15px;
                    padding: 2rem;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }}
                
                .about-section h3 {{
                    margin: 1.5rem 0 0.5rem 0;
                    color: var(--primary);
                }}
                
                .contact-links {{
                    display: flex;
                    gap: 1rem;
                    margin-top: 1.5rem;
                }}
                
                .contact-links a {{
                    padding: 0.8rem 1.5rem;
                    background-color: var(--primary);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 500;
                    transition: background-color 0.3s;
                }}
                
                .contact-links a:hover {{
                    background-color: var(--primary-dark);
                }}
                
                /* Coming Soon */
                .coming-soon {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    margin-top: 3rem;
                }}
                
                .coming-soon img {{
                    width: 200px;
                    border-radius: 10px;
                    margin-bottom: 1rem;
                }}
                
                /* Footer */
                footer {{
                    background-color: var(--primary-dark);
                    color: white;
                    text-align: center;
                    padding: 2rem 0;
                    margin-top: 4rem;
                }}
                
                .footer-content {{
                    max-width: 1200px;
                    margin: 0 auto;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0 1rem;
                }}
                
                .footer-logo h2 {{
                    color: white;
                    margin-bottom: 0.5rem;
                }}
                
                .footer-logo h2::after {{
                    display: none;
                }}
                
                .footer-links {{
                    display: flex;
                    gap: 1.5rem;
                }}
                
                .footer-links a {{
                    color: rgba(255, 255, 255, 0.8);
                    text-decoration: none;
                    transition: color 0.3s;
                }}
                
                .footer-links a:hover {{
                    color: white;
                }}
                
                .copyright {{
                    margin-top: 1.5rem;
                    font-size: 0.9rem;
                    opacity: 0.7;
                }}
                
                /* Responsive Design */
                @media (max-width: 768px) {{
                    header {{
                        flex-direction: column;
                        padding: 1rem;
                    }}
                    
                    .logo {{
                        margin-bottom: 1rem;
                    }}
                    
                    .footer-content {{
                        flex-direction: column;
                        text-align: center;
                    }}
                    
                    .footer-logo {{
                        margin-bottom: 1.5rem;
                    }}
                    
                    .hero {{
                        padding: 3rem 1rem;
                    }}
                    
                    .hero h2 {{
                        font-size: 2rem;
                    }}
                }}
                
                @media (max-width: 576px) {{
                    nav {{
                        flex-wrap: wrap;
                        justify-content: center;
                    }}
                    
                    .footer-links {{
                        flex-direction: column;
                        gap: 0.8rem;
                    }}
                }}
            </style>
        </head>
        <body>
            {content}
            
            <footer>
                <div class="footer-content">
                    <div class="footer-logo">
                        <h2>Ani3Lix</h2>
                        <p>Your hub for anime updates!</p>
                    </div>
                    <div class="footer-links">
                        <a href="/">Home</a>
                        <a href="/anime">Anime List</a>
                        <a href="/about">About</a>
                    </div>
                </div>
                <div class="copyright">
                    &copy; {current_year} Ani3Lix | Created by The Fool
                </div>
            </footer>
            
            <script src="https://inapp.telega.io/sdk/v1/sdk.js"></script>
            <script>
                const ads = window.TelegaIn?.AdsController?.create_miniapp ? 
                    window.TelegaIn.AdsController.create_miniapp({{ token: '170a3bc1-4cb3-4c99-8a30-58c7c44117f0' }}) : null;
                
                if (ads) {{
                    ads.ad_show({{ adBlockUuid: '6b346b7a-ff49-43fb-8c23-cbb3e008f836' }});
                }}
                
                // Add a simple animation effect for links
                document.querySelectorAll('.community-link, .tracker').forEach(element => {{
                    element.addEventListener('mouseenter', () => {{
                        element.style.transform = 'translateY(-5px)';
                    }});
                    
                    element.addEventListener('mouseleave', () => {{
                        element.style.transform = 'translateY(0)';
                    }});
                }});
            </script>
        </body>
        </html>
        '''

async def run_server(host: str, port: int) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    server = HTTPServer(host, port)
    logger.info(f"Starting Ani3Lix server on {host}:{port}")
    
    try:
        await server.run_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_server("127.0.0.1", 8080))
