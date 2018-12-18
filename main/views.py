import os

from django.shortcuts import render
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings as djangoSettings
from django.http import HttpResponse
from django.template import RequestContext

from .models import ScrapyTask

from urllib.parse import urlparse, urljoin
from scrapyd_api import ScrapydAPI

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time
import uuid

# set up chromedriver for selenium to use as browser in the background
chrome_options = Options()
chrome_options.binary_location = os.environ.get('../drivers/chromedriver.exe')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.environ.get('CHROMEDRIVER_PATH'))

# JS which is injected by Selenium when opening the url
injected_js     = (
    """        
        (function(d, script) {
            // set host url to body
            document.body.setAttribute('host', d.domain);
            document.body.setAttribute('path', d.location.pathname);

            // create a turn-on/turn-off crawl button
            var div = document.createElement('div');
            div.innerHTML = \"<button class='document-viewing' id='turnOffCrawlBtn'>Turn on scraping</button>\".trim();
            document.body.appendChild(div.firstChild); 

            // load stylesheet
            var style = document.createElement('style');
            style.innerHTML = \"#turnOffCrawlBtn { position: fixed;z-index:9999999999999999999999;top:50%;right:0;font-size:25px;color:#fff;background:#007bff;border-color:#007bff;border-radius:.3rem;line-height:1.5;cursor:pointer;padding:.5rem 1rem;display:block;font-weight:400;text-align:center;white-space:nowrap;vertical-align:middle;border:1px solid transparent;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;} #turnOffCrawlBtn:hover {background-color:#0062cc;border-color:#005cbf} \";
            d.head.appendChild(style);

            // load script with asset-logic
            scriptAsset = d.createElement('script');
            scriptAsset.type = 'text/javascript';
            scriptAsset.async = true;
            scriptAsset.onload = function(){
                // remote script has loaded
            };
            scriptAsset.src = '/static/main/js/asset_loader.js';
            d.head.appendChild(scriptAsset);                    

            // load font-awesome to target site
            var link = document.createElement('div');
            link.innerHTML = '<link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css\">';
            d.head.appendChild(link);                       

            // load script with crawling-logic
            scriptCrawl = d.createElement('script');
            scriptCrawl.type = 'text/javascript';
            scriptCrawl.async = true;
            scriptCrawl.onload = function(){
                // remote script has loaded
            };
            scriptCrawl.src = '/static/main/js/crawl.js';
            d.head.appendChild(scriptCrawl);    

        }(document));
    """
)

# Create your views here.

# main ui
def index(request):            

    # each task will get a unique id
    pid = str(uuid.uuid4())    
    ScrapyTask.objects.create(pid=pid)

    fname = str(uuid.uuid4()) + ".html"
    ScrapyTask.file_name = fname 
    
    url = request.POST.get('iframe-nav')
    if (url == None):
        url = ""        
        context={'default_page':static(os.path.join('main','tmp','default.html')), 'url': url, 'pid': pid}
    else:    
        domain = urlparse(url).netloc
        
        # open the webpage with selenium and inject JS into the document
        driver.get(url)
        driver.execute_script(injected_js)

        # open the default_iframe.html file and copy the html code from selenium into it
        path=os.path.join(djangoSettings.MAIN_DIR_STATIC_TMP, fname)
        defIframe=open(path, 'w+',encoding='utf-8')    
        defIframe.write(driver.page_source)
        defIframe.close()   
        context={'default_page':static(os.path.join('main','tmp',fname)), 'url': url, 'pid': pid}

    # return view        
    response = render(request, 'main/index.html', context)                        
    return response

# handler for [...]/scrapy
def scrapy(request):    
    url         = request.POST.get('url')       # current url
    domain      = request.POST.get('host')      # domain
    selector    = request.POST.get('selector')  # XPath or CSS selector (currently only CSS selectors are supported)
    pid         = request.POST.get('pid')       # generated ID

    # schedule spider "scrapy_results" from the project iScrapy in by requesting scrapyd-service
    # pass the tasks pid, current url, domain and a selector
    task    = djangoSettings.SCRAPYD.schedule('crawler', 'scrapy_results', pid=pid, url=url, domain=domain, selector=selector)

    # update database
    tmp = ScrapyTask.objects.get(pid=pid)
    tmp.task_id = task
    tmp.save(update_fields=['task_id'])    

    # we stay on the page
    return render(request, 'main/index.html', context={})