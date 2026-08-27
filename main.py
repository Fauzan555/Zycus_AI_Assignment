import argparse
import json
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from src.triage_agent import triage_ticket
from src.account_summariser import summarise_account_health
from evals.eval_harness import run_eval_harness

# Initialize FastAPI App
app = FastAPI(
    title="Zycus AI Support & TAM API",
    description="Production-grade AI microservices for Intelligent Ticket Triage and TAM Account Health Summarisation",
    version="1.0.0"
)


# Request & Response Schemas for FastAPI
class TicketInputSchema(BaseModel):
    subject: str = Field(..., description="Ticket subject line")
    body: str = Field(..., description="Ticket body content")
    product: Optional[str] = Field("DataBridge Pro", description="Product name")
    product_area: Optional[str] = Field("Connectors", description="Product area or module")


class TriageOutputSchema(BaseModel):
    product_area: str
    category: str
    urgency: str
    urgency_reasoning: str
    matched_doc: Optional[str] = None
    recommended_responder_team: str
    draft_response: str
    pii_scrubbed: Optional[Dict[str, int]] = None


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Zycus AI Technical Support & TAM Internal Tooling API",
        "version": "1.0.0",
        "endpoints": ["/triage (POST)", "/account-summary/{account_id} (GET)", "/eval-report (GET)"]
    }


@app.post("/triage", response_model=TriageOutputSchema)
def api_triage_ticket(payload: TicketInputSchema):
    """
    Task 1 REST Endpoint: Ingests a ticket payload and returns structured triage output.
    """
    try:
        result = triage_ticket(payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/account-summary/{account_id}")
def api_summarise_account(account_id: str, days: int = Query(90, ge=1, le=365)):
    """
    Task 2 REST Endpoint: Generates a deterministic QBR account health brief.
    """
    try:
        result = summarise_account_health(account_id, days=days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/eval-report")
def api_get_eval_report():
    """
    Task 3 REST Endpoint: Returns the latest evaluation harness report.
    """
    try:
        summary = run_eval_harness()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    parser = argparse.ArgumentParser(description="Zycus AI Support & TAM Engine")
    parser.add_argument("--triage", action="store_true", help="Run Task 1 sample ticket triage CLI")
    parser.add_argument("--summarise", type=str, help="Run Task 2 TAM account brief CLI (provide account_id)")
    parser.add_argument("--run-evals", action="store_true", help="Run Task 3 evaluation harness CLI")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI REST server on port 8000")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")

    args = parser.parse_args()

    if args.triage:
        print("\n--- Running Task 1: Ticket Triage CLI Demo ---")
        sample_ticket = {
            "subject": "CRITICAL: Unable to connect DataBridge Pro to Connectors",
            "body": "Hi team, Our Connectors pipeline has been failing since yesterday morning. Error message: 'ERR_CONNECTION_TIMEOUT after 30s'. Contact support@acme.com or +1-800-555-0199.",
            "product": "DataBridge Pro",
            "product_area": "Connectors"
        }
        output = triage_ticket(sample_ticket)
        print(json.dumps(output, indent=2))

    elif args.summarise:
        print(f"\n--- Running Task 2: TAM Account Summariser CLI Demo ({args.summarise}) ---")
        output = summarise_account_health(args.summarise)
        print(json.dumps(output, indent=2))

    elif args.run_evals:
        run_eval_harness()

    elif args.serve:
        print(f"Starting FastAPI server on http://0.0.0.0:{args.port}...")
        uvicorn.run("main:app", host="0.0.0.0", port=args.port, reload=True)

    else:
        # Default behavior if no flags passed: run evals and display help
        print("No specific command flag passed. Executing Task 3 Evaluation Harness by default...\n")
        run_eval_harness()


if __name__ == "__main__":
    main()
