import dukpy


class JSContext:
    """
    A class to manage a JavaScript context using `dukpy`.
    """

    def __init__(self):
        self.interp = dukpy.JSInterpreter()
        self.result = None

    def _register(self, data):
        for func_name, func in data:
            self.apply_function(func_name, func)

    def apply_function(self, function_name: str, function):
        """
        Register a Python function to be callable from JavaScript.

        :param function_name: The name of the function in JavaScript.
        :param function: The Python function to register.
        """
        self.interp.export_function(function_name, function)

    def run(self, script: str, code: str):
        """
        Execute a block of JavaScript code.

        :param script: The name for the script (for debugging purposes).
        :param code: The JavaScript code to execute.
        """
        try:
            return self.interp.evaljs(code)
        except dukpy.JSRuntimeError as e:
            raise RuntimeError(
                f"JavaScript execution error in script '{script}': {e}"
            ) from e
