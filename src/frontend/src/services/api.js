const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const documentTypeMap = {
  "Aadhaar Card": "aadhaar",
  Passport: "passport",
  Other: "other",
};

export async function analyzeDocument(file, documentType) {
  const formData = new FormData();

  formData.append("file", file);
  formData.append(
    "document_type",
    documentTypeMap[documentType] || "other"
  );

  const response = await fetch(
    `${API_BASE_URL}/api/analyze`,
    {
      method: "POST",
      body: formData,
    }
  );

  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      result.detail || "Document analysis failed."
    );
  }

  return result;
}