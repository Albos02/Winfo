from datetime import datetime
import os
from winfo_constants import BUTTON_NOT_PRESSED_COLOR, BUTTON_PRESSED_COLOR

class Logger:
    def __init__(self):
        self.log_dir = 'logs'

        self.filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        self.path = os.path.join(self.log_dir, self.filename)

        os.makedirs(self.log_dir, exist_ok=True)
    
    def format(self, level, message):
        """
        Format the log message
        
        :param level: Log level (e.g., 'INFO', 'ERROR')
        :param message: Log message
        :return: Formatted log string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return f"{timestamp} - {level} - {message}"
    
    def write_to_log_file(self, level, message):
        """
        Write a formatted log message to the file
        
        :param level: Log level
        :param message: Log message
        """
        formatted_message = self.format(level, message)
        with open(self.path, 'a') as f:
            f.write(formatted_message + '\n')
        
        print('logged', formatted_message)
    
    def info(self, message):
        """
        Log an INFO level message
        
        :param message: Message to log
        """
        self.write_to_log_file('INFO', message)
    
    def error(self, message):
        """
        Log an ERROR level message
        
        :param message: Message to log
        """
        self.write_to_log_file('ERROR', message)

logger = Logger()


class FrameNavigator():
    """manages frames to move forward/backward in history and load frames instantly by storing them"""
    def __init__(self):
        self.frame_history = []
        self.frame_names = []
        self.reset()
    def reset(self):
        logger.info('reseting frame navigator')

        self.current_index = None

        self.active_frame = None
        self.active_frame_name = None
    def dehover_left_column_buttons(self):
        self.button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
        self.button2.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
        self.button3.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
        self.button4.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    def hover_left_column_button_active(self):
        # if fav_active or all_station_active:
        if active_frame_manager.active_frame_type == 'fav_station' or active_frame_manager.active_frame_type == 'all_station':
            self.button1.configure(fg_color=BUTTON_PRESSED_COLOR)
        # elif map_active:
        elif active_frame_manager.active_frame_type == 'map':
            self.button2.configure(fg_color=BUTTON_PRESSED_COLOR)
        elif active_frame_manager.active_frame_type == 'alert':
            self.button3.configure(fg_color=BUTTON_PRESSED_COLOR)
        # elif settings_active:
        elif active_frame_manager.active_frame_type == 'settings':
            self.button4.configure(fg_color=BUTTON_PRESSED_COLOR)
    def get_active_frame_name(self):
        if station_frame_active:
            self.active_frame_name = 'station_frame'
            self.active_frame = station_frame
        elif map_active:
            self.active_frame_name = 'map'
            self.active_frame = map_frame
        elif fav_active:
            self.active_frame_name = 'fav_station'
            self.active_frame = table_frame
        elif all_station_active:
            self.active_frame_name = 'all_station'
            self.active_frame = table_frame
        elif settings_active:
            self.active_frame_name = 'settings'
            self.active_frame = settings_frame
        else:
            logger.info('FrameNavigator.get_active_frame_name() error ? : no active frame')

    def set_new_active_frame(self, frame_name):
        global station_frame_active, map_active, fav_active, all_station_active, settings_active
        station_frame_active, map_active, fav_active, all_station_active, settings_active = False, False, False, False, False
        if frame_name == 'station_frame':
            station_frame_active = True
        elif frame_name == 'map':   
            map_active = True
        elif frame_name == 'fav_station':
            fav_active = True
        elif frame_name == 'all_station':
            all_station_active = True
        elif frame_name == 'settings':
            settings_active = True
        else:
            logger.error('FrameNavigator.set_new_active_frame(): frame_name not valid')
    def store_frame(self, frame, frame_name):
        self.frame_history.append(frame)
        self.frame_names.append(frame_name)

    def forget_active_frame(self, store: bool=True):
        logger.info(f'forget_active_frame() called -> store: {store}')
        if self.current_index is not None and store is True:
            self.reset()   

        # self.get_active_frame_name()
        self.active_frame = active_frame_manager.active_frame
        self.active_frame_name = active_frame_manager.active_frame_type
        
        if self.active_frame is None: #if Winfo is starting up
            return
        if store:
            self.store_frame(self.active_frame, self.active_frame_name)

        if self.active_frame is not None:
            self.active_frame.pack_forget()

    def pack_frame(self):
        if len(self.frame_history) > 0:
            # self.get_active_frame_name(self.frame_history[self.current_index])
            # self.set_new_active_frame(self.frame_names[self.current_index])

            active_frame_manager.set_active_frame(self.frame_history[self.current_index], self.frame_names[self.current_index])

            frame_to_pack = self.frame_history[self.current_index]
            if frame_to_pack is not None:
                frame_to_pack.pack(expand=True, fill='both')
            logger.info(f'successfully packed frame: {self.active_frame_name}')
        else:
            logger.error('FrameNavigator.pack_frame(): history is empty')
        self.hover_left_column_button_active()


    def go_back(self, *e):
        logger.info('FrameNavigator.go_back() called')
        if self.current_index is None:
            logger.info('going back for the first time')
            self.forget_active_frame(store=True)
            self.current_index = -2 #(# index set after forget_active_frame because frame was stored and index was set to None)
            self.dehover_left_column_buttons()
        elif len(self.frame_history) > abs(self.current_index):
            logger.info('going back once more')
            self.forget_active_frame(store=False)
            self.current_index -= 1
            self.dehover_left_column_buttons()
        else:
            logger.info('cant go back more')

        self.pack_frame()
    def go_forward(self, *e):
        logger.info('FrameNavigator.go_forward() called')
        if self.current_index is None:
            logger.info('cant go forward anymore')
            return
        if abs(self.current_index) == 1:
            logger.info('cant go forward anymore')
            return

        self.dehover_left_column_buttons()

        logger.info('going forward once more')
        self.forget_active_frame(store=False)
        self.current_index += 1

        self.pack_frame()

frame_navigator = FrameNavigator()


class ActiveFrameManager():
    def __init__(self):
        self.active_frame_type = None
        self.active_frame = None
    def set_active_frame(self, frame, frame_type):
        self.active_frame = frame
        self.active_frame_type = frame_type


active_frame_manager = ActiveFrameManager()