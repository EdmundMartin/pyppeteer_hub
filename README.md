# Notes
Highly experimental, very unstable.

# Project Goal
The project aims to provide a wrapper around the Python port of Puppeteer (pyppeteer). The server provides a number of
endpoints for rendering, as well as providing endpoints for interacting and using a consistent session. The server can
manage multiple browsers with multiple tabs allowing (theoretically) high request throughput. There is also a Python 
client that works with the servers JSON API to provide a Selenium-esque experience.

## Running the Server
```python
from server import run_server
run_server(host='0.0.0.0', port=8000, browsers=1, max_cap=10)
```
The server package contains a run_server function. It is here where the number of browsers and tabs is defined. 
Additionally, the host and port can be set as above.

## Client
```python
from client import Session

sess = Session('http://localhost:8000')
res = sess.get('http://edmundmartin.com', post_load_wait=5)
res = sess.close()
```
## Client Methods
### get
```python
sess = Session('http://localhost:8000')
sess = sess.get('http://example.com', post_load_wait=0)
```
Makes a get request to a page. A post_load_wait can be set to wait a set number of seconds post page load.


## TODO
* Implement proper error handling
* Determine which errors should end a session
* Implement an adapter for Selenium compatibility
* Add additional methods to Session class
* Add async client
* Add Golang client
* Load & Performance testing