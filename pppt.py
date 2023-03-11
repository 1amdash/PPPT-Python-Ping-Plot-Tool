"""Netwrk Status... and latency and stuff"""
#!/usr/bin/env python3.6
import os
import curses
import curses.textpad
import curses.panel
import platform
import subprocess
import threading
import socket
import collections
import time
import argparse


def prepare_curses():
    """Setup terminal for curses operations."""
    stdscr.erase()
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    stdscr.bkgdset(curses.color_pair(1))
    
def end_curses():
    """Gracefully reset terminal to normal settings."""
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    os.system('reset')

def draw_win(height, width, y_start, x_start):
    window = stdscr.derwin(height, width, y_start, x_start)
    window.bkgd(curses.color_pair(1))
    window.keypad(1)
    return window

def get_ip_address(ip_to_ping):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((ip_to_ping, 80))
    return s.getsockname()[0]
            
def ping(host_or_ip):
    if platform.system().lower() == 'windows':
        command = ['ping', '-l', host_or_ip]
    else:
        command = ['ping', host_or_ip]
        proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=0,
                    universal_newlines=True
                    )
    return proc

class get_output:
    def __init__(self, ping, host):
        self.ping_process = ping(host)
        self.read()
        
    def read(self):
        packets = 0
        packets_lost = 0
        latency = 0
        time_out = 1
        queue_packets.append(packets)
        queue_packets_lost.append(packets_lost)
        queue_latency.append(latency)
        queue_time_out.append(time_out)     
        for line in iter(self.ping_process.stdout.readline, ''):
            if not line:
                break
            elif line.startswith('64'):
                packets += 1
                queue_packets[-1] = packets
                time_index = line.find('time=')
                ms_index = line.find(' ms')
                raw_num = line[time_index+5:ms_index].strip()
                latency = convert_ms(raw_num)
                queue_latency[-1] = latency
                queue_time_out[-1] = 1
                time.sleep(.001)
            elif line.startswith('Request'):
                packets += 1
                packets_lost += 1
                queue_packets_lost[-1] = packets_lost
                queue_packets[-1] = packets
                queue_time_out[-1] = 0
                
class Main:
    def __init__(self, main_window, ip_to_ping):

        graph_size = 40
        loss = 0
        
        min_time = 0
        max_time = 0
        avg_time = 0
        jitters = jitter()
        jitt = 0
        bar = bar_graph()

        my_ip_address = get_ip_address(ip_to_ping)

        t = threading.Thread(
            name='PingThread', target=get_output, args=(ping, ip_to_ping), daemon=True)
        t.start()
        
        ready_to_exit = False
        
        while len(queue_latency) != 1:
                waiting = 1

        while queue_latency[0] == 0:
            waiting = 1

        while ready_to_exit is not True:
            if len(queue_latency) > graph_size:
                queue_latency.popleft()
            
            latency = queue_latency[-1]
            self.packets_lost = queue_packets_lost[-1]
            self.packets = queue_packets[-1]

            if queue_time_out[-1] == 0:
                latency = 0
                
            hist.add(latency)
            min_time = hist.min_val()
            max_time = hist.max_val(hist.times)
            avg_time = hist.avg(latency)
            

            if len(hist.times) > 1:
                jitt = jitters.calc(hist.times)
                
            if self.packets_lost > 1:
                loss = packet_loss(self.packets, self.packets_lost)

            top_info(main_window, 
                     update_all_views, 
                     self.packets, 
                     self.packets_lost, 
                     loss, 
                     my_ip_address, 
                     ip_to_ping, 
                     latency, 
                     jitt
                     )

            bar.bar_graph(main_window, 5, update_all_views, hist,min_time,max_time, avg_time)
            curses.doupdate()
            something = 1
        
def update_all_views(window):
    stdscr.noutrefresh()
    window.noutrefresh()
       
def top_info(window, update_all_views, packets, packets_lost, packet_loss, src_ip, dest_ip, latency, jitter):
    screen_width = stdscr.getmaxyx()[1]
    spacing = screen_width * ' '
    window.addstr(0, 0, spacing)
    window.addstr(1, 0, spacing)
    window.addstr(2, 0, spacing)
    window.addstr(0, 0, str(src_ip) + ' > ' + str(dest_ip))
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

    def bar_graph(self, window, bar_graph_top, update, history, min, max, avg_time):
        time.sleep(.80)
        ping_max = max
        ping_min = min
        ping_time = hist.times[-1]
        self.bar_graph_bottom = bar_graph_top + 10
        self.window = window
        self.update = update
        graph_top = 5
        graph_bottom = 14
        self.x_axis_labels(ping_min,avg_time,ping_max)
        scaled_times_hist = self.draw_bars(history, ping_max, ping_min, graph_top, graph_bottom)
        clean_graph(self.window, self.update)
        self.scroll(scaled_times_hist)
        self.update(self.window)

    def draw_bars(self, history, ping_max, ping_min, graph_top, graph_bottom):
        scaled_times_hist = []
        for ping_time in history.times:
            new_time = scale_numbers(ping_time, ping_max, ping_min, graph_top, graph_bottom)
            new_time = not_below_zero(new_time)
            scaled_times_hist.append(new_time)
        return scaled_times_hist
        
    def x_axis_labels(self, ping_min, avg_time, ping_max):

        self.window.addstr(5, 0, '    ')
        self.window.addstr(5, 0, str(ping_max))

        self.window.addstr(10, 0, '    ')
        self.window.addstr(10, 0, str(avg_time))

        self.window.addstr(14, 0, '    ')
        self.window.addstr(14, 0, str(ping_min))

    def scroll(self, scaled_times_hist):
        graph_bars_horizontal = 5
        for x in scaled_times_hist:
            graph_bars_horizontal += 1
            for bar_height in reversed(range(x, self.bar_graph_bottom)):                
                bar_fill = '#'
                self.window.addstr(bar_height, graph_bars_horizontal, bar_fill, curses.color_pair(1))
        self.update(self.window)
        
class history:
    def __init__(self) -> None:
        self.times = []
        self.history_length = 40
        
    def replace_last(self, new_time):
        array_length = len(self.times)
        for i in range(array_length):
            if i+1 == array_length:
                self.times[i] = new_time 
            elif i >= 0 and i < array_length:
                  
                self.times[i] = self.times[i+1]
    
    def add(self, pings):
        if len(self.times) > self.history_length:
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

def clean_graph(window, update):
    bar_graph_top = 5
    bar_graph_bottom = 15
    graph_width = 41
    for x in range(graph_width):
        for height in range(bar_graph_top,bar_graph_bottom):
            window.addstr(height, x+6, ' ')
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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Graph pings.', usage='%(prog)s [options]')
    parser.add_argument('ip', help='IP Address', nargs='?', type=str, default='8.8.4.4')
    args = parser.parse_args()
    
    stdscr = curses.initscr()
    screen_height, screen_width = stdscr.getmaxyx()
    prepare_curses()

    main_window = draw_win(screen_height,screen_width,0,0)
    hist = history()
    queue_latency = collections.deque()
    queue_packets = collections.deque()
    queue_packets_lost = collections.deque()
    queue_time_out = collections.deque()
    
    main = Main(main_window, args.ip)
    end_curses()
