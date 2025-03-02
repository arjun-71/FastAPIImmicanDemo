from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import csv
import io
import os

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# Path to store the uploaded CSV file
CSV_FILE_PATH = "uploaded_data.csv"

# Pydantic model for the CSV data
class JobData(BaseModel):
    proposed_job_title: str = Field(..., alias='Proposed Job Title')                    
    image: str = Field(..., alias='Image')
    job_sector: str = Field(..., alias='Job Sector')
    province: str = Field(..., alias='Select Province')
    job_score: str = Field(..., alias='Job score')
    job_approximate_time: str = Field(..., alias='Job Approximate Time')
    settlement_score: str = Field(..., alias='Settlement Score')
    settlement_approximate_time: str = Field(..., alias='Settlement Approximate Time')

    class Config:
        # Ensure that the model uses the aliases when serializing to JSON
        allow_population_by_field_name = True

# PUT endpoint to upload CSV file
@app.put("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
    
    try:
        content = await file.read()
        csv_reader = csv.DictReader(io.StringIO(content.decode('utf-8')))
        
        data = []
        for row in csv_reader:
            # Map CSV columns to the Pydantic model
            job_data = JobData(
                proposed_job_title=row['Proposed Job Title'],
                image=row['Image'],
                job_sector=row['Job Sector'],
                province=row['Select Province'],
                job_score=row['Job score'],
                job_approximate_time=row['Job Approximate Time'],
                settlement_score=row['Settlement Score'],
                settlement_approximate_time=row['Settlement Approximate Time']
            )
            data.append(job_data)
        
        # Optionally, save the validated data to a file
        with open(CSV_FILE_PATH, "w", newline='', encoding='utf-8') as csvfile:
            fieldnames = job_data.dict().keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item.dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")
    
    return {"message": "CSV file uploaded and processed successfully"}

# GET endpoint to fetch data from the uploaded CSV file
@app.get("/data/", response_model=List[JobData])
async def get_data():
    if not os.path.exists(CSV_FILE_PATH):
        raise HTTPException(status_code=404, detail="CSV file not found. Please upload a file first.")
    
    data = []
    try:
        with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                job_data = JobData(
                    proposed_job_title=row['Proposed Job Title'],
                    image=row['Image'],
                    job_sector=row['Job Sector'],
                    province=row['Select Province'],
                    job_score=row['Job score'],
                    job_approximate_time=row['Job Approximate Time'],
                    settlement_score=row['Settlement Score'],
                    settlement_approximate_time=row['Settlement Approximate Time']
                )
                data.append(job_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV file: {e}")
    
    return data

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "FastAPI is working!"}
