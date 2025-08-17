from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
from gemini_client import GeminiClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RFP Proposal Analyzer API", version="1.0.0")

# Initialize Gemini client
gemini = GeminiClient()


# ---------- FILE PROCESSING ----------
async def process_uploaded_file_Proposal(uploaded_file: UploadFile):
    """Process uploaded file and extract text using Gemini"""
    if uploaded_file is not None:
        file_type = uploaded_file.content_type
        file_name = uploaded_file.filename

        try:
            if file_type == "text/plain":
                content = (await uploaded_file.read()).decode("utf-8")
                return content

            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                content = await gemini.extract_text_from_docx_proposal(uploaded_file)
                return content if content else None

            elif file_type == "application/pdf":
                content = await gemini.extract_text_from_uploaded_pdf_proposal(uploaded_file)
                return content if content else None

            else:
                return None

        except Exception as e:
            raise Exception(f"Error processing file {file_name}: {str(e)}")

    return None


# ---------- Pydantic Models ----------
class AnalysisRequest(BaseModel):
    proposal_text: str
    extra_components: Optional[str] = None


class RFPAnalysisRequest(BaseModel):
    rfp_text: str
    company_profile: Optional[str] = None


class AnalysisResponse(BaseModel):
    status: str
    analyze_proposal: str
    error: Optional[str] = None


class analyzePricingRequest(BaseModel):
    proposal_text:str
    ai_analysis_details: str
    historical_data:Optional[str] = None


class analyzePricingResponse(BaseModel):
    status: str
    result: str
    error: Optional[str] = None



# ---------- Routes ----------
@app.get("/")
async def root():
    return {"message": "RFP Proposal Analyzer API is running"}


@app.post("/upload/proposal")
async def upload_proposal_file(file: UploadFile = File(...)):
    """Upload and extract text from proposal file"""
    try:
        text = await process_uploaded_file_Proposal(file)

        if text is None:
            raise HTTPException(status_code=400, detail="Failed to process the file")

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "filename": file.filename,
                "content_type": file.content_type,
                "text": text,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_proposal_components", response_model=AnalysisResponse)
async def analyze_proposal_components(request: AnalysisRequest):
    try:
        analyze_proposal_result = await gemini.analysis_proposal(request.proposal_text, request.extra_components)
        return AnalysisResponse(status="success", analyze_proposal=analyze_proposal_result)
    except Exception as e:
        return AnalysisResponse(status="error", analyze_proposal_result="", error=str(e))


@app.post("/analyze/pricing", response_model=analyzePricingResponse)
async def analyze_pricing_api(request: analyzePricingRequest):
    try:
    
        result = await gemini.analyze_pricing(request.proposal_text, request.ai_analysis_details)
        return analyzePricingResponse(status="success", result=result)
    except Exception as e:
        return analyzePricingResponse(status="error", result="", error=str(e))


@app.post("/analyze/cost-realism", response_model=AnalysisResponse)
async def analyze_cost_realism(request: AnalysisRequest):
    try:
        component_analysis = gemini.analysis_proposal(request.proposal_text, request.extra_components)
        result = gemini.analyze_cost_realism(request.proposal_text, component_analysis)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))


@app.post("/analyze/technical", response_model=AnalysisResponse)
async def technical_analysis(request: AnalysisRequest):
    try:
        result = gemini.technical_analysis_review(request.proposal_text)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))


@app.post("/analyze/compliance", response_model=AnalysisResponse)
async def compliance_analysis(request: AnalysisRequest):
    try:
        result = gemini.compliance_assessment(request.proposal_text)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))


@app.post("/rfp/analyze", response_model=AnalysisResponse)
async def analyze_rfp(request: RFPAnalysisRequest):
    try:
        result = gemini.analyze_rfp(request.rfp_text)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))


@app.post("/rfp/eligibility", response_model=AnalysisResponse)
async def check_eligibility(request: RFPAnalysisRequest):
    try:
        if not request.company_profile:
            raise HTTPException(status_code=400, detail="Company profile required")
        result = gemini.analyze_eligibility(request.rfp_text, request.company_profile)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))


@app.post("/rfp/generate-proposal", response_model=AnalysisResponse)
async def generate_proposal(request: RFPAnalysisRequest):
    try:
        if not request.company_profile:
            raise HTTPException(status_code=400, detail="Company profile required")
        result = gemini.generate_project_proposal(request.rfp_text, request.company_profile)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))


@app.post("/generate/summary", response_model=AnalysisResponse)
async def generate_summary(
    proposal_text: str = Form(...),
    component_analysis: Optional[str] = Form(None),
    price_analysis: Optional[str] = Form(None),
    cost_realism: Optional[str] = Form(None),
    technical_analysis: Optional[str] = Form(None),
    compliance_assessment: Optional[str] = Form(None),
):
    try:
        result = gemini.analysis_proposal_summary(
            proposal_text,
            component_analysis,
            price_analysis,
            cost_realism,
            technical_analysis,
            compliance_assessment,
        )
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
