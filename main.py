import argparse, json
from kpi_rca.parser import parse_request
from kpi_rca.service import run_analysis
from kpi_rca.formatter import to_narrative, drivers_table, to_json


def main():
    # Define the CLI: one required question, the rest are the optional inputs from Box 1
    p = argparse.ArgumentParser(description="KPI Root-Cause Agent")
    p.add_argument("question")
    p.add_argument("--metric")
    p.add_argument("--current", help="YYYY-MM-DD to YYYY-MM-DD")
    p.add_argument("--baseline", help="YYYY-MM-DD to YYYY-MM-DD")
    p.add_argument("--filters", help='JSON, e.g. \'{"device":"all"}\'')
    p.add_argument("--json", action="store_true", help="print structured JSON only")
    a = p.parse_args()

    # Box 2: raw input -> validated AnalysisRequest (filters arrive as a JSON string)
    request = parse_request(a.question, a.metric, a.current, a.baseline,
                            json.loads(a.filters) if a.filters else None)
    print(f"Parsed request: {request.model_dump()}\n")

    # Boxes 3-10: run the agent loop and get the RCAReport
    report = run_analysis(request)

    # Box 11: display in the requested format
    if a.json:
        print(to_json(report))
    else:
        print(to_narrative(report))
        print("\nTop drivers:\n" + drivers_table(report))
        print("\nStructured JSON:\n" + to_json(report))


if __name__ == "__main__":
    main()