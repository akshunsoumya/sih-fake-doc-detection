import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  History as HistoryIcon,
  Search,
  Filter,
  FileText,
  ShieldCheck,
  ShieldAlert,
  Clock3,
  ChevronRight,
  CalendarDays,
  X,
  RefreshCw,
  Database,
} from "lucide-react";

import "./History.css";


/*
=============================================================
MOCK HISTORY DATA
=============================================================

This data is ONLY for frontend development.

WHEN BACKEND IS READY:
Remove/replace this mock data with the response received
from your Node.js backend.

Expected backend response can look like:

[
  {
    id: "analysis_001",
    documentType: "Aadhaar Card",
    fileName: "aadhaar.jpg",
    result: "Authentic",
    confidence: 96,
    riskScore: 4,
    createdAt: "2026-09-03T14:30:00"
  }
]

=============================================================
*/

const mockHistory = [
  {
    id: "analysis_001",
    documentType: "Aadhaar Card",
    fileName: "aadhaar_front.jpg",
    result: "Authentic",
    confidence: 96,
    riskScore: 4,
    createdAt: "2026-09-03T14:30:00",
  },

  {
    id: "analysis_002",
    documentType: "Passport",
    fileName: "passport_scan.png",
    result: "Forged",
    confidence: 91,
    riskScore: 87,
    createdAt: "2026-09-02T18:45:00",
  },

  {
    id: "analysis_003",
    documentType: "Aadhaar Card",
    fileName: "document_03.jpg",
    result: "Forged",
    confidence: 88,
    riskScore: 79,
    createdAt: "2026-09-02T11:20:00",
  },

  {
    id: "analysis_004",
    documentType: "Passport",
    fileName: "passport_front.jpg",
    result: "Authentic",
    confidence: 94,
    riskScore: 6,
    createdAt: "2026-09-01T16:10:00",
  },

  {
    id: "analysis_005",
    documentType: "Other",
    fileName: "official_document.jpg",
    result: "Authentic",
    confidence: 89,
    riskScore: 11,
    createdAt: "2026-08-31T13:35:00",
  },

  {
    id: "analysis_006",
    documentType: "Aadhaar Card",
    fileName: "aadhaar_copy.png",
    result: "Forged",
    confidence: 94,
    riskScore: 92,
    createdAt: "2026-08-30T10:05:00",
  },
];


function History() {

  /*
  ============================================================
  STATE
  ============================================================
  */

  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [documentFilter, setDocumentFilter] = useState("All");


  /*
  ============================================================
  BACKEND INTEGRATION AREA
  ============================================================

  WHEN BACKEND IS READY:

  1. Remove mockHistory usage.
  2. Create state:

       const [historyData, setHistoryData] = useState([]);

  3. Fetch the user's analysis history from Node.js:

       const response = await fetch(
         "http://localhost:5000/api/history"
       );

       const data = await response.json();

       setHistoryData(data);

  4. Authentication/user identification can later be
     added here as well.

  Example:

       useEffect(() => {
         const fetchHistory = async () => {
           try {
             const response = await fetch(
               "http://localhost:5000/api/history"
             );

             const data = await response.json();

             setHistoryData(data);
           } catch (error) {
             console.error(error);
           }
         };

         fetchHistory();
       }, []);

  ============================================================
  */


  /*
  ============================================================
  FILTER HISTORY
  ============================================================
  */

  const filteredHistory = useMemo(() => {

    return mockHistory.filter((item) => {

      const matchesSearch =
        item.fileName
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||

        item.documentType
          .toLowerCase()
          .includes(searchTerm.toLowerCase());


      const matchesStatus =
        statusFilter === "All" ||
        item.result === statusFilter;


      const matchesDocument =
        documentFilter === "All" ||
        item.documentType === documentFilter;


      return (
        matchesSearch &&
        matchesStatus &&
        matchesDocument
      );

    });

  }, [searchTerm, statusFilter, documentFilter]);


  /*
  ============================================================
  STATISTICS

  These currently come from mockHistory.

  BACKEND:
  These can either be calculated on frontend from the
  returned history array or returned directly by the backend.
  ============================================================
  */

  const totalAnalyses = mockHistory.length;

  const authenticCount = mockHistory.filter(
    (item) => item.result === "Authentic"
  ).length;

  const forgedCount = mockHistory.filter(
    (item) => item.result === "Forged"
  ).length;


  /*
  ============================================================
  HELPERS
  ============================================================
  */

  const formatDate = (dateString) => {

    const date = new Date(dateString);

    return date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

  };


  const formatTime = (dateString) => {

    const date = new Date(dateString);

    return date.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    });

  };


  const clearFilters = () => {

    setSearchTerm("");
    setStatusFilter("All");
    setDocumentFilter("All");

  };


  const hasActiveFilters =
    searchTerm !== "" ||
    statusFilter !== "All" ||
    documentFilter !== "All";


  /*
  ============================================================
  RENDER
  ============================================================
  */

  return (
    <div className="history-page">


      {/* =====================================================
          HEADER
      ===================================================== */}

      <section className="history-header">

        <div className="history-container">

          <div className="history-heading">

            <div className="history-badge">

              <HistoryIcon size={16} />

              <span>
                Verification History
              </span>

            </div>


            <h1>
              Analysis history
            </h1>


            <p>
              Review previous document verification analyses,
              results and confidence scores.
            </p>

          </div>

        </div>

      </section>



      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <main className="history-main">

        <div className="history-container">


          {/* =================================================
              STATISTICS
          ================================================= */}

          <div className="history-stats">


            {/* Total */}

            <div className="history-stat-card">

              <div className="history-stat-icon blue">
                <Database size={20} />
              </div>

              <div>

                <span>
                  Total Analyses
                </span>

                <strong>
                  {totalAnalyses}
                </strong>

              </div>

            </div>


            {/* Authentic */}

            <div className="history-stat-card">

              <div className="history-stat-icon green">
                <ShieldCheck size={20} />
              </div>

              <div>

                <span>
                  Authentic
                </span>

                <strong>
                  {authenticCount}
                </strong>

              </div>

            </div>


            {/* Forged */}

            <div className="history-stat-card">

              <div className="history-stat-icon red">
                <ShieldAlert size={20} />
              </div>

              <div>

                <span>
                  Potentially Forged
                </span>

                <strong>
                  {forgedCount}
                </strong>

              </div>

            </div>


            {/* Last Analysis */}

            <div className="history-stat-card">

              <div className="history-stat-icon purple">
                <Clock3 size={20} />
              </div>

              <div>

                <span>
                  Last Analysis
                </span>

                <strong>
                  {mockHistory.length > 0
                    ? formatDate(mockHistory[0].createdAt)
                    : "—"}
                </strong>

              </div>

            </div>

          </div>



          {/* =================================================
              HISTORY CARD
          ================================================= */}

          <section className="history-card">


            {/* -----------------------------------------------
                CARD HEADER
            ------------------------------------------------ */}

            <div className="history-card-header">

              <div>

                <h2>
                  Previous Analyses
                </h2>

                <p>
                  View and review your previous document checks.
                </p>

              </div>


              {/* Backend refresh placeholder */}

              <button
                type="button"
                className="refresh-button"
                title="Refresh history"
                onClick={() => {
                  /*
                  ============================================
                  BACKEND:
                  Refresh history from Node.js API here.

                  Example:

                  await fetchHistory();

                  ============================================
                  */
                }}
              >

                <RefreshCw size={17} />

                <span>
                  Refresh
                </span>

              </button>

            </div>



            {/* =================================================
                FILTER BAR
            ================================================= */}

            <div className="history-filters">


              {/* Search */}

              <div className="history-search">

                <Search size={17} />

                <input
                  type="text"
                  placeholder="Search by file name or document type..."
                  value={searchTerm}
                  onChange={(event) =>
                    setSearchTerm(event.target.value)
                  }
                />

              </div>


              {/* Status */}

              <div className="history-select-wrapper">

                <Filter size={15} />

                <select
                  value={statusFilter}
                  onChange={(event) =>
                    setStatusFilter(event.target.value)
                  }
                >

                  <option value="All">
                    All Results
                  </option>

                  <option value="Authentic">
                    Authentic
                  </option>

                  <option value="Forged">
                    Potentially Forged
                  </option>

                </select>

              </div>


              {/* Document */}

              <div className="history-select-wrapper">

                <FileText size={15} />

                <select
                  value={documentFilter}
                  onChange={(event) =>
                    setDocumentFilter(event.target.value)
                  }
                >

                  <option value="All">
                    All Documents
                  </option>

                  <option value="Aadhaar Card">
                    Aadhaar Card
                  </option>

                  <option value="Passport">
                    Passport
                  </option>

                  <option value="Other">
                    Other Documents
                  </option>

                </select>

              </div>


              {/* Clear */}

              {hasActiveFilters && (

                <button
                  type="button"
                  className="clear-filters"
                  onClick={clearFilters}
                >

                  <X size={15} />

                  Clear

                </button>

              )}

            </div>



            {/* =================================================
                DESKTOP TABLE
            ================================================= */}

            <div className="history-table-wrapper">

              {filteredHistory.length > 0 ? (

                <table className="history-table">

                  <thead>

                    <tr>

                      <th>
                        Document
                      </th>

                      <th>
                        Type
                      </th>

                      <th>
                        Result
                      </th>

                      <th>
                        Confidence
                      </th>

                      <th>
                        Date
                      </th>

                      <th>
                        Action
                      </th>

                    </tr>

                  </thead>


                  <tbody>

                    {filteredHistory.map((item) => (

                      <tr key={item.id}>


                        {/* Document */}

                        <td>

                          <div className="history-document">

                            <div className="history-document-icon">
                              <FileText size={18} />
                            </div>

                            <div>

                              <strong>
                                {item.fileName}
                              </strong>

                              <span>
                                ID: {item.id}
                              </span>

                            </div>

                          </div>

                        </td>


                        {/* Type */}

                        <td>

                          <span className="document-type-label">
                            {item.documentType}
                          </span>

                        </td>


                        {/* Result */}

                        <td>

                          <div
                            className={`history-result ${
                              item.result === "Authentic"
                                ? "authentic"
                                : "forged"
                            }`}
                          >

                            {item.result === "Authentic" ? (
                              <ShieldCheck size={16} />
                            ) : (
                              <ShieldAlert size={16} />
                            )}

                            <span>
                              {item.result === "Authentic"
                                ? "Authentic"
                                : "Potentially Forged"}
                            </span>

                          </div>

                        </td>


                        {/* Confidence */}

                        <td>

                          <div className="confidence-cell">

                            <strong>
                              {item.confidence}%
                            </strong>

                            <div className="confidence-bar">

                              <span
                                style={{
                                  width: `${item.confidence}%`,
                                }}
                              ></span>

                            </div>

                          </div>

                        </td>


                        {/* Date */}

                        <td>

                          <div className="history-date">

                            <strong>
                              {formatDate(item.createdAt)}
                            </strong>

                            <span>
                              {formatTime(item.createdAt)}
                            </span>

                          </div>

                        </td>


                        {/* Action */}

                        <td>

                          <Link
                            to="/results"
                            state={{
                              historyItem: item,
                            }}
                            className="view-result-button"
                          >

                            View Result

                            <ChevronRight size={15} />

                          </Link>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              ) : (

                <div className="history-empty-filtered">

                  <div className="empty-filter-icon">
                    <Search size={26} />
                  </div>

                  <h3>
                    No matching analyses
                  </h3>

                  <p>
                    Try changing your search or filter options.
                  </p>

                  <button
                    type="button"
                    onClick={clearFilters}
                  >
                    Clear Filters
                  </button>

                </div>

              )}

            </div>



            {/* =================================================
                MOBILE CARDS

                Same data, mobile-friendly presentation.
            ================================================= */}

            <div className="history-mobile-list">

              {filteredHistory.map((item) => (

                <div
                  className="history-mobile-card"
                  key={item.id}
                >

                  <div className="mobile-card-top">

                    <div className="history-document">

                      <div className="history-document-icon">
                        <FileText size={18} />
                      </div>

                      <div>

                        <strong>
                          {item.fileName}
                        </strong>

                        <span>
                          {item.documentType}
                        </span>

                      </div>

                    </div>


                    <div
                      className={`history-result ${
                        item.result === "Authentic"
                          ? "authentic"
                          : "forged"
                      }`}
                    >

                      {item.result === "Authentic" ? (
                        <ShieldCheck size={15} />
                      ) : (
                        <ShieldAlert size={15} />
                      )}

                      <span>
                        {item.result}
                      </span>

                    </div>

                  </div>


                  <div className="mobile-card-details">

                    <div>

                      <span>
                        Confidence
                      </span>

                      <strong>
                        {item.confidence}%
                      </strong>

                    </div>


                    <div>

                      <span>
                        Risk Score
                      </span>

                      <strong>
                        {item.riskScore}%
                      </strong>

                    </div>


                    <div>

                      <span>
                        Date
                      </span>

                      <strong>
                        {formatDate(item.createdAt)}
                      </strong>

                    </div>

                  </div>


                  <Link
                    to="/results"
                    state={{
                      historyItem: item,
                    }}
                    className="mobile-view-result"
                  >

                    View Full Analysis

                    <ChevronRight size={16} />

                  </Link>

                </div>

              ))}

            </div>



            {/* =================================================
                FOOTER NOTE
            ================================================= */}

            <div className="history-card-footer">

              <div>

                <CalendarDays size={16} />

                <span>
                  Showing {filteredHistory.length} of{" "}
                  {totalAnalyses} analyses
                </span>

              </div>


              <span>
                Results are generated by DocVerify AI
              </span>

            </div>

          </section>



          {/* =================================================
              BACKEND PLACEHOLDER
          ================================================= */}

          <div className="backend-placeholder">

            <Database size={19} />

            <div>

              <strong>
                Backend integration point
              </strong>

              <span>
                History records will be loaded from the
                Node.js API once backend integration is complete.
              </span>

            </div>

          </div>


        </div>

      </main>

    </div>
  );
}

export default History;