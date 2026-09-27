# KPI Root-Cause Agent

An autonomous, enterprise-grade AI agent powered by **LangChain** and **LangGraph** designed to automate business metrics investigation, driver breakdown, and automated root-cause analysis (RCA).

Given a plain-language prompt (e.g., *"Why did checkout conversion drop 12% this week?"*), this system formulates diagnostic hypotheses, runs deterministic data warehouse queries (SQL/Pandas), parses structural evidence, and delivers validated, structured diagnostic reports (`RCAReport`).

---

## 🌟 Architecture & Key Features

* **Autonomous Hypothesis Engine:** Iteratively tests metric anomalies using short-term state memory (`InMemStateSaver`) without hallucinations.
* **Deterministic Tool Execution:** Connects directly to data warehouses (PostgreSQL, Snowflake, BigQuery) via Pandas and SQLAlchemy for precise metric rollups and dimensional breakdowns.
* **Type-Safe Structured Output:** Enforces reliable input parsing (`AnalysisRequest`) and schema-validated final report outputs (`RCAReport`) using Pydantic.
* **Loop-Based Reasoning:** Evaluates evidence confidence dynamically through continuous tool interaction until full diagnostic coverage is achieved.

---

## 🛠️ Built With

* **Orchestration:** LangChain, LangGraph
* **Data Processing:** Python, Pandas, SQLAlchemy, Pydantic
* **LLM Engine:** OpenAI GPT-4o 
* **Environment:** Python 3.10+

---

## 💼 Commercial Use, Custom AI Development & Consulting

This repository serves as an open architectural prototype for autonomous data diagnostics.

If your organization requires **custom Agentic AI pipelines**, **production-grade enterprise analytics**, or **tailored machine learning integration**, **[Elute Insights](https://eluteinsights.com)** provides end-to-end data consulting services:

* **Agentic AI & LLM Systems:** Enterprise AI agents, RAG pipelines, and automated workflow agents.
* **Data Science & Machine Learning:** Predictive modeling, churn analysis, customer segmentation, and causal inference.
* **Data Engineering & Analytics:** Warehouse setup, BI visualizers, and SQL query automation platforms.

### Contact & Inquiries
* **Founder:** Kanak Agrawal
* **Company:** Elute Insights
* **Email:** [kanak@eluteinsights.com](mailto:kanak@eluteinsights.com)
* **Services & Portfolio:** Reach out directly via email to request a custom demo or schedule a scoping call for your organization's data needs.

---

## 📄 License

This repository is licensed under the **CC BY-NC 4.0 License** (Creative Commons Attribution-NonCommercial 4.0 International).

* **Personal & Educational Use:** Free to inspect, download, and adapt for personal or research purposes.
* **Commercial Use:** Any commercial deployment, SaaS integration, or enterprise implementation requires explicit commercial licensing from Elute Insights. Please contact [kanak@eluteinsights.com](mailto:kanak@eluteinsights.com) for details.


# kpi-root-cause-agent
An autonomous LangChain &amp; LangGraph agent for automated KPI root-cause analysis, anomaly detection, and data driver attribution using Python, Pydantic, and SQL.
