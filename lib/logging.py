import threading
import sublime


class Loger:
    debug = False
    employer = "CodeCounter"

    def print(*args):
        if Loger.debug:
            print("CodeCounter:", *args)

    def error(errmsg):
        sublime.error_message(errmsg)

    def threading(function, ing_msg, done_msg, on_done=None):
        def check(last_view, i, d):
            active_view = sublime.active_window().active_view()
            if last_view != active_view:
                last_view.erase_status(Loger.employer)

            if not thread.is_alive():
                cleanup = active_view.erase_status
                Loger.print(done_msg)
                active_view.set_status(Loger.employer, done_msg)
                sublime.set_timeout(lambda: cleanup(Loger.employer), 2000)
                if on_done is not None:
                    on_done()
                return

            dynamic = " [%s=%s]" % (' ' * i, ' ' * (7 - i))
            active_view.set_status(Loger.employer, ing_msg + dynamic)

            if i == 0 or i == 7:
                d = -d

            sublime.set_timeout(lambda: check(active_view, i + d, d), 100)

        Loger.print("Start " + ing_msg)
        thread = threading.Thread(target=function)
        thread.start()
        check(sublime.active_window().active_view(), 0, -1)
