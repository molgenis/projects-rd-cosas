#'////////////////////////////////////////////////////////////////////////////
#' FILE: cli.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-05-04
#' MODIFIED: 2022-05-04
#' PURPOSE: colored terminal messages
#' STATUS: stable
#' PACKAGES: 
#' COMMENTS: 
#'////////////////////////////////////////////////////////////////////////////

class cli:
    def __init__(self):
        self._start = '\u001b'
        self._stop = '\u001b[0m'
        self._blue = '[34;1m'
        self._green = '[32:1m'
        self._red = '[31;1m'
        self._white = '[37;1m'
        self._yellow = '[33;1m'
        
        self.error = self._setStatus(self._red, '⨉')
        self.success = self._setStatus(self._green, '✓')
        self.warning = self._setStatus(self._yellow, '!')
        
    def _setStatus(self, color, text):
        return self._start + color + text + self._stop
        
    def _print(self, color, text):
        print(self.start, color, text, self.stop)
    
    def alert_success(self, text):
        """Print a success message"""
        print(f'{self.success} {text}')

    def alert_error(self, text):
        """Print an error message"""
        print(f'{self.error} {text}')

    def alert_warning(self, text):
        """Print a warning message"""
        print(f'{self.warning} {text}')
        
    def text_value(self, text):
        """Style text as a value"""
        return self._start + self._blue + str(text) + self._stop
    
    def text_success(self, text):
        """Style text as a success message"""
        return self._start + self._green + str(text) + self._stop
        
    def text_error(self, text):
        """Style text as an error message"""
        return self._start + self._red + str(text) + self._stop
    
    def text_warning(self, text):
        """Style text as an warning message"""
        return self._start + self._yellow + str(text) + self._stop