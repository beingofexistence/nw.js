import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nw_util import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import utils

chrome_options = Options()
chrome_options.add_argument("nwapp=" + os.path.dirname(os.path.abspath(__file__)))
chrome_options.add_experimental_option("windowTypes", ["webview"])

testdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(testdir)

port_n = utils.free_port()
port = str(port_n)
server = subprocess.Popen(['python', '../http-server-node.py', port])

time.sleep(1)
tpl = open('index.tpl', 'r')
content = tpl.read().replace('{port}', port)
tpl.close()

html = open('index.html', 'w')
html.write(content)
html.close()

if not wait_net_service("127.0.0.1", port_n, 30):
    import platform
    if platform.system() == 'Windows':
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(server.pid)])
    else:
        server.terminate()
    raise Exception('Timeout when waiting for http server')

driver = webdriver.Chrome(executable_path=os.environ['CHROMEDRIVER'], chrome_options=chrome_options, service_log_path="log", service_args=["--verbose"])
driver.implicitly_wait(5)
try:
    wait_window_handles(driver, 2)
    print(driver.current_url)
    result = wait_for_element_id(driver, 'inject_start')
    print('inject_js_start: %s' % result)
    assert('success' in result)
    elems = driver.find_elements_by_tag_name('h1')
    assert(len(elems) == 1)
    driver.switch_to.window(driver.window_handles[1])
    result = wait_for_element_id(driver, 'inject_start')
    print('inject_js_start in iframe: %s' % result)
    assert('success' in result)
    elems = driver.find_elements_by_tag_name('h1')
    assert(len(elems) == 1)
finally:
    driver.quit()
    import platform
    if platform.system() == 'Windows':
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(server.pid)])
    else:
        server.terminate()
