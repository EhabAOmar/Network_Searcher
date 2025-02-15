import time
import shutil
import os
from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, File, UploadFile,HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from utils import search_network



app = FastAPI()

# Mount the static folder for CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates (HTML rendering)
templates = Jinja2Templates(directory="templates")



# Route to serve the user form (HTML page)
@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

UPLOAD_DIR = "uploads"  # Directory to store uploaded files
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create folder if it doesn't exist

def progress_bar():
    for i in range(1, 2):
        time.sleep(1)  # Simulate progress update every second


@app.post("/submit/")
async def process_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    keyword1: str = Form(...),
    keyword2: str = Form(...),
    operator: str = Form(...),
    case_sensitive: bool = Form(False),
    file: UploadFile = File(...)
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed!")

    # Save the file under "uploads" folder
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extracting the data from the .CSV file
    with open(file_location) as devices_list:
        lines = devices_list.readlines()

    # getting a dictionary contains the devices list in (IP-address:vendor) format
    try:
        devices = {line.split(",")[0].strip():line.split(",")[1].strip() for line in lines}
    except:
        raise HTTPException(status_code=500, detail="File Format Error --- Please be sure to write the format <ip-address>,<vendor> in the .csv file ---")
    # Searching the devices for the keyword(s)
    data = search_network(username,password,keyword1,keyword2,operator,case_sensitive,devices)

    # Show progress bar "future feature"
    progress_bar()

    # Store data in session (or use query parameters)
    return templates.TemplateResponse("result.html", {"request": request, "data": data,"keyword1": keyword1 ,"keyword2": keyword2 ,"operator": operator, "case_sensitive": case_sensitive})


# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)