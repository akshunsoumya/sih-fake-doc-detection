# AI-Based Identity Document Forgery Detection

## Short Project Overview

This project is a web-based system that takes an uploaded identity document image — such as a passport, national ID, or visa — and analyzes it to flag it as **Genuine**, **Suspicious**, or **Fake**. It combines Optical Character Recognition (OCR), Machine Readable Zone (MRZ) validation, and image tampering detection techniques to give a fast, explainable risk score for a document, along with the specific reasons behind that score.

This project was built for **Smart India Hackathon (SIH)** as a working prototype demonstrating how AI-assisted document screening can support identity verification at checkpoints such as borders, airports, and KYC counters.

> **Important:** This system is a **screening aid**, not a legal or forensic verdict. Its output is meant to help a human verifier make a faster, more informed decision — it does not replace official document verification processes or government identity checks.

---

## Problem Statement

Identity document fraud — including photo substitution, edited text fields, copy-move tampering, and fully fabricated documents — is difficult to catch quickly through manual inspection alone. Officers at checkpoints (border control, airports, hotel check-ins, KYC counters) often have very limited time to examine each document, which increases the risk of forged documents going unnoticed.

There is a need for a fast, first-level AI-assisted screening tool that can:

- Extract and validate the text and structured data on a document
- Detect signs of digital tampering in the image itself
- Present a clear, explainable risk assessment to the person reviewing the document

This project addresses that need with a practical, demonstrable prototype.

---

## Why This Project Matters

- **Speed:** Manual document checks are slow under high foot-traffic conditions (e.g., border crossings, airport counters). An automated first-pass screening tool can significantly reduce review time.
- **Consistency:** Human reviewers can miss subtle signs of tampering due to fatigue or time pressure. Automated checks (like MRZ checksum validation) apply the same rigorous standard every time.
- **Explainability:** Instead of a black-box "fake or real" answer, this system shows *why* a document was flagged, which builds trust and helps the human reviewer make the final call.
- **Real-world relevance:** Document fraud is a persistent issue across immigration, banking KYC, hospitality, and government services — this system is designed to be adaptable across these use cases.

---

## Features

### Implemented / In Progress

- **Document upload interface** — users can upload a JPG/PNG image of a document through a simple web page.
- **OCR-based text extraction** — extracts visible fields such as name, date of birth, and document number using Tesseract OCR.
- **MRZ (Machine Readable Zone) validation** — for passports and visas, reads the machine-readable code at the bottom of the document and validates its built-in checksum digits to detect tampering.
- **Tamper detection** — analyzes the image using: 
  - **Error Level Analysis (ELA)** to detect regions with inconsistent compression (a sign of digital editing)
  - **Copy-move detection** to find duplicated regions within the same image
  - **Metadata (EXIF) inspection** to check for missing camera data or editing-software signatures
- **Risk scoring engine** — combines the results of all checks into a single risk label (**Low / Medium / High**) along with a plain-language list of reasons.
- **Result dashboard** — displays the uploaded document, extracted fields, risk score, and reasons in a clear visual format.

### Planned / Future Scope

- Face/photo region tamper check as a dedicated module
- Operator login and authentication system
- History log of previously checked documents
- Support for additional document types beyond passport and national ID
- Deployment to a public hosted environment

*(See* [*Future Scope*](https://claude.ai/chat/d72c98de-e416-4a0a-8c0b-3ef66adc9c4e#future-scope) *for the complete list.)*

---

## How the System Works

The system processes a document through the following pipeline:

1. **Upload** — The user uploads a document image through the frontend.
2. **Preprocessing** — The image is resized, denoised, and straightened (deskewed) to improve accuracy of later steps.
3. **OCR (Text Extraction)** — All visible text on the document is extracted, and key fields (name, date of birth, document number) are parsed out.
4. **MRZ Reading** *(for passports/visas)* — The machine-readable code at the bottom of the document is parsed and its checksum digits are validated mathematically.
5. **Tamper Detection** — The image is analyzed using Error Level Analysis, copy-move detection, and metadata inspection to identify signs of digital editing.
6. **Risk Scoring** — All the results above are combined using a rule-based scoring function into a final risk label with supporting reasons.
7. **Result Display** — The final result, along with the extracted document image, fields, and reasons, is shown to the user on the result page.

Each step above is handled by an independent module, which keeps the codebase organized and allows multiple team members to work on different parts of the pipeline in parallel.

---

## Tech Stack

| Layer Technology                       |                                                    |
| -------------------------------------- | -------------------------------------------------- |
| **Frontend**                           | React (or plain HTML/CSS/JavaScript), Tailwind CSS |
| **Backend**                            | Python, FastAPI                                    |
| **Database**                           | SQLite                                             |
| **OCR**                                | Tesseract OCR (via `pytesseract`)                  |
| **MRZ Reading**                        | PassportEye                                        |
| **Computer Vision / Image Processing** | OpenCV, Pillow                                     |
| **Version Control**                    | Git & GitHub                                       |

We chose classical computer vision and rule-based techniques (ELA, MRZ checksum validation, copy-move detection) instead of a custom-trained deep learning model. This decision was made because:

- These techniques are explainable — every flagged result comes with a clear, understandable reason.
- They do not require large labeled training datasets, which are difficult to obtain for this problem due to privacy and security restrictions on real identity document data.
- They are realistic to build and validate within the SIH project timeline.

---

## Repository Structure

```
sih-fake-doc-detection/
├── frontend/                  # Web UI (upload page, result dashboard)
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/                   # FastAPI application and API routes
│   ├── app/
│   │   ├── main.py            # API entry point, orchestrates all modules
│   │   └── common/            # Shared utilities (e.g., preprocessing)
│   └── requirements.txt
├── ml_modules/                 # OCR, MRZ, and tamper detection logic
│   ├── ocr_module/
│   ├── mrz_module/
│   └── tamper_module/
├── dataset/
│   ├── genuine/                # Genuine/specimen sample document images
│   └── fake/                   # Tampered/synthetic sample document images
├── docs/                        # Documentation, architecture notes, API contract
│   ├── architecture.png
│   └── api_contract.md
├── .gitignore
├── README.md
└── LICENSE

```

**Notes on structure:**

- `ml_modules/` keeps all detection logic (OCR, MRZ, tamper checks) separate from the backend's API/orchestration code, so each can be developed and tested independently.
- `dataset/` contains only small sample images used for development and demo purposes — see [Dataset Strategy](https://claude.ai/chat/d72c98de-e416-4a0a-8c0b-3ef66adc9c4e#dataset-strategy) below.
- Large files (raw video, large datasets) are not committed directly to this repository; links to external storage (Google Drive/YouTube) are used instead where applicable.

---

## Setup Instructions

These instructions cover Windows, macOS, and Linux development environments.

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher (if using the React frontend)
- Tesseract OCR installed on your system (required for `pytesseract` and `PassportEye`)

**Installing Tesseract OCR:**

**Windows:**

Install Tesseract OCR using the Windows installer/package available from the official Tesseract project or a trusted Windows distribution. After installation, make sure the Tesseract executable is available in your system `PATH`. If it is not, configure the Tesseract path in the Python application (for example, through `pytesseract.pytesseract.tesseract_cmd`).

**macOS (using Homebrew):**

```bash
brew install tesseract
```

**Ubuntu/Debian Linux:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### 1. Clone the repository

```bash
git clone https://github.com/<your-org-or-username>/sih-fake-doc-detection.git
cd sih-fake-doc-detection

```

### 2. Backend setup

**Windows (PowerShell):**

```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, you can run the commands from Command Prompt instead:

```cmd
cd backend
py -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd ../frontend
npm install

```

### 4. Environment variables

Create a `.env` file inside `backend/` for any configuration values (e.g., database file path). This file is excluded from version control via `.gitignore` and should never be committed.

---

## How to Run the Project

### Start the backend server

**Windows (PowerShell):**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Windows (Command Prompt):**

```cmd
cd backend
venv\Scripts\activate.bat
uvicorn app.main:app --reload
```

**macOS / Linux:**

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`.

### Start the frontend

In a separate terminal:

```bash
cd frontend
npm run dev

```

The web app will be available at `http://localhost:5173` (or the port shown in your terminal).

### Using the application

1. Open the frontend in your browser.
2. Upload a document image (JPG or PNG).
3. Wait for the system to process the document.
4. View the risk score, extracted fields, and reasons on the result page.

---

## API Overview

The backend exposes a single primary endpoint that the frontend communicates with:

### `POST /analyze`

**Description:** Accepts an uploaded document image and returns a combined analysis result.

**Request:** `multipart/form-data` containing the image file.

**Response (example):**

```json
{
  "document_type": "passport",
  "extracted_fields": {
    "name": "SAMPLE NAME",
    "date_of_birth": "1998-05-14",
    "document_number": "A1234567"
  },
  "mrz_check": {
    "checksum_valid": true
  },
  "tamper_check": {
    "ela_score": 12,
    "copy_move_detected": false,
    "metadata_flag": false
  },
  "risk_score": "Low",
  "reasons": [
    "MRZ checksum passed",
    "No significant compression inconsistency detected",
    "No duplicated regions found in the image"
  ]
}

```

> **Note:** This response format is the agreed API contract for the project (see `docs/api_contract.md`). Any changes to field names or structure must be communicated to the whole team before implementation, since both frontend and backend code depend on this exact shape.

---

## Dataset Strategy

Real government-issued identity documents (such as actual citizens' Aadhaar cards or passports) **cannot be used** in this project due to privacy and legal restrictions. Instead, this project relies on:

- **Public specimen datasets** — publicly available mock/specimen identity document datasets designed for document analysis research (e.g., MIDV-500, MIDV-2020), which use artificially generated or non-real identity data.
- **Synthetic sample data** — sample "genuine" document templates that the team has manually edited (photo swapped, text altered, regions duplicated) to create labeled "fake"/tampered examples for testing.

All sample images used in `dataset/genuine/` and `dataset/fake/` are either public specimens or team-created synthetic examples — **no real personal identity data is used or stored in this repository.**

Each sample is labeled in `dataset/labels.csv` with its filename, class (genuine/fake), tamper type, and document type, to support consistent testing of the detection pipeline.

---

## Team Members and Roles

| Member Name | Responsibility |
| ----------- | -------------- |
|             |                |
|             |                |
|             |                |
|             |                |
|             |                |
|             |                |

*(Team member names and responsibilities will be added as the project roles are finalized.)*

---

## GitHub Workflow

This repository follows a simple, structured branching model to support parallel development across the team:

- **`main`** — the protected, stable branch. Only fully tested, working code is merged here. This branch reflects the current demo-ready state of the project.
- **`dev`** — the integration branch. All completed feature work is merged here first for combined testing before being promoted to `main`.
- **Member branches** — each team member works on their own branch (e.g., `feature/abhay-ocr`, `feature/shoaib-tamper`) to develop their assigned module without affecting others' work.

**General workflow:**

1. Pull the latest `dev` branch before starting new work.
2. Create or switch to your personal feature branch.
3. Commit changes with clear, descriptive messages.
4. Push your branch and open a Pull Request into `dev`.
5. Changes are reviewed before merging into `dev`, and periodically, a stable `dev` state is merged into `main`.

This workflow keeps `main` always in a stable, demo-ready condition, while allowing active development to continue safely in parallel across the team.

---

## Known Limitations

- The system currently supports a limited set of document types (passport and one national ID format); broader document support is planned but not yet implemented.
- Tamper detection is based on classical computer vision techniques (ELA, copy-move, metadata analysis) rather than a trained deep learning model, so detection accuracy is bounded by the strength of these techniques rather than learned pattern recognition.
- The dataset used for testing is limited in size (public specimen data plus a small set of team-created synthetic samples), since large labeled datasets of forged identity documents are not publicly available for privacy and security reasons.
- There is currently no integration with any official government identity verification database — all analysis is performed solely on the uploaded image itself.
- Face/photo-region-specific tamper detection is not yet implemented as a dedicated module.
- The system does not currently include user authentication or a history log of past checks.

---

## Future Scope

- Dedicated face/photo region tamper detection module
- Operator login and role-based access
- History and audit log of all previously analyzed documents
- Support for a wider range of document types and countries
- Real-time integration with checkpoint camera hardware
- Exploration of deep learning–based tamper classifiers, contingent on availability of a larger, properly labeled training dataset
- Deployment to a publicly hosted environment for wider accessibility

---

## Contribution Guidelines

This repository is maintained by the SIH project team listed above. If you are a team member contributing to this project:

1. Always branch off from the latest `dev` branch.
2. Keep your changes scoped to your assigned module folder wherever possible.
3. Write clear, descriptive commit messages (e.g., `feat: add MRZ checksum validation`, `fix: handle blurry OCR input`).
4. Open a Pull Request into `dev` and request a review before merging.
5. Do not commit large files (raw datasets, video files) directly — use external links where applicable.
6. Do not commit `.env` files or any sensitive configuration values.
7. Ensure your code runs without errors locally before opening a Pull Request.

---

## License

This project is released under the MIT License. See the `LICENSE` file for full details.

---

*This README serves as the primary reference document for the project. It will be updated as the system evolves throughout development.*