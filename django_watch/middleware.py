import time
import logging
import traceback


def unwrap(func):
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func


class WatchMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.BLACK = "\033[0;30m"
        self.RED = "\033[0;31m"
        self.GREEN = "\033[0;32m"
        self.BROWN = "\033[0;33m"
        self.BLUE = "\033[0;34m"
        self.PURPLE = "\033[0;35m"
        self.CYAN = "\033[0;36m"
        self.LIGHT_GRAY = "\033[0;37m"
        self.DARK_GRAY = "\033[1;30m"
        self.LIGHT_RED = "\033[1;31m"
        self.LIGHT_GREEN = "\033[1;32m"
        self.YELLOW = "\033[1;33m"
        self.LIGHT_BLUE = "\033[1;34m"
        self.LIGHT_PURPLE = "\033[1;35m"
        self.LIGHT_CYAN = "\033[1;36m"
        self.LIGHT_WHITE = "\033[1;37m"
        self.BOLD = "\033[1m"
        self.FAINT = "\033[2m"
        self.ITALIC = "\033[3m"
        self.UNDERLINE = "\033[4m"
        self.BLINK = "\033[5m"
        self.NEGATIVE = "\033[7m"
        self.CROSSED = "\033[9m"
        self.END = "\033[0m"

    def __call__(self, request):
        response = None
        time_start = time.monotonic()    
        response = self.get_response(request)
        if hasattr(response, "status_code") and hasattr(request, "process_stdout_end") and request.process_stdout_end:
            process_stdout_end = request.process_stdout_end            
            process_stdout_end += f"{self.YELLOW} • STATUS {response.status_code} • Total time • {round((time.monotonic() - time_start), 2)}s{self.END}"        
            print(process_stdout_end)
        return response

    def process_view(self, request, func, args, kwargs):
        view_class = getattr(func, "view_class", None)
        func = unwrap(func)

        if view_class:
            method_name = request.method.lower()
            method_func = getattr(view_class, method_name, None)
            code = method_func.__code__ if method_func and hasattr(method_func, "__code__") else None
            display_name = f"{view_class.__name__}.{method_name}"
            filename = code.co_filename if code else ""
            lineno = code.co_firstlineno if code else "?"
            process_stdout_start = f"\n░░ {self.BOLD}{request.method} {filename} {self.END} • {self.GREEN}{display_name}{self.END} • {self.YELLOW}Line number {lineno}{self.END}"
            request.process_stdout_end = f"\n░░ {self.BOLD}{request.method} {filename} {self.END} • {self.GREEN}{display_name} [  OK  ]{self.END}"
        elif hasattr(func, "__code__"):
            process_stdout_start = f"\n░░ {self.BOLD}{request.method} {func.__code__.co_filename} {self.END} • {self.GREEN}{func.__name__}{self.END} • {self.YELLOW}Line number {func.__code__.co_firstlineno}{self.END}"
            request.process_stdout_end = f"\n░░ {self.BOLD}{request.method} {func.__code__.co_filename} {self.END} • {self.GREEN}{func.__name__} [  OK  ]{self.END}"
        else:
            return

        print(process_stdout_start)
            if args: 
                print(f"░░░░ args: {args}"[:200])
            if kwargs: 
                print(f"░░░░ kwargs: {kwargs}"[:200])
            if request.GET:
                print(f"░░░░ request.GET: {request.GET}"[:200])                
            if request.POST: 
                print(f"░░░░ request.POST: {request.POST}"[:200])
                
            try:
                if not request.POST and request.body:
                    print(f"░░░░ request.body: {request.body}"[:200])
            except Exception as e:
                pass
            
    def process_exception(self, request, exception):
        print(f"{self.RED}{self.BOLD}░ Exception{self.END}{self.END}")
        print( "░░░░ TRACEBACK:\n{}".format( "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))))
