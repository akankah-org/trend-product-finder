"""Serve folder ini di :8001. Jalankan: python serve.py"""
import http.server
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler,
                 port=8001, bind="127.0.0.1")
