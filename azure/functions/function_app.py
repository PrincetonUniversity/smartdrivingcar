import azure.functions as func
from process_newsletter import bp

app = func.FunctionApp()
app.register_functions(bp)
