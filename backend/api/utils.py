import pandas as pd
import subprocess
import os
from datetime import datetime

import shutil

# Try to find pdflatex in system path, fallback to hardcoded path for local dev
PDFLATEX_PATH = shutil.which("pdflatex") or r"D:\MikTEX\miktex\bin\x64\pdflatex.exe"


def analyze_csv(file):
    df = pd.read_csv(file)

    summary = {
        "total_equipment": int(len(df)),
        "avg_flowrate": float(df["Flowrate"].mean()),
        "avg_pressure": float(df["Pressure"].mean()),
        "avg_temperature": float(df["Temperature"].mean()),
        "type_distribution": df["Type"].value_counts().to_dict(),
        "table": df.to_dict(orient="records")
    }

    return summary


def generate_pdf_latex(summary):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    template_path = os.path.join(base_dir, "report_template.tex")
    tex_path = os.path.join(base_dir, "report.tex")
    pdf_path = os.path.join(base_dir, "report.pdf")

    # Safety check
    if not os.path.exists(PDFLATEX_PATH):
        raise FileNotFoundError(
            f"pdflatex.exe not found at {PDFLATEX_PATH}"
        )

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Generate professional Report ID
    report_id = f"REP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    type_rows = ""
    for k, v in summary["type_distribution"].items():
        type_rows += f"{k} & {v} \\\\\n"

    filled = (
        template
        .replace("{{REPORT_ID}}", report_id)
        .replace("{{TOTAL}}", str(summary["total_equipment"]))
        .replace("{{AVG_FLOWRATE}}", f"{summary['avg_flowrate']:.2f}")
        .replace("{{AVG_PRESSURE}}", f"{summary['avg_pressure']:.2f}")
        .replace("{{AVG_TEMPERATURE}}", f"{summary['avg_temperature']:.2f}")
        .replace("{{TYPE_ROWS}}", type_rows)
    )

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(filled)

    subprocess.run(
        [
            PDFLATEX_PATH,
            "-interaction=nonstopmode",
            tex_path
        ],
        cwd=base_dir,
        check=True
    )

    return pdf_path
