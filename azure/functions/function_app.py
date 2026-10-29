import azure.functions as func
from process_newsletter import bp
from connector_handler import connector_bp

app = func.FunctionApp()
app.register_functions(bp)

app.register_functions(connector_bp)
