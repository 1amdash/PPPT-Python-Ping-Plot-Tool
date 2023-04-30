"""
PPPT - Python Ping Plot Tool - Ping graph, latency, and jitter.

Imports Pyping...
:homepage: https://github.com/toxinu/Pyping/
:copyleft: 1989-2011 by the python-ping team, see AUTHORS for more details.
:license: GNU GPL v2, see LICENSE for more details.
"""
#!/usr/bin/env python3.6
import os
import curses
import curses.textpad
import curses.panel
import threading
import socket
import collections
import time
import argparse
import pyping_4

CONST_ESCAPE_KEY = 27

def prepare_curses():
    """Setup terminal for curses operations."""
    stdscr = curses.initscr()
    stdscr.erase()
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.bkgdset(curses.color_pair(1))
    return stdscr
    
def end_curses():
    """Gracefully reset terminal to normal settings."""
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    os.system('reset')

def draw_win(height, width, y_start, x_start):
    """Returns window derived from stdscr."""
    window = stdscr.derwin(height, width, y_start, x_start)
    window.bkgd(curses.color_pair(1))
    window.keypad(1)
    return window

def check_window_size(window, screen_height, screen_width):
    resize = curses.is_term_resized(screen_height, screen_width)

    # Action in loop if resize is True:
    if resize is True:
        y, x = window.getmaxyx()
        curses.resizeterm(y, x)
        stdscr.noutrefresh()
        screen_height, screen_width = stdscr.getmaxyx()
        resize = False
        return screen_height, screen_width
    else:
        return screen_height, screen_width
        
        
def get_ip_address_simple(arg1, arg2):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(.3)
        sock.connect(('10.254.254.254', 1))
        ip_address = sock.getsockname()[0]

    except:
        ip_address = None
    finally:
        queue_my_ip_address.append(ip_address)
        while True:
            try:
                time.sleep(3)
                queue_my_ip_address[-1] = sock.getsockname()[0]
            except:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect(('10.254.254.254', 1))

class get_ip_address:
    def __init__(self, ip_to_ping):
        self.remote_ip = ip_to_ping
        sock = self.estab_socket()
        sock.settimeout(1)
        
        self.connect(sock)
        self.check(sock)
        
    def estab_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self.sock
        
    def connect(self, sock):
        try:
            sock.connect(('dns.google', 1))
        except TimeoutError:
            return
        
    def check(self, sock):
        while True:
            try:
                self.ip_address = sock.getsockname()[0]
            except TimeoutError:
                self = self.connect(sock)

            queue_my_ip_address = self.ip_address
    
def ping(destination, count, timeout, packet_size, *args, **kwargs):
	p = pyping_4.Ping(destination, queue_latency, queue_packets, queue_packets_lost, queue_time_out, packet_header, trace_route, timeout, packet_size, *args, **kwargs)
	return p.run(count)

class Main:
    def __init__(self, main_window, ip_to_ping, count):
        screen_height, screen_width = stdscr.getmaxyx()

        jitters = jitter()
        bar = bar_graph()
        queue_packets_lost.append(0)
        self.packets_lost = 0

        timeout = 1000
        packet_size=55
        graph_top = 5
        loss = 0
        min_time = 0
        max_time = 0
        avg_time = 0
        jitt = 0

        
        #my_ip_address = get_ip_address_simple(ip_to_ping)
        #ip_address = get_ip_address(ip_to_ping)
        #my_ip_address = ip_address.ip_address
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        IPChecker = threading.Thread(
            name='IPChecker', target=get_ip_address_simple, args=('1', '2'), daemon=True)
        IPChecker.start()
        
        PingThreadObj = threading.Thread(
            name='PingThread', target=ping, args=(ip_to_ping, count, timeout, packet_size), daemon=True)
        
        PingThreadObj.start()
        
        
        
        #my_ip_address = get_ip_address_simple(ip_to_ping)
        
        timeout = timeout / 1000

        ready_to_exit = False
        
        while len(queue_latency) != 1:
                waiting = 1

        while queue_latency[0] == 0:
            waiting = 1
            
            

        while ready_to_exit is not True:

            
            screen_height, screen_width = check_window_size(main_window, screen_height, screen_width)
            self.graph_width = int(screen_width  - 10)
            graph_height = screen_height
            hist.set_length(int(self.graph_width))

            if len(queue_latency) > self.graph_width:
                queue_latency.popleft()
                
                
            hist.times = trim_array(hist.times, self.graph_width)    
            
            latency = queue_latency[-1][0]
            if queue_packets_lost[-1] > self.packets_lost:
                
                self.packets_lost = queue_packets_lost[-1]
                latency = 0
            self.packets = queue_packets[-1]

            min_rtt = queue_latency[-1][5]
            avg_rtt = queue_latency[-1][6]
            max_rtt = queue_latency[-1][7]
            main_window.addstr(3, 0, "min: " + min_rtt +" avg: "+avg_rtt+" max: " + max_rtt)
            
            hist.add(latency)
            min_time = hist.min_val()
            max_time = hist.max_val(hist.times)
            avg_time = hist.avg(latency)
            hist_array_length = len(hist.times)
            
            if len(hist.times) > 1:
                jitt = jitters.calc(hist.times)
            
            if self.packets_lost > 1:
                loss = packet_loss(self.packets, self.packets_lost)
            
            if len(queue_my_ip_address) != 1:
                my_ip_address = 'searching'
            else:
            
               my_ip_address = queue_my_ip_address[-1]
            
            top_info(main_window, 
                     update_all_views, 
                     self.packets, 
                     self.packets_lost, 
                     loss, 
                     my_ip_address, 
                     ip_to_ping, 
                     latency, 
                     jitt,
                     hist_array_length,
                     self.graph_width
                     )
            
            try:
                bar.bar_graph(self, main_window, graph_top, self.graph_width, graph_height, update_all_views, hist,min_time,max_time, avg_time, timeout)
            except KeyboardInterrupt:
                ready_to_exit = True
            curses.doupdate()
            something = 1
            event = key_press(main_window)
            
            if count is not None:
                if count == self.packets:
                    ready_to_exit = True
                    time.sleep(5)

            ready_to_exit = self.exit_main_loop(event, ready_to_exit)


    def exit_main_loop(self, event, ready_to_exit):
        if event == CONST_ESCAPE_KEY or ready_to_exit == True:
            return True
        else:
            return False
        
        
def new_pad():
    height, width = stdscr.getmaxyx()
    pad = curses.newpad(height, width)
    pad.scrollok(True)
    return pad

def trim_array(array, length):
    if length < len(array):
        difference = len(array) - length

        del(array[0:difference])
        return array    
    else: return array
    
def key_press(window_obj):
    window_obj.nodelay(True)
    try:
        key = window_obj.getch()
    except KeyboardInterrupt:
        return
    if key:
        key_press_event(key)
         
def key_press_event(key):
    CONST_NO_KEY_PRESSED = -1
    if key == CONST_NO_KEY_PRESSED:
        pass
    else:
        event_response(key)

def event_response(event):
    if event is CONST_ESCAPE_KEY:
        return CONST_ESCAPE_KEY
    else:
        pass
    
def update_all_views(window):
    stdscr.noutrefresh()
    window.noutrefresh()
       
def top_info(window, update_all_views, packets, packets_lost, packet_loss, src_ip, dest_ip, latency, jitter, history_length, graph_width):
    screen_width = stdscr.getmaxyx()[1]
    spacing = screen_width * ' '
    text_color = curses.color_pair(2)
    window.addstr(4, 0, str(history_length) + ' ' + str( graph_width), text_color)
    window.addstr(0, 0, str(src_ip) + ' > ' + str(dest_ip), text_color)
    window.addstr(1, 0, str('Packets: ') + str(packets) 
                        + str(' Lost: ') + str(packets_lost) 
                        + str(' Loss: ') + str(packet_loss) + str('%') 
                        )              
    
    if jitter > 60:
        color = curses.color_pair(3)
    elif jitter > 30:
        color = curses.color_pair(2)
    else:
        color = curses.color_pair(1)
        
    latency = round(latency, 3)

    window.addstr(2, 0, str('Latency: ') + str(latency) + str(' ms') + str(' Jitter: ') + str(jitter) + str(' ms'), color)
    update_all_views(window)
    curses.doupdate()

def convert_ms(raw):
    millisecs_float = float(raw)
    millisecs_int = int(millisecs_float)
    return millisecs_int

class jitter:
    
    def __init__(self):
        self.jitter_times = []
    
    def calc(self, history):
        
        last_time = history[-2]
        next_time = history[-1]
        jitter_time = last_time - next_time
        self.jitter_times.append(abs(jitter_time))
            
        jitter_list_length = len(self.jitter_times)
        sum_jitter = sum(self.jitter_times)
        jitt = sum_jitter / jitter_list_length
        self.jitt = round(jitt)
        if jitter_list_length > 41:
            self.jitter_times.pop(0)
        return self.jitt

def packet_loss(packets, packets_lost):
    packet_loss = float(packets_lost/packets)
    packet_loss = packet_loss * 100
    packet_loss = round(packet_loss, 3)
    return packet_loss    

class bar_graph:
    def __init__(self):
        x = 0

    def bar_graph(self, main, window, bar_graph_top, graph_width, graph_height, update, history, min, max, avg_time, timeout):
        ping_max = max
        ping_min = min
        latency = hist.times[-1]
        timeout = timeout * 1000
        # if timeout > latency:
        #     sleep_time = ((timeout - latency) / 1000)
        #     time.sleep(sleep_time)
        time.sleep(.2)
        
        self.window = window
        self.update = update
        graph_top = 5
        clean_graph(self.window, self.update, bar_graph_top, graph_height, graph_width)
        self.x_axis_labels(ping_min,avg_time,ping_max, bar_graph_top, graph_height)
        scaled_times_hist = self.draw_bars(history, ping_max, ping_min, graph_top, graph_height)
        self.scroll(main, scaled_times_hist, graph_height)
        self.update(self.window)

    def draw_bars(self, history, ping_max, ping_min, graph_top, graph_bottom):
        scaled_times_hist = []
        for ping_time in history.times:
            new_time = scale_numbers(ping_time, ping_max, ping_min, graph_top, graph_bottom)
            new_time = not_below_zero(new_time)
            scaled_times_hist.append(new_time)
        return scaled_times_hist
        
    def x_axis_labels(self, ping_min, avg_time, ping_max, bar_graph_top, bar_graph_bottom):
        
        ping_max = round(ping_max, 3)
        avg_time = round(avg_time, 3)
        ping_min = round(ping_min, 3)
        
        graph_middle = round(((bar_graph_bottom - bar_graph_top) / 2) + bar_graph_top)
        self.window.addstr(bar_graph_top, 0, str(ping_max), curses.color_pair(2))
        self.window.addstr(graph_middle, 0, str(avg_time), curses.color_pair(2))
        self.window.addstr(bar_graph_bottom - 1, 0, str(ping_min), curses.color_pair(2))

    def scroll(self, main, scaled_times_hist, bar_graph_bottom):
        graph_bars_horizontal = 7
        for x in scaled_times_hist:
            graph_bars_horizontal += 1
            for bar_height in reversed(range(x, bar_graph_bottom)):                
                bar_fill = '=='
                if main.graph_width < len(scaled_times_hist):
                    pass
                else:
                   self.window.addstr(bar_height, graph_bars_horizontal, bar_fill, curses.color_pair(1))
        self.update(self.window)
        
class history:
    def __init__(self, history_length) -> None:
        self.times = []
        self.set_length(history_length)
    
    def set_length(self, length):
        self.history_length = length
        
    def replace_last(self, new_time):
        array_length = len(self.times)
        for i in range(array_length):
            if i+1 == array_length:
                self.times[i] = new_time 
            elif i >= 0 and i < array_length:
                  
                self.times[i] = self.times[i+1]
    
    def add(self, pings):
        if len(self.times) >= self.history_length:
            self.replace_last(pings)
        else:
            self.times.append(pings)

    def avg(self, pings):
        try:
            times_sum = sum(self.times)
            times_avg = times_sum / len(self.times)
            times_avg = round(times_avg)
            return times_avg
        except:
            return pings                        
    def min_val(self):
        min_list = [v for v in self.times if v != 0]
        try:
            return min(min_list)
        except ValueError:
            return 0
        
    def max_val(self, pings):
        try:
            return max(self.times)
        except ValueError:
            return 200

def clean_graph(window, update, bar_graph_top, bar_graph_bottom, graph_width):
    screen_width = stdscr.getmaxyx()[1]
    screen_width = screen_width - 1
    for x in range(screen_width):
        for height in range(bar_graph_top,bar_graph_bottom):
            window.addstr(height, x, ' ') # +6
    update(window)
    
def not_below_zero(number):
    if number < 5:
        number = 5
        return number
    else:
        return number

def scale_numbers(value, old_min, old_max, new_min, new_max):
    try:
        value_new = ( (value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min
    except ZeroDivisionError:
        value_new = 0 
    value_round = round(value_new)
    value_int = int(value_round)
    return value_int


def argument_parser():
    parser = argparse.ArgumentParser(description='Graph pings.', usage='%(prog)s [options]')
    parser.add_argument('-i', dest='ip', help='IP Address', nargs='?', type=str, default='dns.google')
    parser.add_argument('-c', dest='count', help='Count', nargs='?', type=int)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = argument_parser()    
    stdscr = prepare_curses()
    screen_height, screen_width = stdscr.getmaxyx()
    main_window = draw_win(screen_height,screen_width,0,0)
    hist = history(screen_width)
    queue_latency = collections.deque()
    queue_packets = collections.deque()
    queue_packets_lost = collections.deque()
    queue_time_out = collections.deque()
    queue_my_ip_address = collections.deque()
    packet_header = collections.deque()
    trace_route = collections.deque()
    
    main = Main(main_window, args.ip, args.count)
    end_curses()
