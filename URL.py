import gzip
import socket
import ssl


class URL:
    def __init__(self, url):
        self.scheme = None
        self.host = None
        self.port = None
        self.path = None
        self.view_source_mode = False
        self.is_blank = False

        try:

            # Check for view-source scheme
            if url.startswith("view-source:"):
                self.view_source_mode = True
                url = url[len("view-source:"):]
                print(url)

            # Handle about:blank
            if url == "about:blank":
                self.is_blank = True
                return

            # Handle different schemes (http, https, file, data)
            if url.startswith("file://"):
                self.scheme = "file"
                self.file_path = url[len("file://"):]
            elif url.startswith("data:"):
                self.scheme = "data"
                self.data_url = url[len("data:"):]
            else:
                self.scheme, rest = url.split("://", 1)
                assert self.scheme in ["http", "https"]
                if self.scheme == "http":
                    self.port = 80
                elif self.scheme == "https":
                    self.port = 443

                if "/" not in rest:
                    rest = rest + "/"
                self.host, self.path = rest.split("/", 1)
                self.path = "/" + self.path
                if ":" in self.host:
                    self.host, port = self.host.split(":", 1)
                    self.port = int(port)

        except Exception as e:
            print(f"Error parsing URL: {e}")
            self.is_blank = True

        self.s = {}
        self.cache = {}  # Store URLs and responses

    def request(self):
        if self.is_blank:
            return ""  # Return empty content for about:blank or malformed URLs
        
        if self.scheme == "http" or self.scheme == "https":
            return self.handle_http()
        elif self.scheme == "file":
            return self.handle_file()
        elif self.scheme == "data":
            return self.handle_data()
        
    def handle_http(self):
        if self.path in self.cache:
            return self.cache[self.path]

        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM )
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            self.s = ctx.wrap_socket(self.s, server_hostname=self.host)
        self.s.connect((self.host, self.port))

        request = "GET {} HTTP/1.0\r\n".format(self.path)  # Keep-alive uses HTTP 1.1
        request += "Host: {}\r\n".format(self.host)
        # request += "Connection: keep-alive\r\n"  # Add keep-alive header
        request += "\r\n"
        self.s.send(request.encode("utf8"))
        response = self.s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        if status.startswith("3"):  # Redirect handling
            for line in response:
                if line.startswith("Location:"):
                    location = line.split(" ", 1)[1].strip()
                    if location.startswith("/"):
                        location = "{}://{}{}".format(self.scheme, self.host, location)
                    self.__init__(location)
                    return self.request()  # Recursive redirect
        
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        if "content-encoding" in response_headers and response_headers["content-encoding"] == "gzip":
            content = gzip.decompress(content)
        self.cache[self.path] = content        
        self.s.close()
        return content


    def handle_file(self):
        try:
            with open(self.path, "r", encoding="utf8") as f:
                return f.read()
        except FileNotFoundError:
            return "File not found: " + self.path

    def handle_data(self):
        if self.path.startswith("text/html,"):
            return self.path.split(",", 1)[1]  # Inline HTML content
        return "Unsupported data type"

    def handle_view_source(self):
        return self.request()  # Returns the source HTML without formatting
    
    def resolve(self, url):
        if "://" in url: return URL(url)
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        if url.startswith("//"):
            return URL(self.scheme + ":" + url)
        else:
            return URL(self.scheme + "://" + self.host + \
                       ":" + str(self.port) + url)