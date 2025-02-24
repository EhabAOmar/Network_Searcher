from fastapi import FastAPI, Form, Request, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from utils import search_network
import pandas as pd
from datetime import datetime
import shutil
import os


app = FastAPI()

# Mount the static folder for CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates (HTML rendering)
templates = Jinja2Templates(directory="templates")



# Route to serve the user form (HTML page)
@app.get("/")
async def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

UPLOAD_DIR = "uploads"  # Directory to store uploaded files
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create folder if it doesn't exist


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
    if (not file.filename.endswith(".csv") and not file.filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Only .csv & .xlsx files are allowed!")

    # Save the file under "uploads" folder
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extracting the data from the .CSV file
    if file.filename.endswith(".csv"):
        # Extracting the data from the .CSV file
        with open(file_location) as devices_list:
            lines = devices_list.readlines()

        # Delete the uploaded file after extracting devices information from it
        os.remove(file_location)

        # getting a dictionary contains the devices list in (IP-address:vendor) format
        try:
            devices = {line.split(",")[0].strip():line.split(",")[1].strip() for line in lines}
        except:
            raise HTTPException(status_code=500, detail="File Format Error --- Please be sure to write the format <ip-address>,<vendor> in the .csv file ---")
    else:
        # Reading the Excel sheet, will return into {Columns:{Rows}} dictionaries
        pd_read = pd.read_excel(file_location, header=None).to_dict()

        # Extracting device IP: Vendor from the Excel sheet Columns/Rows format
        devices = {pd_read[0][i]:pd_read[1][i] for i in pd_read[0].keys()}

        # Delete the uploaded file after extracting devices information from it
        os.remove(file_location)

    global IP_list
    IP_list = list(devices.keys())

    # Searching the devices for the keyword(s)
    global data
    data = search_network(username,password,keyword1,keyword2,operator,case_sensitive,devices)


    # Store data in session (or use query parameters)
    return templates.TemplateResponse("result.html", {"request": request, "data": data,"keyword1": keyword1 ,"keyword2": keyword2 ,"operator": operator, "case_sensitive": case_sensitive})


@app.get("/download/results")
async def download_excel():

    sheet = {}

    hostname_list, vendor_list, keyword_list, case_sensitive_list, matching_lines_list = [], [], [], [], []
    data_list = list(data.values())
    for item in data_list:
        hostname_list.append(item[0])
        vendor_list.append(item[1])
        keyword_list.append(item[2])
        case_sensitive_list.append(item[3])
        matching_lines_list.append(item[4])


    sheet["Device IP"] = IP_list
    sheet["Hostname"] = hostname_list
    sheet["Vendor/Model"] = vendor_list
    sheet["Keyword"] = keyword_list
    sheet["Case Sensitive"] = case_sensitive_list
    sheet["Configuration Lines"] = matching_lines_list

    # Convert dictionary to DataFrame
    df = pd.DataFrame(sheet)

    # Get the current date to tag it to the output file
    date_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    # Save DataFrame to an Excel file
    file_path = f"results_{date_time}.xlsx"
    df.to_excel(file_path, index=False)

    # Serve the file for download
    return FileResponse(file_path, filename=file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


TEMPLATE_PATH = "templates/template.xlsx"

@app.get("/download-template")
async def download_template():
    if os.path.exists(TEMPLATE_PATH):
        return FileResponse(TEMPLATE_PATH, filename="template.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return {"error": "File not found"}



# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)