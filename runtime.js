window = {
  console: {
    log: function (x) {
      call_python("log", x);
    },
  },

  history: {
    print: function () {
      call_python("print_history");
    },
    clear: function () {
      call_python("clear_history");
    },
    next: function () {
      call_python("get_next_history_url");
    },
    prev: function () {
      call_python("get_prev_history_url");
    },
  },
};

console = window.console;
history = window.history;
